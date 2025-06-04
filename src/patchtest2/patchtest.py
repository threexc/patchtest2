import inspect
import json
import os
import sys
import importlib.util
from pathlib import Path
from patchtest2.parser import PatchtestParser
from patchtest2.mbox import PatchSeries, TargetRepo


class Patchtest:
    def __init__(self, target_repo, series, suites=None, module_paths=None):
        self.target_repo = target_repo
        self.series = series

        # Always include 'core' suite, then add any additional suites
        self.suites = ['core']
        if suites:
            # Add additional suites, avoiding duplicates
            for suite in suites:
                if suite not in self.suites:
                    self.suites.append(suite)

        # Always include src/patchtest2/tests, then add any additional paths
        self.module_paths = ['src/patchtest2/tests']
        if module_paths:
            # Add additional paths, avoiding duplicates
            for path in module_paths:
                if path not in self.module_paths:
                    self.module_paths.append(path)

        # Load all test modules and their functions
        self.results = {}
        self._load_test_modules()

    def _load_test_modules(self):
        """Load test functions from all specified suites and module paths"""
        for suite_name in self.suites:
            suite_results = {}

            # Look for the suite module in all specified paths
            module_found = False
            for module_path in self.module_paths:
                module_file = Path(module_path) / f"{suite_name}.py"

                if module_file.exists():
                    module_found = True
                    # Load the module dynamically
                    spec = importlib.util.spec_from_file_location(
                        f"patchtest2.tests.{suite_name}",
                        module_file
                    )
                    module = importlib.util.module_from_spec(spec)

                    # Add to sys.modules to handle imports within the module
                    sys.modules[f"patchtest2.tests.{suite_name}"] = module
                    spec.loader.exec_module(module)

                    # Extract test functions from the module
                    test_functions = {
                        k: v for (k, v) in inspect.getmembers(module, inspect.isfunction)
                        if k != "patchtest_result" and k.startswith("test_")
                    }

                    # Run tests and collect results
                    for func_name, func in test_functions.items():
                        suite_results[func_name] = self._results(func)

                    break  # Found the module, no need to check other paths

            if not module_found:
                print(f"Warning: Suite '{suite_name}' not found in any of the specified module paths")
                continue

            self.results[suite_name] = suite_results

    def _results(self, testname):
        """Run a test function against all patches in the series"""
        return [testname(patch) for patch in self.series.patchdata]

    def _print_result(self, category, tag):
        """Print results for a specific test function"""
        for value in self.results[category][tag]:
            print(value)

    def _print_results(self, category):
        """Print all results for a specific suite"""
        for tag in self.results[category].keys():
            self._print_result(category, tag)

    def print_results(self):
        """Print all results from all suites"""
        for category in self.results.keys():
            self._print_results(category)

    def _log_results(self, logfile):
        """Log results to a text file"""
        result_str = ""
        for category in self.results.keys():
            for tag in self.results[category].keys():
                for value in self.results[category][tag]:
                    result_str += value + "\n"
        with open(logfile + ".testresult", "w") as f:
            f.write(result_str)

    def _log_json(self, logfile):
        """Log results to a JSON file"""
        with open(logfile + ".testresult", "w") as f:
            f.write(json.dumps(self.results, indent=4, sort_keys=True))

    def log_results(self, logfile, mode=None):
        """Log results in specified format"""
        if mode == "json":
            self._log_json(logfile)
        else:
            self._log_results(logfile)


def run():
    """Main entry point for patchtest"""
    parser = PatchtestParser.get_parser()
    args = parser.parse_args()

    # Parse suites argument
    suites = None
    if hasattr(args, 'suites') and args.suites:
        suites = [suite.strip() for suite in args.suites.split(',')]

    # Parse module paths argument
    module_paths = None
    if hasattr(args, 'module_paths') and args.module_paths:
        module_paths = args.module_paths

    target_repo = TargetRepo(args.repodir)
    series = PatchSeries(args.patch_path)
    results = Patchtest(target_repo, series, suites=suites, module_paths=module_paths)

    results.print_results()

    if args.log_json:
        results.log_results(os.path.basename(args.patch_path), mode="json")
    if args.log_results:
        results.log_results(os.path.basename(args.patch_path))
