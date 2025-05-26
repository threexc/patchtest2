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

@patchtest_result
def test_mbox_commit_message_user_tags(target):
    """Test for GitHub-style username tags (@username) in commit messages"""
    result = "PASS"
    reason = "Mbox includes one or more GitHub-style username tags. Ensure that any '@' symbols are stripped out of usernames"

    if patterns.mbox_github_username.search_string(target.commit_message):
        result = "FAIL"

    return target.subject, result, reason

@patchtest_result
def test_mbox_bugzilla_entry_format(target):
    """Test for proper Bugzilla entry format in commit messages"""
    result = "PASS"
    reason = None

    # Check if there's any bugzilla reference
    if not patterns.mbox_bugzilla.search_string(target.commit_message):
        result = "SKIP"
        reason = "No bug ID found"
    elif not patterns.mbox_bugzilla_validation.search_string(target.commit_message):
        result = "FAIL"
        reason = 'Bugzilla issue ID is not correctly formatted - specify it with format: "[YOCTO #<bugzilla ID>]"'

    return target.subject, result, reason

@patchtest_result
def test_mbox_author_valid(target):
    """Test for valid patch author"""
    result = "PASS"
    reason = f'Invalid author {target.author}. Resend the series with a valid patch author'

    for invalid in patterns.invalid_submitters:
        if invalid.search_string(target.author):
            result = "FAIL"
            break

    return target.subject, result, reason

@patchtest_result
def test_mbox_non_auh_upgrade(target):
    """Test that patch is not from AUH (Auto Upgrade Helper)"""
    result = "PASS"
    reason = f"Invalid author {patterns.auh_email}. Resend the series with a valid patch author"

    if patterns.auh_email in target.commit_message:
        result = "FAIL"

    return target.subject, result, reason

@patchtest_result
def test_mbox_target_mailing_list_meta_project(target):
    """Check for meta-* project tags in subject line"""
    result = "PASS"
    reason = "Series sent to the wrong mailing list or some patches from the series correspond to different mailing lists"

    # Check for meta-* project indicators in subject
    project_regex = pyparsing.Regex(r"\[(?P<project>meta-.+)\]")
    if project_regex.search_string(target.subject):
        result = "FAIL"

    return target.subject, result, reason

@patchtest_result
def test_mbox_revert_signed_off_by_exception(target):
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
def test_mbox_shortlog_revert_format(target):
    """Test revert commit shortlog format"""
    result = "PASS"
    reason = None

    if target.shortlog.startswith('Revert "'):
        # Could add specific revert format validation here if needed
        if not target.shortlog.endswith('"'):
            result = "FAIL"
            reason = 'Revert commit shortlog should be in format: Revert "original shortlog"'
    else:
        result = "SKIP"
        reason = "Not a revert commit"

    return target.subject, result, reason
