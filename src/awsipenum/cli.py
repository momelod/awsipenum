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


def main(): # noqa
    args = create_parser().parse_args()

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

    list = []
    public_v4 = []
    private_v4 = []
    public_v6 = []
    private_v6 = []
    sts.debug = args.debug
    ec2.debug = args.debug

    for p in sts.profiles_check(args.profile):
        for r in sts.regions(p, args.region):

            if args.ec2:
                ec2_inventory = ec2.Instance(p, r)
                ec2_eips = ec2.elasticIPs(p, r)

                if args.ipv4 and args.internal:

                    for privateIpv4 in ec2_inventory.listPrivateIpv4():
                        if privateIpv4 not in private_v4:
                            private_v4.append(privateIpv4)

                    for privateIpv4 in ec2_eips.listPrivateIpv4():
                        if privateIpv4 not in private_v4:
                            private_v4.append(privateIpv4)

                if args.ipv4 and args.external:

                    for publicIpv4 in ec2_inventory.listPublicIpv4():
                        if publicIpv4 not in public_v4:
                            public_v4.append(publicIpv4)

                    for publicIpv4 in ec2_eips.listPublicIpv4():
                        if publicIpv4 not in public_v4:
                            public_v4.append(publicIpv4)

                if args.ipv6 and args.internal:

                    for privateIpv6 in ec2_inventory.listPrivateIpv6():
                        if privateIpv6 not in private_v6:
                            private_v6.append(privateIpv6)

                    for privateIpv6 in ec2_eips.listPrivateIpv6():
                        if privateIpv6 not in private_v6:
                            private_v6.append(privateIpv6)

                if args.ipv6 and args.external:

                    for publicIpv6 in ec2_inventory.listPublicIpv6():
                        if publicIpv6 not in public_v6:
                            public_v6.append(publicIpv6)

                    for publicIpv6 in ec2_eips.listPublicIpv6():
                        if publicIpv6 not in public_v6:
                            public_v6.append(publicIpv6)

            if args.elbv2:
                elb_inventory = elb.v2(p, r)

                if args.ipv4 and args.internal:

                    for privateIpv4 in elb_inventory.listPrivateIpv4():
                        if privateIpv4 not in private_v4:
                            private_v4.append(privateIpv4)

                if args.ipv4 and args.external:

                    for publicIpv4 in elb_inventory.listPublicIpv4():
                        if publicIpv4 not in public_v4:
                            public_v4.append(publicIpv4)

                if args.ipv6 and args.internal:

                    for privateIpv6 in elb_inventory.listPrivateIpv6():
                        if privateIpv6 not in private_v6:
                            private_v6.append(privateIpv6)

                if args.ipv6 and args.external:

                    for publicIpv6 in elb_inventory.listPublicIpv6():
                        if publicIpv6 not in public_v6:
                            public_v6.append(publicIpv6)

            if args.elb:
                elb_inventory = elb.Classic(p, r)

                if args.ipv4 and args.internal:

                    for privateIpv4 in elb_inventory.listPrivateIpv4():
                        if privateIpv4 not in private_v4:
                            private_v4.append(privateIpv4)

                if args.ipv4 and args.external:

                    for publicIpv4 in elb_inventory.listPublicIpv4():
                        if publicIpv4 not in public_v4:
                            public_v4.append(publicIpv4)

                if args.ipv6 and args.internal:

                    for privateIpv6 in elb_inventory.listPrivateIpv6():
                        if privateIpv6 not in private_v6:
                            private_v6.append(privateIpv6)

                if args.ipv6 and args.external:

                    for publicIpv6 in elb_inventory.listPublicIpv6():
                        if publicIpv6 not in public_v6:
                            public_v6.append(publicIpv6)

            if args.cloudfront:
                cf_distrobutions = cloudfront.Distrobution(p, r)

                if args.ipv4 and args.internal:

                    for privateIpv4 in cf_distrobutions.listPrivateIpv4():
                        if privateIpv4 not in private_v4:
                            private_v4.append(privateIpv4)

                if args.ipv4 and args.external:

                    for publicIpv4 in cf_distrobutions.listPublicIpv4():
                        if publicIpv4 not in public_v4:
                            public_v4.append(publicIpv4)

                if args.ipv6 and args.internal:

                    for privateIpv6 in cf_distrobutions.listPrivateIpv6():
                        if privateIpv6 not in private_v6:
                            private_v6.append(privateIpv6)

                if args.ipv6 and args.external:

                    for publicIpv6 in cf_distrobutions.listPublicIpv6():
                        if publicIpv6 not in public_v6:
                            public_v6.append(publicIpv6)

            if args.rds:
                rds_inventory = rds.Instance(p, r)

                if args.ipv4 and args.internal:

                    for privateIpv4 in rds_inventory.listPrivateIpv4():
                        if privateIpv4 not in private_v4:
                            private_v4.append(privateIpv4)

                if args.ipv4 and args.external:

                    for publicIpv4 in rds_inventory.listPublicIpv4():
                        if publicIpv4 not in public_v4:
                            public_v4.append(publicIpv4)

                if args.ipv6 and args.internal:

                    for privateIpv6 in rds_inventory.listPrivateIpv6():
                        if privateIpv6 not in private_v6:
                            private_v6.append(privateIpv6)

                if args.ipv6 and args.external:

                    for publicIpv6 in rds_inventory.listPublicIpv6():
                        if publicIpv6 not in public_v6:
                            public_v6.append(publicIpv6)

    if args.metadata:
        if args.format == "json":
            print(render.to_json(list))
        elif args.format == "yaml":
            print(render.to_yaml(list))
    else:
        if args.format == "json":
            print(render.to_json(
                private_v4 + private_v6 + public_v4 + public_v6)
            )
        elif args.format == "yaml":
            print(render.to_yaml(
                private_v4 + private_v6 + public_v4 + public_v6)
            )


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

    return list
