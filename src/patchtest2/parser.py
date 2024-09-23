# ex:ts=4:sw=4:sts=4:et
# -*- tab-width: 4; c-basic-offset: 4; indent-tabs-mode: nil -*-
#
# parser: implementation of a patchtest-specific parser
#
# Copyright (C) 2024 Trevor Gamblin <tgamblin@baylibre.com>
#
# SPDX-License-Identifier: GPL-2.0-only
#

import os
import argparse

default_testdir = os.path.abspath(os.path.dirname(__file__) + "/tests")
default_repodir = os.path.abspath(os.path.dirname(__file__) + "/../../..")


class PatchtestParser(object):
    """Abstract the patchtest argument parser"""

    @classmethod
    def get_parser(cls):
        parser = argparse.ArgumentParser()

        target_patch_group = parser.add_mutually_exclusive_group(required=True)

        target_patch_group.add_argument(
            "--patch", metavar="PATCH", dest="patch_path", help="The patch to be tested"
        )

        target_patch_group.add_argument(
            "--directory",
            metavar="DIRECTORY",
            dest="patch_path",
            help="The directory containing patches to be tested",
        )

        parser.add_argument(
            "--repodir",
            metavar="REPO",
            default=default_repodir,
            help="Name of the repository where patch is merged",
        )

        parser.add_argument(
            "--testdir",
            metavar="TESTDIR",
            default=default_testdir,
            help="Directory where test cases are located",
        )

        parser.add_argument(
            "--target-branch",
            "-b",
            dest="target_branch",
            help="Branch name used by patchtest to branch from. If not provided, it uses the current one.",
        )

        parser.add_argument(
            "--debug", "-d", action="store_true", help="Enable debug output"
        )

        parser.add_argument(
            "--log-results",
            action="store_true",
            help='Enable logging to a file matching the target patch name with ".testresult" appended',
        )

        return parser
