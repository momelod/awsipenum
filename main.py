#!/usr/bin/env python

import argparse
import ec2enum
import msg

msg = msg.msg

parser = argparse.ArgumentParser()
parser.add_argument(
    '-d', '--debug',
    default=False,
    help='enable debug',
    action=argparse.BooleanOptionalAction
)
parser.add_argument(
    '-p', '--profile',
    help='choose a single profile',
    action='store'
)
parser.add_argument(
    '-r', '--region',
    help='choose a single region',
    action='store'
)
args = parser.parse_args()


profile_list = ec2enum.profiles_check(args.profile, args.debug)
for p in profile_list:
    for r in ec2enum.regions(p, args.region, args.debug):
        ec2enum.enum_ec2(p, r, args.debug)
