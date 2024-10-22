import patchtest2.patterns as patterns
import pyparsing

class PatchtestResult:
    def __init__(self, patch, testname, result, reason):
        self.patch = patch
        self.testname = testname
        self.result = result
        self.reason = reason
        self.pass_string = f"{self.result}: {self.testname} on {self.patch}"
        self.skip_or_fail_string = f"{self.result}: {self.testname} on {self.patch} ({self.reason})"

    def __str__(self):
        if self.result == "PASS":
            return self.pass_string
        else:
            return self.skip_or_fail_string

class PatchtestResults:
    def __init__(self, target_repo, series):
        self.target_repo = target_repo
        self.series = series
        self.mbox_signed_off_by_results = [test_mbox_signed_off_by_presence(patch) for patch in self.series.patchdata]
        self.mbox_shortlog_format_results = [test_mbox_shortlog_format(patch) for patch in self.series.patchdata]

# test_for_pattern()
# @pattern: a pyparsing regex object
# @string: a string (patch subject, commit message, author, etc. to
# search for
def test_for_pattern(pattern, string):
    if pattern.search_string(string):
        return "PASS"
    else:
        return "FAIL"

def test_mbox_signed_off_by_presence(target):
    test_name = "test_mbox_signed_off_by_presence"
    result = test_for_pattern(patterns.signed_off_by,
                              target.commit_message)
    reason = "mbox was missing a signed-off-by tag"
    return PatchtestResult(target.subject,
                           test_name,
                           result,
                           reason)

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

    return PatchtestResult(target.subject,
                           test_name,
                           result,
                           reason)
