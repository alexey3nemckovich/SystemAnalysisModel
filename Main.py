import sys
from option33 import create_args_parser
from Simulator import build_model_graph


def parse_params():
    parser = create_args_parser()
    if len(sys.argv) > 1:
        args = parser.parse_args(sys.argv[1:])
        if(args.p1 < 0 or args.p1 > 1):
            print("Probability can't be more than 1 or less than 0")
            exit()
        if (args.p2 < 0 or args.p2 > 1):
            print("Probability can't be more than 1 or less than 0")
            exit()
        return args
    else:
        parser.print_help()
        exit()


if __name__ == '__main__':
    params = parse_params()
    ##res = simulate(params)
    build_model_graph(params)
