import patchtest2.patterns as patterns
import pyparsing
import re
import unidiff


class PatchtestResult:
    def __init__(self, patch, testname, result, reason):
        self.patch = patch
        self.testname = testname
        self.result = result
        self.reason = reason
        self.pass_string = f"{self.result}: {self.testname} on {self.patch}"
        self.skip_or_fail_string = (
            f"{self.result}: {self.testname} on {self.patch} ({self.reason})"
        )

    def __str__(self):
        if self.result == "PASS":
            return self.pass_string
        else:
            return self.skip_or_fail_string


class PatchtestResults:
    def __init__(self, target_repo, series):
        self.target_repo = target_repo
        self.series = series
        self.mbox_results = dict(
            [
                (
                    "signed_off_by",
                    self._results(test_mbox_has_signed_off_by),
                ),
                (
                    "shortlog_format",
                    self._results(test_mbox_shortlog_format),
                ),
                (
                    "has_commit_message",
                    self._results(test_mbox_has_commit_message),
                ),
                (
                    "diff_parse",
                    self._results(test_mbox_unidiff_parse_error),
                ),
            ]
        )

        self.results = dict(
            [
                (
                    "mbox",
                    self.mbox_results,
                ),
            ]
        )

    def _results(self, testname):
        return [testname(patch) for patch in self.series.patchdata]

    def _print_result(self, category, tag):
        for value in self.results[category][tag]:
            print(value)

    def _print_results(self, category):
        for tag in self.results[category].keys():
            self._print_result(category, tag)

    def print_results(self):
        for category in self.results.keys():
            self._print_results(category)


# test_for_pattern()
# @pattern: a pyparsing regex object
# @string: a string (patch subject, commit message, author, etc. to
# search for
def test_for_pattern(pattern, string):
    if pattern.search_string(string):
        return "PASS"
    else:
        return "FAIL"


def test_mbox_has_signed_off_by(target):
    test_name = "test_mbox_has_signed_off_by"
    result = test_for_pattern(patterns.signed_off_by, target.commit_message)
    reason = "mbox was missing a signed-off-by tag"
    return PatchtestResult(target.subject, test_name, result, reason)


def test_mbox_shortlog_format(target):
    test_name = "test_mbox_shortlog_format"
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

    return PatchtestResult(target.subject, test_name, result, reason)


def test_mbox_has_commit_message(target):
    test_name = "test_mbox_has_commit_message"
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

    return PatchtestResult(target.subject, test_name, result, reason)

def test_mbox_unidiff_parse_error(target):
    test_name = "test_mbox_unidiff_parse_error"
    result = "PASS"
    reason = f"Patch \"{target.shortlog}\" contains malformed diff lines."

    try:
        diff = unidiff.PatchSet.from_string(target.data.as_string())
    except unidiff.UnidiffParseError as upe:
        result = "FAIL"

    return PatchtestResult(target.subject, test_name, result, reason)
