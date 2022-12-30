import botocore
import boto3
import json
import requests
from awsipenum import msg

debug = False
msg.debug = debug


def elb_ips(p: str, r: str): # noqa
    if p == "from_environment":
        session = boto3.session.Session()
    else:
        session = boto3.session.Session(profile_name=p, region_name=r)

    client = session.client('elb')
    list = []

    msg.info("\n")
    msg.info("[" + p + "]" + "[" + r + "]: ")

    try:
        paginator = client.get_paginator("describe_load_balancers")
        paginator_interator = paginator.paginate()
        result_full = paginator_interator.build_full_result()
        result = result_full.get('LoadBalancerDescriptions')
    except botocore.errorfactory.ClientError:
        result = False

    if result:
        msg.hdr("Enumerating Classic LoadBalancer IPs ..")

        for lb in result:
            ip_list = []
            i = finding()
            i.type = "elb_classic"
            i.id = lb['DNSName']
            i.region = r
            i.profile = p
            i.vpc = lb['VPCId']
            i.name = lb['LoadBalancerName']

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
                        ip_list.append(answer['data'])

                    if lb['Scheme'] == 'internal':
                        i.private_ip = ip_list

                    elif lb['Scheme'] == 'internet-facing':
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
