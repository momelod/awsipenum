# AWS IP address Enumerator

Generate a list of all IP addresses in your AWS account(s).

Features:
* Iterates over all your AWS accounts as defined by `aws configure` or from environment vars AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY.
* Limit the enumeration by aws profile(s), region(s), service(s), IP version, public or private IPs.
* Outputs to either `json` or `yaml` formats.
* Optionally show metadata (Type, Name) along with IP.
* Currently supports `ec2`, `elb`, `elbv2`, `rds` and `cloudfront`.


## Installation
```
pip install awsipenum
```

## Usage
If you do not supply a profile or region argument then ALL your profiles and regions will be scanned.

```
usage: awsipenum [-h] [-d | --debug | --no-debug] [-p PROFILE [PROFILE ...]] [-r REGION [REGION ...]]
                 [-f {json,yaml}] [--ipv4 | --no-ipv4] [--ipv6 | --no-ipv6] [--external | --no-external]
                 [--internal | --no-internal] [--cloudfront | --no-cloudfront] [--ec2 | --no-ec2]
                 [--elb | --no-elb] [--elbv2 | --no-elbv2] [--rds | --no-rds]
                 [-m | --metadata | --no-metadata]

options:
  -h, --help            show this help message and exit
  -d, --debug, --no-debug
                        enable debug (default: False)
  -p PROFILE [PROFILE ...], --profile PROFILE [PROFILE ...]
                        choose a single profile
  -r REGION [REGION ...], --region REGION [REGION ...]
                        choose a single region
  -f {json,yaml}, --format {json,yaml}
                        output format
  --ipv4, --no-ipv4     enable ipv4 (default: True)
  --ipv6, --no-ipv6     enable ipv6 (default: True)
  --external, --no-external
                        enable external public ips (default: True)
  --internal, --no-internal
                        enable internal private ips (default: True)
  --cloudfront, --no-cloudfront
                        enable cloudfront (default: True)
  --ec2, --no-ec2       enable ec2 (default: True)
  --elb, --no-elb       enable elb (default: True)
  --elbv2, --no-elbv2   enable elbv2 (default: True)
  --rds, --no-rds       enable rds (default: True)
  -m, --metadata, --no-metadata
                        output with metadata (default: False)
```

## Examples

With debug and metadata:

```bash
awsipenum --profile default --region us-east-1 --metadata --debug

Validating profiles ..
[default]: Profile Validated

Validating region access ..
[default][us-east-1]: Region Enabled

[default][us-east-1]: Enumerating Instace IPs ..

[default][us-east-1]: Enumerating Elastic IPs ..

[default][us-east-1]: Enumerating LoadBalancer v2 IPs ..

[default][us-east-1]: Enumerating Classic LoadBalancer IPs ..

[default][us-east-1]: Enumerating Cloudfront Distrobutions ..

[default][us-east-1]: Enumerating RDS IPs ..
[
    {
        "type": "ec2_instance",
        "id": "i-99999999999999999",
        "vpc": "vpc-99999999",
        "region": "us-east-1",
        "profile": "default",
        "name": "ubuntu-server",
        "public_ip": [
            "1.2.3.4"
        ],
        "private_ip": [
            "10.0.0.10"
        ]
    },
    {
        "type": "cloudfront",
        "id": "E1N99999999999",
        "region": "us-east-1",
        "profile": "default",
        "name": "d9999999999999.cloudfront.net",
        "public_ip": [
            "1.2.3.5",
            "1.2.3.6",
            "1.2.3.7",
            "1.2.3.8",
            "fd8a:42f0:6c9e:ce95:0000:0000:0000:0001",
            "fd8a:42f0:6c9e:ce95:0000:0000:0000:0002",
            "fd8a:42f0:6c9e:ce95:0000:0000:0000:0003",
            "fd8a:42f0:6c9e:ce95:0000:0000:0000:0004",
            "fd8a:42f0:6c9e:ce95:0000:0000:0000:0005",
            "fd8a:42f0:6c9e:ce95:0000:0000:0000:0006",
            "fd8a:42f0:6c9e:ce95:0000:0000:0000:0007",
            "fd8a:42f0:6c9e:ce95:0000:0000:0000:0008"
        ]
    }
]
```

Only show public IP v4
```bash
awsipenum -p default --region us-east-1 --no-ipv6 --no-internal
[
    "1.2.3.4",
    "1.2.3.5",
    "1.2.3.6",
    "1.2.3.7",
    "1.2.3.8"
]
```

Filter out a service
```bash
awsipenum -p default --region us-east-1 --no-cloudfront -f yaml
- 10.0.0.10
- 1.2.3.4
```

Run as a docker container:
```bash
docker run --rm --name awsipenum -v ~/.aws:/root/.aws momelod/awsipenum --profile my-named-profile --region us-east-1

docker run --rm --name awsipenum -e AWS_SECRET_ACCESS_KEY -e AWS_ACCESS_KEY_ID momelod/awsipenum 
```
