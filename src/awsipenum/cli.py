from argparse import ArgumentParser, BooleanOptionalAction
from awsipenum import sts, ec2, render, elb, cloudfront, rds, msg
import json
import requests


def create_parser():
    parser = ArgumentParser()
    parser.add_argument(
        '-d', '--debug',
        default=False,
        help='enable debug',
        action=BooleanOptionalAction
    )
    parser.add_argument(
        '-p', '--profile',
        nargs='+',
        default=False,
        help='choose a single profile'
    )
    parser.add_argument(
        '-r', '--region',
        nargs='+',
        default=False,
        help='choose a single region'
    )
    parser.add_argument(
        '-f', '--format',
        choices=["json", "yaml"],
        default='json',
        help='output format'
    )
    parser.add_argument(
        '--ipv4',
        help='enable ipv4',
        default=False,
        action=BooleanOptionalAction
    )
    parser.add_argument(
        '--ipv6',
        help='enable ipv6',
        default=False,
        action=BooleanOptionalAction
    )
    parser.add_argument(
        '--external',
        help='enable external public ips',
        default=False,
        action=BooleanOptionalAction
    )
    parser.add_argument(
        '--internal',
        help='enable internal private ips',
        default=False,
        action=BooleanOptionalAction
    )
    parser.add_argument(
        '--cloudfront',
        help='enable cloudfront',
        default=False,
        action=BooleanOptionalAction
    )
    parser.add_argument(
        '--ec2',
        help='enable ec2',
        default=False,
        action=BooleanOptionalAction
    )
    parser.add_argument(
        '--elb',
        help='enable elb',
        default=False,
        action=BooleanOptionalAction
    )
    parser.add_argument(
        '--elbv2',
        help='enable elbv2',
        default=False,
        action=BooleanOptionalAction
    )
    parser.add_argument(
        '--rds',
        help='enable rds',
        default=False,
        action=BooleanOptionalAction
    )
    parser.add_argument(
        '-m', '--metadata',
        help='output with metadata',
        default=False,
        action=BooleanOptionalAction
    )

    return parser


def dnsOverHTTP(fqdn: str):
    """
    function to resolve dns name to ip address usiing Cloudflare's
    free dns over https (DoH) service.
    """
    headers = {"accept": "application/dns-json"}
    c = "https://cloudflare-dns.com/"
    q = "dns-query?name="
    v4 = '&type=A'
    v6 = '&type=AAAA'
    list = []

    for t in [v4, v6]:
        url = c + q + fqdn + t
        try:
            response = requests.get(url, headers=headers)
            a = json.loads(response.content)
        except Exception as err:
            msg.warn(err)

        if "Answer" in a:
            for i in range(len(a["Answer"])):
                each = a["Answer"][i]["data"]
                if each not in list:
                    list.append(each)

    list.sort()
    return list


def set_defaults(args):
    # If no single aws service is requested, do them ALL
    if args.cloudfront + args.ec2 + args.elb + args.elbv2 + args.rds == 0:
        args.cloudfront = True
        args.ec2 = True
        args.elb = True
        args.elbv2 = True
        args.rds = True

    # If no ip version is requested, do them ALL
    if args.ipv4 + args.ipv6 == 0:
        args.ipv4 = True
        args.ipv6 = True

    # If no private or public addresses are requested, do them ALL
    if args.internal + args.external == 0:
        args.internal = True
        args.external = True

    return args


def filter(inventory: list, args): # noqa
    list = []

    if args.metadata:
        # Private IPv4 metadata
        for md in inventory.metaPrivateIpv4():
            if md not in list:
                list.append(md)

        # Public IPv4 metadata
        for md in inventory.metaPublicIpv4():
            if md not in list:
                list.append(md)

        # Private IPv6 metadata
        for md in inventory.metaPrivateIpv6():
            if md not in list:
                list.append(md)

        # PublicIPv6 metadata
        for md in inventory.metaPublicIpv6():
            if md not in list:
                list.append(md)

    else:
        # Private IPv4 address only
        if args.ipv4 and args.internal:
            for privateIpv4 in inventory.listPrivateIpv4():
                if privateIpv4 not in list:
                    list.append(privateIpv4)

        # Public IPv4 address only
        if args.ipv4 and args.external:
            for publicIpv4 in inventory.listPublicIpv4():
                if publicIpv4 not in list:
                    list.append(publicIpv4)

        # Private IPv6 address only
        if args.ipv6 and args.internal:
            for privateIpv6 in inventory.listPrivateIpv6():
                if privateIpv6 not in list:
                    list.append(privateIpv6)

        # Public IPv6 address only
        if args.ipv6 and args.external:
            for publicIpv6 in inventory.listPublicIpv6():
                if publicIpv6 not in list:
                    list.append(publicIpv6)

    return list


def main(): # noqa
    args = set_defaults(create_parser().parse_args())

    output = []
    sts.debug = args.debug
    ec2.debug = args.debug

    for p in sts.profiles_check(args.profile):
        for r in sts.regions(p, args.region):
            if args.ec2:
                item = filter(ec2.Instance(p, r), args)
                if item != []:
                    output.append(item)

                item = filter(ec2.elasticIPs(p, r), args)
                if item != []:
                    output.append(item)

            if args.elbv2:
                item = filter(elb.v2(p, r), args)
                if item != []:
                    output.append(item)

            if args.elb:
                item = filter(elb.Classic(p, r), args)
                if item != []:
                    output.append(item)

            if args.cloudfront:
                item = filter(cloudfront.Distrobution(p, r), args)
                if item != []:
                    output.append(item)

            if args.rds:
                item = filter(rds.Instance(p, r), args)
                if item != []:
                    output.append(item)

    if args.format == "json":
        print(render.to_json(output))
    elif args.format == "yaml":
        print(render.to_yaml(output))
