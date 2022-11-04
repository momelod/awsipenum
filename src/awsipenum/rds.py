import botocore
import boto3
import json
import requests
import ipaddress as ip
import warnings
from awsipenum import msg

warnings.filterwarnings(
    'ignore', category=FutureWarning, module='botocore.client'
)

debug = False
msg.debug = debug


def rds_ips(p: str, r: str): # noqa
    if p == "from_environment":
        session = boto3.session.Session()
    else:
        session = boto3.session.Session(profile_name=p, region_name=r)

    client = session.client('rds')
    list = []

    msg.info("\n")
    msg.info("[" + p + "]" + "[" + r + "]: ")

    try:
        paginator = client.get_paginator("describe_db_instances")
        paginator_interator = paginator.paginate()
        result_full = paginator_interator.build_full_result()
        result = result_full.get('DBInstances')
    except botocore.errorfactory.ClientError:
        result = False

    if result:
        msg.hdr("Enumerating RDS IPs ..")

        for db in result:
            ip_list = []
            i = finding()
            i.type = db['Engine']
            i.id = db['Endpoint']['Address']
            i.region = r
            i.profile = p
            i.vpc = db['DBSubnetGroup']['VpcId']
            i.name = db['DBInstanceIdentifier']

            headers = {"accept": "application/dns-json"}
            c = "https://cloudflare-dns.com/"
            q = "dns-query?name="
            v4 = '&type=A'
            v6 = '&type=AAAA'

            for t in [v4, v6]:
                url = c + q + i.id + t
                try:
                    response = requests.get(url, headers=headers)
                    a = json.loads(response.content)
                except Exception as err:
                    msg.warn(err)

                if "Answer" in a:
                    for answer in a['Answer']:
                        address = answer['data']
                        a = ip.ip_address(address)
                        ip_list.append(address)

                        if a.version == 4:
                            i.private_ip = ip_list
                        elif a.version == 6:
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
