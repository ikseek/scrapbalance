from argparse import ArgumentParser

from scrapbalance.scrapmts import MTSHelper


def print_status(login, password):
    scrapper = MTSHelper.login(login, password)
    print("\n".join(scrapper.status))
    scrapper.logout()


def parse_args():
    parser = ArgumentParser("Mobile balance request tool")
    parser.add_argument('phone', help="Phone number")
    parser.add_argument('password', help="Self-service password")
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        print_status(args.phone, args.password)
    except Exception as e:
        print(e)
        exit(1)


if __name__ == '__main__':
    main()
