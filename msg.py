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


def msg(stat: str, msg: str, debug: bool):
    if debug:
        if stat == "hdr":
            print('%s%s%s' % (f"{bcolors.HEADER}", msg, f"{bcolors.ENDC}"))
        if stat == "ok":
            print('%s%s%s' % (f"{bcolors.OKGREEN}", msg, f"{bcolors.ENDC}"))
        if stat == "ko":
            print('%s%s%s' % (f"{bcolors.OKBLUE}", msg, f"{bcolors.ENDC}"))
        if stat == "warn":
            print('%s%s%s' % (f"{bcolors.WARNING}", msg, f"{bcolors.ENDC}"))
        if stat == "info":
            print(f"{bcolors.ENDC}" + msg, end='')

    if stat == "fatal":
        print(f"{bcolors.FAIL}" + msg + f"{bcolors.ENDC}")
