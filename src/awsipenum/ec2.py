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

    if p == "from_environment":
        session = boto3.session.Session()
    else:
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


class Instance:
    def __init__(self, aws_profile, aws_region):
        self.aws_profile = aws_profile
        self.aws_region = aws_region
        self.public_ip_list = []
        self.private_ip_list = []
        self.inventory = {}

    def getEc2(self):
        if self.aws_profile == "from_environment":
            session = boto3.session.Session()
        else:
            session = boto3.session.Session(
                profile_name=self.aws_profile,
                region_name=self.aws_region
            )

        client = session.client('ec2')

        try:
            paginator = client.get_paginator("describe_instances")
            paginator_interator = paginator.paginate()
            result_full = paginator_interator.build_full_result()
            result = result_full.get('Reservations')
        except botocore.errorfactory.ClientError:
            result = False
        return result

    def metaData(self): #noqa
        result = self.getEc2()
        if result:
            msg.hdr("Enumerating Instace IPs ..")
            for reservation in result:
                public_ip_list = []
                private_ip_list = []
                for instance in reservation['Instances']:
                    """
                    if no VpCID is present the instance has been terminated
                    """
                    if "VpcId" in instance:
                        type = "ec2_instance"
                        id = instance['InstanceId']
                        vpc = instance['VpcId']
                        region = self.aws_region
                        profile = self.aws_profile

                        if "Tags" in instance:
                            for t in instance['Tags']:
                                if t['Key'].lower() == 'name':
                                    name = t['Value']

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

                        self.inventory[id] = {
                            "id": id,
                            "name": name,
                            "type": type,
                            "vpc": vpc,
                            "profile": profile,
                            "region": region,
                            "public_ip": public_ip_list,
                            "private_ip": private_ip_list
                            }

        return self.inventory


class elasticIPs:
    def __init__(self, aws_profile, aws_region):
        self.aws_profile = aws_profile
        self.aws_region = aws_region
        self.inventory = {}

    def getEip(self):
        if self.aws_profile == "from_environment":
            session = boto3.session.Session()
        else:
            session = boto3.session.Session(
                profile_name=self.aws_profile,
                region_name=self.aws_region
            )

        client = session.client('ec2')

        try:
            result = client.describe_addresses()
        except botocore.errorfactory.ClientError:
            result = False
        return result

    def getVpcId(self, instance: str):
        if self.aws_profile == "from_environment":
            session = boto3.session.Session()
        else:
            session = boto3.session.Session(
                profile_name=self.aws_profile,
                region_name=self.aws_region
            )

        client = session.client('ec2')

        try:
            result = client.describe_instances(InstanceIds=[
                    instance])["Reservations"][0]["Instances"][0]['VpcId']
        except botocore.errorfactory.ClientError:
            result = False
        return result

    def metaData(self):
        result = self.getEip()
        name = ""
        vpc = ""
        if result:
            msg.hdr("Enumerating Elastic IPs ..")
            for address in result['Addresses']:
                type = "ec2_eip"
                id = address['NetworkInterfaceId']
                public_ip = [address['PublicIp']]
                region = self.aws_region
                profile = self.aws_profile

                if "Tags" in address:
                    for t in address['Tags']:
                        if t['Key'].lower() == 'name':
                            name = t['Value']

                if address.get(u'InstanceId') is not None:
                    instance = address['InstanceId']
                    vpc = self.getVpcId(instance)

                if address.get(u'PrivateIpAddress') is not None:
                    private_ip = [address['PrivateIpAddress']]

                self.inventory[id] = {
                    "id": id,
                    "name": name,
                    "instance": instance,
                    "type": type,
                    "vpc": vpc,
                    "profile": profile,
                    "region": region,
                    "public_ip": public_ip,
                    "private_ip": private_ip
                    }

        return self.inventory
