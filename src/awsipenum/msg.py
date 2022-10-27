import sys

debug = False


def hdr(msg: str):
    if debug:
        print('%s%s%s' % (f"{bcolors.HEADER}", msg, f"{bcolors.ENDC}"),
              file=sys.stderr)


def ok(msg: str):
    if debug:
        print('%s%s%s' % (f"{bcolors.OKGREEN}", msg, f"{bcolors.ENDC}"),
              file=sys.stderr)


def ko(msg: str):
    if debug:
        print('%s%s%s' % (f"{bcolors.OKBLUE}", msg, f"{bcolors.ENDC}"),
              file=sys.stderr)


def warn(msg: str):
    if debug:
        print('%s%s%s' % (f"{bcolors.WARNING}", msg, f"{bcolors.ENDC}"),
              file=sys.stderr)


def info(msg: str):
    if debug:
        print(f"{bcolors.ENDC}" + msg, end='',
              file=sys.stderr)


def fatal(msg: str):
    if debug:
        print(f"{bcolors.FAIL}" + msg + f"{bcolors.ENDC}",
              file=sys.stderr)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
