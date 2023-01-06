import botocore
import boto3
import ipaddress as ip
from awsipenum import msg, cli

debug = False
msg.debug = debug


class Distrobution:
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

        client = session.client('cloudfront')

        try:
            paginator = client.get_paginator("list_distributions")
            paginator_interator = paginator.paginate()
            result_full = paginator_interator.build_full_result()
            result = result_full.get('DistributionList')
        except botocore.errorfactory.ClientError:
            result = False

        msg.info("\n")
        msg.hdr("Enumerating Cloudfront Distrobutions ..")
        msg.info("[" + self.aws_profile + "]" + "[" + self.aws_region + "]")

        if result:
            msg.ok(" Found\n")
            distrobutions = result
            if "Items" in distrobutions:
                for distrobution in distrobutions['Items']:
                    type = "cloudfront"
                    id = distrobution['Id']
                    region = self.aws_region
                    profile = self.aws_profile
                    name = distrobution['DomainName']
                    public_ip_list = []
                    private_ip_list = []

                a = cli.dnsOverHTTP(name)

                for address in a:

                    if ip.ip_address(address).is_private:
                        private_ip_list.append(address)
                    else:
                        public_ip_list.append(address)

                    self.inventory[id] = {
                        "id": id,
                        "name": name,
                        "type": type,
                        "vpc": "",
                        "profile": profile,
                        "region": region,
                        "public_ip": public_ip_list,
                        "private_ip": private_ip_list
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
