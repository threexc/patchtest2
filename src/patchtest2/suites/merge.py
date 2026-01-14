#! /usr/bin/env python3

# merge.py
#
# Test suite for testing patch mergeability against target repository
#
# Copyright (C) Trevor Gamblin <tgamblin@baylibre.com>
#
# SPDX-License-Identifier: GPL-2.0-only
#

import os
import tempfile
import git
from patchtest2.mbox import TargetRepo
from patchtest2.results import patchtest_result


@patchtest_result
def test_patch_can_merge(target):
    """Test if a patch can be merged on top of the target repository's current branch"""
    # Get the target repository from the global context
    # This will be set by the Patchtest class when running merge tests
    target_repo = getattr(test_patch_can_merge, "_target_repo", None)
    result = "PASS"
    reason = "No target repository provided for merge testing"

    if target_repo is None:
        result = "FAIL"
        return target.subject, result, reason

    # Create a temporary file for the patch
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".patch", delete=False
    ) as temp_patch:
        # Write the patch data to the temporary file
        # We need to reconstruct the full patch from the email message
        patch_content = str(target.data)
        temp_patch.write(patch_content)
        temp_patch.flush()

        try:
            # Get the current branch name to use as target
            current_branch = target_repo.repo.active_branch.name

            # Create and checkout working branch
            target_repo.checkout_working_branch(current_branch)

            # Test if the patch can be merged
            merge_result = target_repo.can_be_merged(temp_patch.name)

            # Clean up the working branch
            target_repo.cleanup()

            if merge_result is not True:
                # merge_result contains the GitCommandError
                result = "FAIL"
                reason = f"Patch '{target.shortlog}' failed to merge: {merge_result}"
                return target.subject, result, reason

        except Exception as e:
            # Ensure cleanup happens even if there's an unexpected error
            try:
                target_repo.cleanup()
            except:
                pass
            result = "FAIL"
            reason = f"Error testing merge: {str(e)}"
            return target.subject, result, reason

        finally:
            # Clean up the temporary patch file
            try:
                os.unlink(temp_patch.name)
            except:
                pass
