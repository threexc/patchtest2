import patchtest2.patterns as patterns
import pyparsing
import re
import unidiff
from patchtest2.tests.results import patchtest_result

@patchtest_result
def test_mbox_has_signed_off_by(target):
    result = "FAIL"
    if patterns.signed_off_by.search_string(target.commit_message):
        result = "PASS"
    reason = "mbox was missing a signed-off-by tag"
    return target.subject, result, reason

@patchtest_result
def test_mbox_shortlog_format(target):
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
def test_mbox_shortlog_length(target):
    shortlog = re.sub("^(\[.*?\])+ ", "", target.shortlog)
    shortlog_len = len(shortlog)
    result = "PASS"
    reason = f"Edit shortlog so that it is {patterns.mbox_shortlog_maxlength} characters or less (currently {shortlog_len} characters)"

    print(target.shortlog)
    if shortlog.startswith('Revert "'):
        result = "SKIP"
        reason = "No need to test revert patches"
    else:
        if shortlog_len > patterns.mbox_shortlog_maxlength:
            result = "FAIL"

    return target.subject, result, reason

@patchtest_result
def test_mbox_has_commit_message(target):
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
def test_mbox_unidiff_parse_error(target):
    result = "PASS"
    reason = f'Patch "{target.shortlog}" contains malformed diff lines.'

    try:
        diff = unidiff.PatchSet.from_string(target.data.as_string())
    except unidiff.UnidiffParseError as upe:
        result = "FAIL"

    return target.subject, result, reason
