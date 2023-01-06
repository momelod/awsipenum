import botocore
import boto3
import ipaddress as ip
from awsipenum import msg

debug = False
msg.debug = debug


class Instance:
    def __init__(self, aws_profile, aws_region): #noqa
        self.aws_profile = aws_profile
        self.aws_region = aws_region
        self.public_ip_list = []
        self.private_ip_list = []
        self.inventory = {}

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

        msg.info("\n")
        msg.hdr("Enumerating ec2 Instace IPs ..")
        msg.info("[" + self.aws_profile + "]" + "[" + self.aws_region + "]")

        if result:
            msg.ok(" Found\n")
        else:
            msg.ko(" None found\n")

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

    def metaPublicIpv4(self):
        public_ip_list = []
        metadata = self.inventory

        for asset in metadata.keys():
            for public_ip in metadata[asset]["public_ip"]:
                address = ip.ip_address(public_ip)
                if address.version == 4:
                    public_ip_list.append(metadata[asset])

        return public_ip_list

    def metaPrivateIpv4(self):
        private_ip_list = []
        metadata = self.inventory

        for asset in metadata.keys():
            for private_ip in metadata[asset]["private_ip"]:
                address = ip.ip_address(private_ip)
                if address.version == 4:
                    private_ip_list.append(metadata[asset])

        return private_ip_list

    def metaPublicIpv6(self):
        public_ip_list = []
        metadata = self.inventory

        for asset in metadata.keys():
            for public_ip in metadata[asset]["public_ip"]:
                address = ip.ip_address(public_ip)
                if address.version == 6:
                    public_ip_list.append(metadata[asset])

        return public_ip_list

    def metaPrivateIpv6(self):
        private_ip_list = []
        metadata = self.inventory

        for asset in metadata.keys():
            for private_ip in metadata[asset]["private_ip"]:
                address = ip.ip_address(private_ip)
                if address.version == 6:
                    private_ip_list.append(metadata[asset])

        return private_ip_list

    def listPublicIpv4(self):
        public_ip_list = []
        metadata = self.inventory

        for asset in metadata.keys():
            for public_ip in metadata[asset]["public_ip"]:
                address = ip.ip_address(public_ip)
                if address.version == 4:
                    public_ip_list.append(public_ip)

        return public_ip_list

    def listPrivateIpv4(self):
        private_ip_list = []
        metadata = self.inventory

        for asset in metadata.keys():
            for private_ip in metadata[asset]["private_ip"]:
                address = ip.ip_address(private_ip)
                if address.version == 4:
                    private_ip_list.append(private_ip)

        return private_ip_list

    def listPublicIpv6(self):
        public_ip_list = []
        metadata = self.inventory

        for asset in metadata.keys():
            for public_ip in metadata[asset]["public_ip"]:
                address = ip.ip_address(public_ip)
                if address.version == 6:
                    public_ip_list.append(public_ip)

        return public_ip_list

    def listPrivateIpv6(self):
        private_ip_list = []
        metadata = self.inventory

        for asset in metadata.keys():
            for private_ip in metadata[asset]["private_ip"]:
                address = ip.ip_address(private_ip)
                if address.version == 6:
                    private_ip_list.append(private_ip)

        return private_ip_list


class elasticIPs:
    def __init__(self, aws_profile, aws_region): #noqa
        self.aws_profile = aws_profile
        self.aws_region = aws_region
        self.inventory = {}

        if self.aws_profile == "from_environment":
            session = boto3.session.Session()
        else:
            session = boto3.session.Session(
                profile_name=self.aws_profile,
                region_name=self.aws_region
            )

        client = session.client('ec2')

        try:
            result = client.describe_addresses()["Addresses"]
        except botocore.errorfactory.ClientError:
            result = False

        name = ""
        vpc = ""

        msg.info("\n")
        msg.hdr("Enumerating ec2 Elastic IPs ..")
        msg.info(
                "[" + self.aws_profile + "]" + "[" + self.aws_region + "]")
        if result:
            msg.ok(" Found\n")
            for address in result:
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
                    try:
                        vpc = client.describe_instances(
                            InstanceIds=[instance])[
                                "Reservations"
                            ][0]["Instances"][0]['VpcId']
                    except botocore.errorfactory.ClientError:
                        vpc = ""

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
        else:
            msg.ko(" None found\n")

    def metaPublicIpv4(self):
        public_ip_list = []
        metadata = self.inventory

        for asset in metadata.keys():
            for public_ip in metadata[asset]["public_ip"]:
                address = ip.ip_address(public_ip)
                if address.version == 4:
                    public_ip_list.append(asset)

        return public_ip_list

    def metaPrivateIpv4(self):
        private_ip_list = []
        metadata = self.inventory

        for asset in metadata.keys():
            for private_ip in metadata[asset]["private_ip"]:
                address = ip.ip_address(private_ip)
                if address.version == 4:
                    private_ip_list.append(metadata[asset])

        return private_ip_list

    def metaPublicIpv6(self):
        public_ip_list = []
        metadata = self.inventory

        for asset in metadata.keys():
            for public_ip in metadata[asset]["public_ip"]:
                address = ip.ip_address(public_ip)
                if address.version == 6:
                    public_ip_list.append(asset)

        return public_ip_list

    def metaPrivateIpv6(self):
        private_ip_list = []
        metadata = self.inventory

        for asset in metadata.keys():
            for private_ip in metadata[asset]["private_ip"]:
                address = ip.ip_address(private_ip)
                if address.version == 6:
                    private_ip_list.append(metadata[asset])

        return private_ip_list

    def listPublicIpv4(self):
        public_ip_list = []
        metadata = self.inventory

        for asset in metadata.keys():
            for public_ip in metadata[asset]["public_ip"]:
                address = ip.ip_address(public_ip)
                if address.version == 4:
                    public_ip_list.append(public_ip)

        return public_ip_list

    def listPrivateIpv4(self):
        private_ip_list = []
        metadata = self.inventory

        for asset in metadata.keys():
            for private_ip in metadata[asset]["private_ip"]:
                address = ip.ip_address(private_ip)
                if address.version == 4:
                    private_ip_list.append(private_ip)

        return private_ip_list

    def listPublicIpv6(self):
        public_ip_list = []
        metadata = self.inventory

        for asset in metadata.keys():
            for public_ip in metadata[asset]["public_ip"]:
                address = ip.ip_address(public_ip)
                if address.version == 6:
                    public_ip_list.append(public_ip)

        return public_ip_list

    def listPrivateIpv6(self):
        private_ip_list = []
        metadata = self.inventory

        for asset in metadata.keys():
            for private_ip in metadata[asset]["private_ip"]:
                address = ip.ip_address(private_ip)
                if address.version == 6:
                    private_ip_list.append(private_ip)

        return private_ip_list
