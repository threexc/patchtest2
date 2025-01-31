from patchtest2.parser import PatchtestParser
from patchtest2.mbox import PatchSeries, TargetRepo
from patchtest2.tests.core import PatchtestResults


def run():
    parser = PatchtestParser.get_parser()
    args = parser.parse_args()
    target_repo = TargetRepo(args.repodir)
    series = PatchSeries(args.patch_path)
    results = PatchtestResults(target_repo, series)

    results.print_mbox_results("signed_off_by")
    results.print_mbox_results("shortlog_format")
    results.print_mbox_results("commit_message_presence")
