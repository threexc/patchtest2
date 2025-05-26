import patchtest2.patterns as patterns
import pyparsing
import re
import unidiff
from patchtest2.results import patchtest_result

@patchtest_result
def test_mbox_commit_message_user_tags(target):
    """Test for GitHub-style username tags (@username) in commit messages"""
    result = "PASS"
    reason = "Mbox includes one or more GitHub-style username tags. Ensure that any '@' symbols are stripped out of usernames"

    if patterns.mbox_github_username.search_string(target.commit_message):
        result = "FAIL"

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
