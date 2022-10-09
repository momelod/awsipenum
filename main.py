#!/usr/bin/env python

import argparse
import botocore
import boto3
import json

parser = argparse.ArgumentParser()
parser.add_argument(
    '-d', '--debug',
    default=False,
    help='enable debug',
    action=argparse.BooleanOptionalAction
)
parser.add_argument(
    '-p', '--profile',
    help='manually choose a profile',
    action='store'
)
args = parser.parse_args()


def msg(stat, msg):
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

    if args.debug:
        if stat == "ok":
            print(f"{bcolors.OKGREEN}" + msg + f"{bcolors.ENDC}")
        if stat == "warn":
            print(f"{bcolors.WARNING}" + msg + f"{bcolors.ENDC}")
        if stat == "info":
            print(f"{bcolors.ENDC}" + msg, end='')

    if stat == "fatal":
        print(f"{bcolors.FAIL}" + msg + f"{bcolors.ENDC}")


def profiles_check():
    profiles_list = []

    if args.profile:
        profiles_available = [args.profile]
    else:
        profiles_available = boto3.session.Session().available_profiles

    for p in profiles_available:
        msg("info", "[" + p + "]: ")
        session = boto3.session.Session(profile_name=p)
        client = session.client(
            service_name='sts'
        )
        try:
            profile = client.get_caller_identity()
            msg("ok", "Validated")
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


for p in profiles_check():
    session = boto3.session.Session(profile_name=p)
    ec2 = session.client('ec2')
    result = ec2.describe_regions(RegionNames=['us-east-1'])
    json_string = json.dumps(result, indent=2)
    print(json_string)
