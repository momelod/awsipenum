import botocore
import boto3
import json
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
        list = [r]
    else:
        client = session.client('ec2')
        regions = client.describe_regions()

        for r in regions['Regions']:
            list.append(r['RegionName'])

    for r in list:
        msg.info("[" + p + "]" + "[" + r + "]: ")
        sts = session.client('sts', region_name=r)
        try:
            check = sts.get_caller_identity()
        except botocore.exceptions.ClientError:
            check = False

        if check:
            msg.ok("Region Enabled")
            region_enabled.append(r)
        else:
            msg.warn("RegionDisabledException")

        msg.info("")

    return region_enabled


def ips(p: str, r: str):
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
        msg.hdr("Enumerating Public IPs ..")
        for reservation in result['Reservations']:
            for instance in reservation['Instances']:
                i = finding()
                i.id = instance['InstanceId']
                i.vpc = instance['VpcId']

                for t in instance['Tags']:
                    if t['Key'].lower() == 'name':
                        i.name = t['Value']

                if instance.get(u'PublicIpAddress') is not None:
                    i.public_ip = instance['PublicIpAddress']

                if instance.get(u'PrivateIpAddress') is not None:
                    i.private_ip = instance['PrivateIpAddress']

                list.append(json.loads(i.show()))
    else:
        msg.warn("RegionDisabledException")

    print(json.dumps(list))


class finding:
    def __init__(self):
        self.id = ""
        self.public_ip = ""
        self.private_ip = ""
        self.name = ""
        self.vpc = ""

    def show(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True)
