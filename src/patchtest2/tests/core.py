from dataclasses import dataclass

@dataclass
class PatchtestResult:
    patch: str
    testname: str
    result: str
    reason: str

def test_for_pattern(pattern, target):
    pass

