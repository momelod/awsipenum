from argparse import ArgumentParser, BooleanOptionalAction
from awsipenum import sts, ec2, render, elbv2, elb, cloudfront, rds
import ipaddress as ip


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
        default=True,
        action=BooleanOptionalAction
    )
    parser.add_argument(
        '--ipv6',
        help='enable ipv6',
        default=True,
        action=BooleanOptionalAction
    )
    parser.add_argument(
        '--external',
        help='enable external public ips',
        default=True,
        action=BooleanOptionalAction
    )
    parser.add_argument(
        '--internal',
        help='enable internal private ips',
        default=True,
        action=BooleanOptionalAction
    )
    parser.add_argument(
        '--cloudfront',
        help='enable cloudfront',
        default=True,
        action=BooleanOptionalAction
    )
    parser.add_argument(
        '--ec2',
        help='enable ec2',
        default=True,
        action=BooleanOptionalAction
    )
    parser.add_argument(
        '--elb',
        help='enable elb',
        default=True,
        action=BooleanOptionalAction
    )
    parser.add_argument(
        '--elbv2',
        help='enable elbv2',
        default=True,
        action=BooleanOptionalAction
    )
    parser.add_argument(
        '--rds',
        help='enable rds',
        default=True,
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

    list = []
    public_v4 = []
    private_v4 = []
    public_v6 = []
    private_v6 = []
    filtered_list = []

    args = create_parser().parse_args()
    sts.debug = args.debug
    ec2.debug = args.debug

    profile_list = sts.profiles_check(args.profile)

    for p in profile_list:
        for r in ec2.regions(p, args.region):

            if args.ec2:
                instance_obj = ec2.Instance(p, r)
                instance_ips = instance_obj.metaData()
                eip_obj = ec2.elasticIPs(p, r)
                eip_ips = eip_obj.metaData()

                for i in instance_ips:
                    if instance_ips[i] not in list:
                        list.append(instance_ips[i])

                for i in eip_ips:
                    if eip_ips[i] not in list:
                        list.append(eip_ips[i])

            if args.elbv2:
                elbv2_ips = elbv2.elbv2_ips(p, r)

                for i in elbv2_ips:
                    if i not in list:
                        list.append(i)

            if args.elb:
                elb_ips = elb.elb_ips(p, r)

                for i in elb_ips:
                    if i not in list:
                        list.append(i)

            if args.cloudfront:
                cloudfront_ips = cloudfront.cloudfront_ips(p, r)

                for i in cloudfront_ips:
                    if i not in list:
                        list.append(i)

            if args.rds:
                rds_ips = rds.rds_ips(p, r)

                for i in rds_ips:
                    if i not in list:
                        list.append(i)

    for x in list:
        if "public_ip" in x:

            for y in x['public_ip']:
                a = ip.ip_address(y)
                if a.version == 4:
                    if y not in public_v4:
                        public_v4.append(y)
                elif a.version == 6:
                    if y not in public_v6:
                        public_v6.append(y)

        if "private_ip" in x:

            for z in x['private_ip']:
                a = ip.ip_address(z)
                if a.version == 4:
                    if z not in private_v4:
                        private_v4.append(z)
                elif a.version == 6:
                    if z not in private_v6:
                        private_v6.append(z)

    if args.internal:
        if args.ipv4:
            for i in private_v4:
                filtered_list.append(i)
        if args.ipv6:
            for i in private_v6:
                filtered_list.append(i)

    if args.external:
        if args.ipv4:
            for i in public_v4:
                filtered_list.append(i)
        if args.ipv6:
            for i in public_v6:
                filtered_list.append(i)

    if args.metadata:
        if args.format == "json":
            print(render.to_json(list))
        elif args.format == "yaml":
            print(render.to_yaml(list))
    else:
        if args.format == "json":
            print(render.to_json(filtered_list))
        elif args.format == "yaml":
            print(render.to_yaml(filtered_list))
