from argparse import ArgumentParser, BooleanOptionalAction
from awsipenum import sts, ec2


def create_parser():
    parser = ArgumentParser()
    parser.add_argument(
        '-d', '--debug',
        default=False,
        help='enable debug',
        action=BooleanOptionalAction
    )
    parser.add_argument(
        '-p', '--profile',
        default=False,
        help='choose a single profile'
    )
    parser.add_argument(
        '-r', '--region',
        default=False,
        help='choose a single region'
    )
    return parser


def main():

    args = create_parser().parse_args()
    sts.debug = args.debug
    ec2.debug = args.debug

    profile_list = sts.profiles_check(args.profile)
    for p in profile_list:
        for r in ec2.regions(p, args.region):
            ec2.ips(p, r)
