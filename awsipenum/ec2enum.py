import botocore
import boto3
from . import msg

msg = msg.msg


def profiles_check(p: str, debug: bool):
    msg("info", "\n", debug)
    msg("hdr", "Validating profiles ..", debug)
    profiles_list = []

    if p:
        profiles_available = [p]
    else:
        profiles_available = boto3.session.Session().available_profiles

    for p in profiles_available:
        msg("info", "[" + p + "]: ", debug)
        session = boto3.session.Session(profile_name=p)
        sts = session.client(
            service_name='sts'
        )
        try:
            profile = sts.get_caller_identity()
            msg("ok", "Profile Validated", debug)
        except botocore.exceptions.ClientError:
            profile = False
            msg("warn", "ClientError", debug)
        except botocore.exceptions.ConfigParseError:
            profile = False
            msg("warn", "ConfigParseError", debug)
        except botocore.exceptions.ConnectTimeoutError:
            profile = False
            msg("warn", "ConnectTimeoutError", debug)
        except botocore.exceptions.CredentialRetrievalError:
            profile = False
            msg("warn", "CredentialRetrievalError", debug)
        except botocore.exceptions.NoCredentialsError:
            profile = False
            msg("warn", "NoCredentialsError", debug)

        msg("info", "", debug)
        if profile:
            profiles_list.append(p)

    if not profiles_list:
        msg("fatal", "No working profiles found", debug)
        return False
    else:
        return profiles_list


def regions(p: str, r: str, debug: bool):
    msg("info", "\n", debug)
    msg("hdr", "Validating region access ..", debug)
    list = []
    region_enabled = []
    session = boto3.session.Session(profile_name=p)

    if r:
        list = [r]
    else:
        ec2 = session.client('ec2')
        regions = ec2.describe_regions()

        for r in regions['Regions']:
            list.append(r['RegionName'])

    for r in list:
        msg("info", "[" + p + "]" + "[" + r + "]: ", debug)
        sts = session.client('sts', region_name=r)
        try:
            check = sts.get_caller_identity()
        except botocore.exceptions.ClientError:
            check = False

        if check:
            msg("ok", "Region Enabled", debug)
            region_enabled.append(r)
        else:
            msg("warn", "RegionDisabledException", debug)

        msg("info", "", debug)

    return region_enabled


def enum_ec2(p: str, r: str, debug: bool):
    session = boto3.session.Session(profile_name=p, region_name=r)
    ec2 = session.client('ec2')
    count = 0
    msg("info", "\n", debug)
    msg("info", "[" + p + "]" + "[" + r + "]: ", debug)
    try:
        result = ec2.describe_instances()
    except botocore.errorfactory.ClientError:
        result = False

    if result:
        msg("hdr", "Enermerating Public IPs ..", debug)
        for reservation in result['Reservations']:
            for instance in reservation['Instances']:
                if instance.get(u'PublicIpAddress') is not None:
                    count += 1
                    id = instance['InstanceId']
                    ip = instance['PublicIpAddress']
                    tags = instance['Tags']
                    vpc = instance['VpcId']

                    for t in tags:
                        if t['Key'] == 'Name':
                            name = t['Value']

                    finding.id = id
                    finding.ip = ip
                    finding.name = name
                    finding.vpc = vpc
                    print(finding.ip)
    else:
        msg("warn", "RegionDisabledException", debug)

    msg("ko", "Found: " + str(count), debug)


class finding:
    def __init__(self):
        self.id = ""
        self.ip = ""
        self.name = ""
        self.vpc = ""
