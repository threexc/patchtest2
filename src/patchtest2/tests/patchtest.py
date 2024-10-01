from patchtest2.parser import PatchtestParser
from patchtest2.mbox import PatchSeries, TargetRepo
from patchtest2.tests.core import PatchtestResults

def run():
    parser = PatchtestParser.get_parser()
    args = parser.parse_args()
    target_repo = TargetRepo(args.repodir)
    series = PatchSeries(args.patch_path)
    results = PatchtestResults(target_repo, series)
    for testresult in results.mbox_signed_off_by_results:
        print(testresult)
