from argparse import ArgumentParser
from collections import OrderedDict
from configparser import ConfigParser
from getpass import getpass
from os.path import expanduser

from scrapbalance.errors import UnexpectedResponse
from scrapbalance.scrap import MobileScrapper

CFG_FILE_NAME = expanduser("~/.scrapbalance")


def print_status(login, password, cookies):
    scrap_type = MobileScrapper.pick(login)
    scrapper = scrap_type.restore(cookies)
    try:
        status = scrapper.status
    except UnexpectedResponse:
        scrapper = scrap_type.login(login, password)
        status = scrapper.status
    print(">>>", login, "<<<")
    print("\n".join(status))
    print()
    return scrapper.save()


def parse_args():
    parser = ArgumentParser(description="Mobile balance request tool")
    parser.add_argument('-n', '--number', help="Phone number")
    parser.add_argument('-p', '--password', help="Self-service password")
    parser.add_argument('-s', '--store', action='store_true',
                        help="Remember number and password")
    return parser.parse_args()


def parse_config():
    parser = ConfigParser()
    parser.optionxform = str
    parser.read(CFG_FILE_NAME)
    return parser


def main():
    args = parse_args()
    config = parse_config()
    if args.number:
        if args.number not in config:
            config.add_section(args.number)
        cookies = dict(config[args.number])
        password = cookies.pop('__password__', None)
        store_password = True if password else args.store
        if args.password:
            password = args.password
        elif not password:
            password = getpass()
        cookies = print_status(args.number, password, cookies)
        if store_password:
            cookies['__password__'] = password
        config[args.number] = OrderedDict(sorted(cookies.items()))
        with open(CFG_FILE_NAME, 'w') as file:
            config.write(file)
    else:
        for section in config.sections():
            number = section
            cookies = dict(config[number])
            password = cookies.pop(('__password__'), None)
            cookies = print_status(number, password, cookies)
            cookies['__password__'] = password
            config[number] = OrderedDict(sorted(cookies.items()))
            with open(CFG_FILE_NAME, 'w') as file:
                config.write(file)


if __name__ == '__main__':
    main()
