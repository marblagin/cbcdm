import argparse
import sys
from cbapi import CbDefenseAPI
from cbapi.psc.defense import Device


def build_cli_parser(description):
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("--cburl", help="CB server's URL.  e.g., http://127.0.0.1 ")
    parser.add_argument("--apitoken", help="API Token for Carbon Black server")
    parser.add_argument("--orgkey", help="Organization key value for Carbon Black server")
    parser.add_argument("--no-ssl-verify", help="Do not verify server SSL certificate.", action="store_true",
                        default=False)
    parser.add_argument("--profile", help="profile to connect", default="default")
    parser.add_argument("--verbose", help="enable debug logging", default=False, action='store_true')

    return parser


def get_cb_defense_object(args):
    if args.verbose:
        import logging
        logging.basicConfig()
        logging.getLogger("cbapi").setLevel(logging.DEBUG)
        logging.getLogger("__main__").setLevel(logging.DEBUG)

    if args.cburl and args.apitoken:
        cb = CbDefenseAPI(url=args.cburl, token=args.apitoken, ssl_verify=(not args.no_ssl_verify))
    else:
        cb = CbDefenseAPI(profile=args.profile)

    return cb


def main():
    parser = build_cli_parser("List devices")
    device_options = parser.add_mutually_exclusive_group(required=False)
    device_options.add_argument("-i", "--id", type=int, help="Device ID of sensor")
    device_options.add_argument("-n", "--hostname", help="Hostname")

    args = parser.parse_args()
    cb = get_cb_defense_object(args)

    if args.id:
        devices = [cb.select(Device, args.id)]
    elif args.hostname:
        devices = list(cb.select(Device).where("hostNameExact:{0}".format(args.hostname)))
    else:
        devices = list(cb.select(Device))

    print("{0:9} {1:40}{2:18}{3:28}{4}".format("ID", "Hostname", "IP Address", "Last Checkin Time", "Uninstall Code"))
    for device in devices:
        print("{0:9} {1:40s}{2:18s}{3}  {4}".format(device.deviceId, device.name or "None",
                                                    device.lastInternalIpAddress or "Unknown",
                                                    device.lastContact or "Unknown", device.uninstallCode))


if __name__ == "__main__":
    sys.exit(main())
