import patchtest2.patterns as patterns

class PatchtestResult:
    def __init__(self, patch, testname, result):
        self.patch = patch
        self.testname = testname
        self.result = result

    def __str__(self):
        return f"{self.result}: {self.testname} on {self.patch}"

class PatchtestFail(PatchtestResult):
    def __init__(self, patch, testname, result, reason):
        super().__init__(patch, testname, result)
        self.reason = reason

    def __str__(self):
        return f"{self.result}: {self.testname} on {self.patch} ({self.reason})"

class PatchtestResults:
    def __init__(self, target_repo, series):
        self.target_repo = target_repo
        self.series = series
        self.mbox_signed_off_by_results = [test_mbox_signed_off_by_presence(patch) for patch in self.series.patchdata]

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
    result = test_for_pattern(patterns.signed_off_by,
                              target.commit_message)
    if result == "PASS":
        return PatchtestResult(target.subject, "mbox_signed_off_by_presence", result)
    elif result == "FAIL":
        return PatchtestFail(target.subject, "mbox_signed_off_by_presence", result, "mbox was missing a signed-off-by tag")
