import inspect
import patchtest2.tests.core as core
from patchtest2.parser import PatchtestParser
from patchtest2.mbox import PatchSeries, TargetRepo

class Patchtest:
    def __init__(self, target_repo, series):
        self.target_repo = target_repo
        self.series = series
        self.core_results = {k: self._results(v) for (k, v) in inspect.getmembers(core, inspect.isfunction) if k != "patchtest_result"}

        self.results = dict(
            [
                (
                    "core",
                    self.core_results,
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


def run():
    parser = PatchtestParser.get_parser()
    args = parser.parse_args()
    target_repo = TargetRepo(args.repodir)
    series = PatchSeries(args.patch_path)
    results = Patchtest(target_repo, series)

    results.print_results()
