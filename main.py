#!/usr/bin/env python

import argparse
import botocore
import boto3

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


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def msg(stat, msg):
    if args.debug:
        if stat == "hdr":
            print('%s%s%s' % (f"{bcolors.HEADER}", msg, f"{bcolors.ENDC}"))
        if stat == "ok":
            print('%s%s%s' % (f"{bcolors.OKGREEN}", msg, f"{bcolors.ENDC}"))
        if stat == "ko":
            print('%s%s%s' % (f"{bcolors.OKBLUE}", msg, f"{bcolors.ENDC}"))
        if stat == "warn":
            print('%s%s%s' % (f"{bcolors.WARNING}", msg, f"{bcolors.ENDC}"))
        if stat == "info":
            print(f"{bcolors.ENDC}" + msg, end='')

    if stat == "fatal":
        print(f"{bcolors.FAIL}" + msg + f"{bcolors.ENDC}")


def profiles_check():
    msg("info", "\n")
    msg("hdr", "Validating profiles ..")
    profiles_list = []

    if args.profile:
        profiles_available = [args.profile]
    else:
        profiles_available = boto3.session.Session().available_profiles

    for p in profiles_available:
        msg("info", "[" + p + "]: ")
        session = boto3.session.Session(profile_name=p)
        sts = session.client(
            service_name='sts'
        )
        try:
            profile = sts.get_caller_identity()
            msg("ok", "Profile Validated")
        except botocore.exceptions.ClientError:
            profile = False
            msg("warn", "ClientError")
        except botocore.exceptions.ConfigParseError:
            profile = False
            msg("warn", "ConfigParseError")
        except botocore.exceptions.ConnectTimeoutError:
            profile = False
            msg("warn", "ConnectTimeoutError")
        except botocore.exceptions.CredentialRetrievalError:
            profile = False
            msg("warn", "CredentialRetrievalError")
        except botocore.exceptions.NoCredentialsError:
            profile = False
            msg("warn", "NoCredentialsError")

        msg("info", "")
        if profile:
            profiles_list.append(p)

    if not profiles_list:
        msg("fatal", "No working profiles found")
        return False
    else:
        return profiles_list


def regions(p):
    msg("info", "\n")
    msg("hdr", "Validating region access ..")
    list = []
    region_enabled = []

    if args.region:
        list = [args.region]
    else:
        session = boto3.session.Session(profile_name=p)
        ec2 = session.client('ec2')
        regions = ec2.describe_regions()

        for r in regions['Regions']:
            list.append(r['RegionName'])

    for r in list:
        msg("info", "[" + p + "]" + "[" + r + "]: ")
        sts = session.client('sts', region_name=r)
        try:
            check = sts.get_caller_identity()
        except botocore.exceptions.ClientError:
            check = False

        if check:
            msg("ok", "Region Enabled")
            region_enabled.append(r)
        else:
            msg("warn", "RegionDisabledException")

        msg("info", "")

    return region_enabled


def enum_ec2(p, r):
    session = boto3.session.Session(profile_name=p, region_name=r)
    ec2 = session.client('ec2')
    count = 0
    msg("info", "\n")
    msg("info", "[" + p + "]" + "[" + r + "]: ")
    try:
        result = ec2.describe_instances()
    except botocore.errorfactory.ClientError:
        result = False

    if result:
        msg("hdr", "Enermerating Public IPs ..")
        for reservation in result['Reservations']:
            for instance in reservation['Instances']:
                if instance.get(u'PublicIpAddress') is not None:
                    count += 1
                    id = instance['InstanceId']
                    ip = instance['PublicIpAddress']
                    vpc = instance['VpcId']
                    tags = instance['Tags']

                    for t in tags:
                        if t['Key'] == 'Name':
                            name = t['Value']

                    finding = vpc + " " + name + " " + id + " "
                    msg("info", finding)
                    print(ip)
    else:
        msg("warn", "RegionDisabledException")

    msg("ko", "Found: " + str(count))


def main():

    profile_list = profiles_check()
    for p in profile_list:
        for r in regions(p):
            enum_ec2(p, r)


main()
