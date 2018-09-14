#!/usr/bin/env python
import com as bap
import argparse


def request(cmd):
    bap.init_com(port=bap.PORT, device_init=bap.device_init)
    r = bap.request(cmd)
    bap.com_close()
    return r


if __name__ == '__main__':
    # Handle arguments
    parser = argparse.ArgumentParser('cmd handler.')
    parser.add_argument("cmd", help="BA command, presently wery limited, try NOT ls, preset read etc...")
    parser.add_argument("-p", "--port", help="Set serial port, default is {}".format(bap.PORT))
    args = parser.parse_args()

    if args.port:
        bap.PORT = args.port

    r = request(args.cmd)
