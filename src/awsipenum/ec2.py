import botocore
import boto3
from awsipenum import msg

debug = False
msg.debug = debug


def regions(p: str, r: str):
    msg.info("\n")
    msg.hdr("Validating region access ..")
    list = []
    region_enabled = []
    session = boto3.session.Session(profile_name=p)

    if r:
        list = r
    else:
        client = session.client('ec2')
        regions = client.describe_regions()

        for r in regions['Regions']:
            list.append(r['RegionName'])

    for region in list:
        msg.info("[" + p + "]" + "[" + region + "]: ")
        sts = session.client('sts', region_name=region)
        try:
            check = sts.get_caller_identity()
        except botocore.exceptions.ClientError:
            check = False

        if check:
            msg.ok("Region Enabled")
            if region not in region_enabled:
                region_enabled.append(region)
        else:
            msg.warn("RegionDisabledException")

        msg.info("")

    return region_enabled


def instance_ips(p: str, r: str): # noqa
    session = boto3.session.Session(profile_name=p, region_name=r)
    client = session.client('ec2')
    list = []

    msg.info("\n")
    msg.info("[" + p + "]" + "[" + r + "]: ")

    try:
        result = client.describe_instances()
    except botocore.errorfactory.ClientError:
        result = False

    if result:
        msg.hdr("Enumerating Instace IPs ..")
        for reservation in result['Reservations']:
            public_ip_list = []
            private_ip_list = []
            for instance in reservation['Instances']:
                """
                if no VpCID is present the instance has been terminated
                """
                if "VpcId" in instance:
                    i = finding()
                    i.type = "ec2_instance"
                    i.id = instance['InstanceId']
                    i.vpc = instance['VpcId']
                    i.region = r
                    i.profile = p

                    if "Tags" in instance:
                        for t in instance['Tags']:
                            if t['Key'].lower() == 'name':
                                i.name = t['Value']

                    for interface in instance['NetworkInterfaces']:
                        if interface['Ipv6Addresses']:
                            public_ip_list.append(interface['Ipv6Addresses'])

                        for assignment in interface['PrivateIpAddresses']:
                            if assignment.get(u'PrivateIpAddress') is not None:
                                private_ip_list.append(
                                    assignment['PrivateIpAddress']
                                )

                            if "Association" in assignment:
                                public_ip_list.append(
                                    assignment['Association']['PublicIp']
                                )

                    i.public_ip = public_ip_list
                    i.private_ip = private_ip_list

                    list.append(i.show())
    else:
        msg.warn("RegionDisabledException")

    return list


def elastic_ips(p: str, r: str):
    session = boto3.session.Session(profile_name=p, region_name=r)
    client = session.client('ec2')
    list = []

    msg.info("\n")
    msg.info("[" + p + "]" + "[" + r + "]: ")

    try:
        result = client.describe_addresses()
    except botocore.errorfactory.ClientError:
        result = False

    if result:
        msg.hdr("Enumerating Elastic IPs ..")
        for address in result['Addresses']:
            i = finding()
            i.type = "ec2_eip"
            i.id = address['AllocationId']
            i.public_ip = [address['PublicIp']]
            i.region = r
            i.profile = p

            if "Tags" in address:
                for t in address['Tags']:
                    if t['Key'].lower() == 'name':
                        i.name = t['Value']

            if address.get(u'InstanceId') is not None:
                i.instance = [address['InstanceId']]

            if address.get(u'PrivateIpAddress') is not None:
                i.private_ip = [address['PrivateIpAddress']]

            list.append(i.show())
    else:
        msg.warn("RegionDisabledException")

    return list


class finding:
    def __setitem__(self, key, value):
        if key in [
            'type',
            'id',
            'public_ip',
            'private_ip',
            'name',
            'vpc',
            'region',
            'instance',
            'profile'
        ]:
            self.__dict__[key] = value
        else:
            pass

    def show(self):
        return self.__dict__
