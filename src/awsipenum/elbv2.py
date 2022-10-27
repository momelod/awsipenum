import botocore
import boto3
from awsipenum import msg

debug = False
msg.debug = debug


def elbv2_ips(p: str, r: str):
    session = boto3.session.Session(profile_name=p, region_name=r)
    client = session.client('elbv2')
    list = []

    msg.info("\n")
    msg.info("[" + p + "]" + "[" + r + "]: ")

    try:
        result = client.describe_load_balancers()
    except botocore.errorfactory.ClientError:
        result = False

    if result:
        msg.hdr("Enumerating LoadBalancer v2 IPs ..")

        for lb in result['LoadBalancers']:
            i = finding()
            i.type = "elb_v2 " + lb['Type']
            i.id = lb['LoadBalancerArn']
            i.region = r
            i.profile = p
            i.vpc = lb['VpcId']
            i.name = lb['LoadBalancerName']

            for az in lb['AvailabilityZones']:
                ip_list = []

                for ip in az['LoadBalancerAddresses']:
                    ip_list.append(ip['IpAddress'])

                i.public_ip = ip_list

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
            'name',
            'vpc',
            'region',
            'profile'
        ]:
            self.__dict__[key] = value
        else:
            pass

    def show(self):
        return self.__dict__
