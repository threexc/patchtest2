import re

import pyparsing
import unidiff

import patchtest2.patterns as patterns  # type: ignore[import-untyped]
from patchtest2.results import patchtest_result
from patchtest2.mbox import Patch
from typing import Tuple


@patchtest_result
def test_mbox_has_signed_off_by(target: Patch) -> Tuple[str, str, str]:
    result = "FAIL"
    if patterns.signed_off_by.search_string(target.commit_message):
        result = "PASS"
    reason = "mbox was missing a signed-off-by tag"
    return target.subject, result, reason


@patchtest_result
def test_mbox_shortlog_format(target: Patch) -> Tuple[str, str, str]:
    result = "PASS"
    reason = None
    if not target.shortlog.strip():
        result = "SKIP"
        reason = "mbox shortlog was empty, no test needed"

    if target.shortlog.startswith('Revert "'):
        result = "SKIP"
        reason = "No need to test a revert patch"

    try:
        patterns.shortlog.parse_string(target.shortlog, parse_all=True)
    except pyparsing.ParseException as pe:
        result = "FAIL"
        reason = 'Commit shortlog (first line of commit message) should follow the format "<target>: <summary>"'

    return target.subject, result, reason


@patchtest_result
def test_mbox_shortlog_length(target: Patch) -> Tuple[str, str, str]:
    shortlog = re.sub("^(\[.*?\])+ ", "", target.shortlog)
    shortlog_len = len(shortlog)
    result = "PASS"
    reason = f"Edit shortlog so that it is {patterns.mbox_shortlog_maxlength} characters or less (currently {shortlog_len} characters)"

    if shortlog.startswith('Revert "'):
        result = "SKIP"
        reason = "No need to test revert patches"
    else:
        if shortlog_len > patterns.mbox_shortlog_maxlength:
            result = "FAIL"

    return target.subject, result, reason


@patchtest_result
def test_mbox_has_commit_message(target: Patch) -> Tuple[str, str, str]:
    result = "PASS"
    reason = "Please include a commit message on your patch explaining the change"

    # Get all lines that aren't Signed-off-by
    commit_lines = [
        line.strip()
        for line in target.commit_message.splitlines()
        if line.strip() and not line.strip().startswith("Signed-off-by:")
    ]

    # If we have any remaining lines, there's a commit message
    if not commit_lines:
        result = "FAIL"

    return target.subject, result, reason


@patchtest_result
def test_mbox_unidiff_parse_error(target: Patch) -> Tuple[str, str, str]:
    result = "PASS"
    reason = f'Patch "{target.shortlog}" contains malformed diff lines.'

    try:
        diff = unidiff.PatchSet.from_string(target.data.as_string())
    except unidiff.UnidiffParseError as upe:
        result = "FAIL"

    return target.subject, result, reason


@patchtest_result
def test_mbox_revert_signed_off_by_exception(target: Patch) -> Tuple[str, str, str]:
    """Skip signed-off-by test for revert commits"""
    result = "PASS"
    reason = None

    # This is a special case that modifies the signed-off-by test behavior
    # In the original, revert commits skip the signed-off-by requirement
    if patterns.mbox_revert_shortlog_regex.search_string(target.shortlog):
        result = "SKIP"
        reason = "Revert commits do not require Signed-off-by tags"
    elif not patterns.signed_off_by.search_string(target.commit_message):
        result = "FAIL"
        reason = 'Mbox is missing Signed-off-by. Add it manually or with "git commit --amend -s"'

    return target.subject, result, reason


# Additional helper test that might be useful
@patchtest_result
def test_mbox_shortlog_revert_format(target: Patch) -> Tuple[str, str, str]:
    """Test revert commit shortlog format"""
    result = "PASS"
    reason = None

    if target.shortlog.startswith('Revert "'):
        # Could add specific revert format validation here if needed
        if not target.shortlog.endswith('"'):
            result = "FAIL"
            reason = (
                'Revert commit shortlog should be in format: Revert "original shortlog"'
            )
    else:
        result = "SKIP"
        reason = "Not a revert commit"

    return target.subject, result, reason
