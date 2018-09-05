#!/usr/bin/env python3
import com as bap
import argparse
import json
import os
import requests

""" Reprogramming sequence
$ python2 <path>/bactl.py 0017b0024
Testing /dev/ttyACM0
Sending to /dev/ttyACM0
/dev/ttyACM0: 404 Command not found
/dev/ttyACM0 selected
SEND: 
SEND: 
SEND: userpage get
RECV: MAC: ff:ff:ff:ff:ff:ff
RECV: hw[0]: 12002_R1B
RECV: serial[0]: 0017B0024
RECV: hw[1]: KEY
RECV: serial[1]: 1F5PCKKVUI
RECV: hw[2]: 77016_R2A
RECV: serial[2]: 
RECV: 200 OK
Setting serial and hw[0] (12002_R1B) and hw[1] (77016_R2A)
Got serial: 0017B0024.
SEND: userpage unlock 0017B0024
RECV: 200 OK
SEND: userpage erase
RECV: 200 OK
{u'serial[1]': u'1F5PCKKVUI', u'hw[1]': u'KEY', u'serial[0]': u'0017B0024', u'hw[2]': u'77016_R2A', u'serial[2]': u'', u'hw[0]': u'12002_R1B'}
SEND: userpage set serial[1] 1F5PCKKVUI
RECV: 200 OK
SEND: userpage set hw[1] KEY
RECV: 200 OK
SEND: userpage set serial[0] 0017B0024
RECV: 200 OK
SEND: userpage set hw[2] 77016_R2A
RECV: 200 OK
SEND: userpage set serial[2] 
RECV: 404 Syntax error
SEND: userpage set hw[0] 12002_R1B
RECV: 200 OK
SEND: df
RECV: Used: 104368
RECV: Available: 139000
RECV: 200 OK
Terminal mode: Press ESC to exit
"""
try:
    KEY = os.environ['PASSKEY']
    print('PASSKEY found in the environment.')
except KeyError as e:
    print('PASSKEY not found in the environment.')
    KEY = ''
SUPPORTSERIAL = '0017B0024'
TMP = 'curl --data "action=get&serial=0017b0024&passkey={}" rc.bohmeraudio.se/cgi-bin/production.py'.format(KEY)
URL = 'http://rc.bohmeraudio.se/cgi-bin/production.py'

def get_userpage_from_hw():
    d = None
    r = get_userpage_raw_data_hw()
    d = userpage_raw_hw_to_dict(r)
    return d


def get_userpage_from_server(serial):
    r = get_userpage_raw_data_server(serial)
    d = json.loads(r.text)
    print('Successfully downloaded userpage from server')
    for k, v in d['userpage'].items():
        print('{}: {}'.format(k, v))
    return d['userpage']


def get_userpage_raw_data_hw():
    bap.init_com(port=bap.PORT, device_init=bap.device_init)
    r = bap.request('userpage get')
    bap.com_close()
    return r


def get_userpage_raw_data_server(serial, passkey=KEY):
    r = ''
    r = requests.post(URL, data={'action': 'get', 'serial': serial, 'passkey': KEY})
    return r


def set_userpage(userpage_new):
    try:
        userpage_old = get_userpage_from_hw()
        print('Setting userpage for serial {}'.format(userpage_new.get('serial[0]')))
        print('Existing userpage serial {}'.format(userpage_old.get('serial[0]')))
        bap.init_com(port=bap.PORT, device_init=bap.device_init)
        r = bap.request('userpage unlock {}'.format(userpage_old.get('serial[0]')))
        r = bap.request('userpage erase')
        r = bap.request('userpage set serial[1] {}'.format(userpage_new.get('serial[1]')))
        r = bap.request('userpage set hw[1] KEY')
        r = bap.request('userpage set serial[0] {}'.format(userpage_new.get('serial[0]')))
        r = bap.request('userpage set hw[2] {}'.format(userpage_new.get('hw[2]')))
        r = bap.request('userpage set serial[2] {}'.format(userpage_new.get('serial[2]')), code=bap.SYNTAXERROR)
        r = bap.request('userpage set hw[0] {}'.format(userpage_new.get('hw[0]')))
        print('Successfully updated userpage. Result:')
        r = bap.request('userpage get')
    except Exception as e:
        print('ERROR. {}'.format(e))
    finally:
        bap.com_close()


def userpage_raw_hw_to_dict(b):
    d = {}
    l0 = b.decode().split('\n')
    for i in l0:
        if ':' in i:
            l1 = i.split(':')
            k = l1[0]
            v = l1[1:]
            v[0] = v[0].strip()
            if 'MAC' in k:
                # Special case since MAC: ff:ff:ff:ff:ff:ff
                addr = ''
                for addr_part in v:
                    addr += addr_part + ':'
                v[0] = addr[:-1]  # Remove last extra ':'
            d[k] = v[0]
        else:
            # Will skip data at the end: b'200 OK\n\n'
            pass

    for k, v in d.items():
        print('{}: {}'.format(k, v))

    return d


def test_server():
    d = get_userpage_from_server(serial=SUPPORTSERIAL)
    for k, v in d.items():
        print('{}: {}'.format(k, v))


def test_set_userpage():
    userpage_new = get_userpage_from_server('0025A0011')
    set_userpage(userpage_new)


def test_bap():
    d = get_userpage_from_hw()


if __name__ == '__main__':
    # Handle arguments
    parser = argparse.ArgumentParser('set/get of userpage.')
    parser.add_argument("-p", "--port", help="Set serial port, default is {}".format(bap.PORT))
    parser.add_argument("-s", "--serial", help="set the userpage with info for serial id.")
    args = parser.parse_args()

    if args.port:
        bap.PORT = args.port

    if args.serial:
        userpage_new = get_userpage_from_server(args.serial)
        set_userpage(userpage_new)
        exit(0)

    # default behavior
    d = get_userpage_from_hw()

