import botocore
import boto3
import json
import requests
from awsipenum import msg

debug = False
msg.debug = debug


def cloudfront_ips(p: str, r: str):
    session = boto3.session.Session(profile_name=p, region_name=r)
    client = session.client('cloudfront')
    list = []

    msg.info("\n")
    msg.info("[" + p + "]" + "[" + r + "]: ")

    try:
        result = client.list_distributions()
    except botocore.errorfactory.ClientError:
        result = False

    if result:
        msg.hdr("Enumerating Cloudfront Distrobutions ..")

        distrobutions = result['DistributionList']
        if "Items" in distrobutions:
            for distrobution in distrobutions['Items']:
                ip_list = []
                i = finding()
                i.type = "cloudfront"
                i.id = distrobution['Id']
                i.region = r
                i.profile = p
                i.name = distrobution['DomainName']

                headers = {"accept": "application/dns-json"}
                c = "https://cloudflare-dns.com/"
                q = "dns-query?name="
                v4 = '&type=A'
                v6 = '&type=AAAA'

                for t in [v4, v6]:
                    url = c + q + i.name + t
                    try:
                        response = requests.get(url, headers=headers)
                        a = json.loads(response.content)
                    except Exception as err:
                        msg.warn(err)

                    if a.get(u'Answer'):
                        for answer in a['Answer']:
                            ip_list.append(answer['data'])

                        i.public_ip = ip_list

                list.append(i.show())
    else:
        msg.warn("RegionDisabledException")

    return list


class finding:
    def __setitem__(self, key, value):
        if key in [
            'type'
            'id',
            'public_ip',
            'name',
            'region',
            'profile'
        ]:
            self.__dict__[key] = value
        else:
            pass

    def show(self):
        return self.__dict__
