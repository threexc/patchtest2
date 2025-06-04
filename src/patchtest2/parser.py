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

default_testdir = os.path.abspath(os.path.dirname(__file__) + "/suites")
default_repodir = os.path.abspath(os.path.dirname(__file__) + "/../../..")


class PatchtestParser(object):
    """Abstract the patchtest argument parser"""

    @classmethod
    def get_parser(cls):
        parser = argparse.ArgumentParser()

        target_patch_group = parser.add_mutually_exclusive_group(required=True)
        log_type_group = parser.add_mutually_exclusive_group(required=False)

        target_patch_group.add_argument(
            "--patch",
            action="store",
            metavar="PATCH",
            dest="patch_path",
            help="The patch to be tested",
        )

        target_patch_group.add_argument(
            "--directory",
            action="store",
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

        # Add --suites/-s argument for comma-separated list of suite names
        parser.add_argument(
            "--suites",
            "-s",
            type=str,
            help="Comma-separated list of test suite module names to run (core suite is always included)",
        )

        # Add --module-path/-m argument that can be specified multiple times
        parser.add_argument(
            "--module-path",
            "-m",
            dest="module_paths",
            action="append",
            help="Path to search for test modules (src/patchtest2/suites is always included; can be specified multiple times)",
        )

        log_type_group.add_argument(
            "--log-results",
            dest="log_results",
            action="store_true",
            help='Enable logging to a file matching the target patch name with ".testresult" appended',
        )

        log_type_group.add_argument(
            "--log-json",
            dest="log_json",
            action="store_true",
            help='Enable logging to a file matching the target patch name with ".testresult" appended, in json format',
        )

        return parser
