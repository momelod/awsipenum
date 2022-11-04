import boto3
import botocore
import sys
from awsipenum import msg

debug = False


def profiles_check(p: list): # noqa

    msg.debug = debug
    msg.info("\n")
    msg.hdr("Validating profiles ..")
    profiles_list = []

    if p:
        profiles_available = p
    else:
        profiles_available = boto3.session.Session().available_profiles

    if len(profiles_available) == 0:
        profiles_available = ["from_environment"]

    for p in profiles_available:
        msg.info("[" + p + "]: ")

        if p == "from_environment":
            session = boto3.session.Session()
        else:
            session = boto3.session.Session(profile_name=p)

        if session.region_name is None:
            msg.fatal("AWS_DEFAULT_REGION is undefined")

        sts = session.client(
            service_name='sts'
        )
        try:
            profile = sts.get_caller_identity()
            msg.ok("Profile Validated")
        except botocore.exceptions.ClientError:
            profile = False
            msg.warn("ClientError")
        except botocore.exceptions.ConfigParseError:
            profile = False
            msg.warn("ConfigParseError")
        except botocore.exceptions.ConnectTimeoutError:
            profile = False
            msg.warn("ConnectTimeoutError")
        except botocore.exceptions.CredentialRetrievalError:
            profile = False
            msg.warn("CredentialRetrievalError")
        except botocore.exceptions.NoCredentialsError:
            profile = False
            msg.warn("NoCredentialsError")

        msg.info("")
        if profile:
            profiles_list.append(p)

    if not profiles_list:
        msg.fatal("No working profiles found")
        sys.exit(1)
    else:
        return profiles_list
