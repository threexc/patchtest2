# repo: tools for interacting with a git repo from patchtest
#
# SPDX-License-Identifier: GPL-2.0-only
#
# Based on https://git.yoctoproject.org/poky/tree/meta/lib/patchtest/repo.py

import git
import os
from patchtest2 import mbox


class Repo:
    def __init__(self, patch, repodir, commit=None, branch=None):
        self.repodir = repodir
        self.repo = git.Repo.init(repodir)
        self.patch = mbox.PatchSeries(patch)
        self.current_branch = self.repo.active_branch.name

        self.prefix = "patchtest"
        # generate a workingbranch based on the current PID
        # TODO: Make this more unique via a timestamp or something
        self._workingbranch = f"{self.prefix}_{os.getpid()}"
        self.valid_patch_branch = None
        # prefix used for temporal branches/stashes
        self._patchmerged = False
        self._patchcanbemerged = False
        self._commit = None

        # targeted branch defined on the patch may be invalid, so make sure there
        # is a corresponding remote branch
        if self.patch.branch in self.repo.branches:
            self.valid_patch_branch = self.patch.branch

        # Target Commit
        # Priority (top has highest priority):
        #    1. commit given at cmd line
        #    2. branch given at cmd line
        #    3. branch given at the patch
        #    3. current HEAD
        self._commit = (
            self._get_commitid(commit)
            or self._get_commitid(branch)
            or self._get_commitid(self.valid_patch_branch)
            or self._get_commitid("HEAD")
        )

        # create working branch. Use the '-B' flag so that we just
        # check out the existing one if it's there
        self.repo.git.execute(
            ["git", "checkout", "-B", self._workingbranch, self._commit]
        )

        # Check if patch can be merged using git-am
        try:
            # Make sure to get the absolute path of the file
            self.repo.git.execute(
                ["git", "apply", "--check", os.path.abspath(self.patch.path)],
                with_exceptions=True,
            )
            self._patchcanbemerged = True
        except git.exc.GitCommandError as ce:
            pass

    def ismerged(self):
        return self._patchmerged

    def canbemerged(self):
        return self._patchcanbemerged

    def _get_commitid(self, commit):

        if not commit:
            return None

        try:
            return self.repo.rev_parse(commit).hexsha
        except Exception as e:
            print(f"Couldn't find commit {commit} in repo")

        return None

    def merge(self):
        if self._patchcanbemerged:
            self.repo.git.execute(
                ["git", "am", "--keep-cr", os.path.abspath(self.patch.path)]
            )
            self._patchmerged = True

    def clean(self):
        self.repo.git.execute(["git", "checkout", self.current_branch])
        self.repo.git.execute(["git", "branch", "-D", self._workingbranch])
        self._patchmerged = False
