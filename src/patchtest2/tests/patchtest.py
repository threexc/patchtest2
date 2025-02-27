import inspect
import json
import os
import patchtest2.tests.core as core
from patchtest2.parser import PatchtestParser
from patchtest2.mbox import PatchSeries, TargetRepo


class Patchtest:
    def __init__(self, target_repo, series):
        self.target_repo = target_repo
        self.series = series
        self.core_results = {
            k: self._results(v)
            for (k, v) in inspect.getmembers(core, inspect.isfunction)
            if k != "patchtest_result"
        }

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

    def _log_results(self, logfile):
        result_str = ""
        for category in self.results.keys():
            for tag in self.results[category].keys():
                for value in self.results[category][tag]:
                    result_str += value + "\n"

        with open(logfile + ".testresult", "w") as f:
            f.write(result_str)

    def _log_json(self, logfile):
        with open(logfile + ".testresult", "w") as f:
            f.write(json.dumps(self.results, indent=4, sort_keys=True))

    def log_results(self, logfile, mode=None):
        if mode == "json":
            self._log_json(logfile)
        else:
            self._log_results(logfile)


def run():
    parser = PatchtestParser.get_parser()
    args = parser.parse_args()
    target_repo = TargetRepo(args.repodir)
    series = PatchSeries(args.patch_path)
    results = Patchtest(target_repo, series)

    results.print_results()
    if args.log_json:
        results.log_results(os.path.basename(args.patch_path), mode="json")

    if args.log_results:
        results.log_results(os.path.basename(args.patch_path))
