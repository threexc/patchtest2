#! /usr/bin/env python3

# mbox.py
#
# Classes for representing mboxes, parsed patches and patch series, and
# the repositories they target
#
# Copyright (C) Trevor Gamblin <tgamblin@baylibre.com>
#
# SPDX-License-Identifier: MIT
#

import email
import os
import re
from dataclasses import dataclass
from email.message import Message
from typing import List, Optional, Iterator, Any

import git


# From: https://stackoverflow.com/questions/59681461/read-a-big-mbox-file-with-python
class MboxReader:
    def __init__(self, filepath: str) -> None:
        self.handle = open(filepath, "rb")
        assert self.handle.readline().startswith(b"From ")

    def __enter__(self) -> "MboxReader":
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, exc_traceback: Any) -> None:
        self.handle.close()

    def __iter__(self) -> Iterator[Message]:
        return iter(self.__next__())

    def __next__(self) -> Iterator[Message]:
        lines: List[bytes] = []
        while True:
            line = self.handle.readline()
            if line == b"" or line.startswith(b"From "):
                yield email.message_from_bytes(b"".join(lines))
                if line == b"":
                    break
                lines = []
                continue
            lines.append(line)


class Patch:
    def __init__(self, data: Message) -> None:
        self.data = data
        self.author: str = data["From"] or ""
        self.to: str = data["To"] or ""
        self.cc: str = data["Cc"] or ""
        self.subject: str = data["Subject"] or ""
        payload = data.get_payload()
        # Handle payload that might be a list or string
        if isinstance(payload, list):
            payload_str = str(payload[0]) if payload else ""
        else:
            payload_str = str(payload)
        self.split_body: List[str] = re.split("---", payload_str, maxsplit=1)
        self.commit_message: str = self.split_body[0]
        self.diff: str = self.split_body[1] if len(self.split_body) > 1 else ""
        # get the shortlog, but make sure to exclude bracketed prefixes
        # before the colon, and remove extra whitespace/newlines
        self.shortlog: str = (
            self.subject[self.subject.find("]", 0, self.subject.find(":")) + 1 :]
            .replace("\n", "")
            .strip()
        )


class PatchSeries:
    def __init__(self, filepath: str) -> None:
        with MboxReader(filepath) as mbox:
            # Keep raw copies of messages in a list
            self.messages: List[Message] = [message for message in mbox]
            # Get a copy of each message's core patch contents
            self.patchdata: List[Patch] = [Patch(message) for message in self.messages]

        assert self.patchdata
        self.patch_count: int = len(self.patchdata)
        self.path: str = filepath
        self.branch: str = self.get_branch()

    def get_branch(self) -> str:
        fullprefix = ""
        pattern = re.compile(r"(\[.*\])", re.DOTALL)

        # There should be at least one patch in the series and it should
        # include the branch name in the subject, so parse that
        match = pattern.search(self.patchdata[0].subject)
        if match:
            fullprefix = match.group(1)

        branch, branches, valid_branches = None, [], []

        if fullprefix:
            prefix = fullprefix.strip("[]")
            branches = [b.strip() for b in prefix.split(",")]
            valid_branches = [b for b in branches if PatchSeries.valid_branch(b)]

        if len(valid_branches):
            branch = valid_branches[0]

        # Get the branch name excluding any brackets. If nothing was
        # found, then assume there was no branch tag in the subject line
        # and that the patch targets master
        if branch is not None:
            return branch.split("]")[0]
        else:
            return "master"

    @staticmethod
    def valid_branch(branch: str) -> bool:
        """Check if branch is valid name"""
        lbranch = branch.lower()

        invalid = (
            lbranch.startswith("patch")
            or lbranch.startswith("rfc")
            or lbranch.startswith("resend")
            or re.search(r"^v\d+", lbranch)
            or re.search(r"^\d+/\d+", lbranch)
        )

        return not invalid


class TargetRepo:
    def __init__(self, repodir: str) -> None:
        self.repodir: str = repodir
        self.repo: git.Repo = git.Repo.init(repodir)
        self.start_branch: str = self.repo.active_branch.name
        self.working_branch: str = f"patchtest_{os.getpid()}"

    def checkout_working_branch(self, target_branch: str) -> None:
        # create working branch. Use the '-B' flag so that we just
        # check out the existing one if it's there
        self.repo.git.execute(
            ["git", "checkout", "-B", self.working_branch, target_branch]
        )

    def can_be_merged(self, patchfile: str) -> bool:
        # We don't actually want to propagate the error if the patch
        # can't merge, so put a try-except around it. However, if the
        # check fails, return False
        try:
            self.merge_patch(patchfile)
            return True
        except git.exc.GitCommandError:
            self.abort_merge()
            return False

    def merge_patch(self, patchfile: str) -> None:
        self.repo.git.execute(
            ["git", "am", "--keep-cr", os.path.abspath(patchfile)], with_exceptions=True
        )

    def abort_merge(self) -> None:
        self.repo.git.execute(["git", "am", "--abort"])

    def cleanup(self) -> None:
        self.repo.git.execute(["git", "checkout", self.start_branch])
        self.repo.git.execute(["git", "branch", "-D", self.working_branch])
