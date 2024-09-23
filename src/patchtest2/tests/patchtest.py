from patchtest2.parser import PatchtestParser

def run():
    parser = PatchtestParser.get_parser()
    args = parser.parse_args()

    print(args)
