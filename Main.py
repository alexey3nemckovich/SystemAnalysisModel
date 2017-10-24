import argparse
import sys
from Simulator import simulate
from Simulator import build_model_graph


def create_args_parser():
    parser = argparse.ArgumentParser(
        description='System simulator'
    )
    required_args = parser.add_argument_group('required named arguments')
    required_args.add_argument('--c', type=int, help='Count tacts before source gives new request', required=True)
    required_args.add_argument('--p1', type=float, help='Probability that request will not be processed by first channel', required=True)
    required_args.add_argument('--p2', type=float, help='Probability that request will not be processed by second channel', required=True)
    required_args.add_argument('--n', type=int, help='Count tacts to simulate', required=True)
    return parser


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
