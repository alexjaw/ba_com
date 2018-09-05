# -*- coding: utf-8 -*-
import datetime
import serial
import time

CMDOK = b'200 OK\n\n'
CMDNOTFOUND = b'404 Command not found\n\n'
SYNTAXERROR = b'404 Syntax error\n\n'
EOC = b'\n\n'  # End Of Cmd
EOL = b'\n\n'
PORT = '/dev/ttyACM0'

com = None


def init_com(port, baudrate=115200, timeout=1, rtscts=0, device_init=None):
    global com
    com_ok = False
    while not com_ok:
        try:
            com = serial.Serial(port=port, baudrate=baudrate, timeout=timeout, rtscts=rtscts)
            com_ok = True
            print('Com established through {}.'.format(com.name))
        except serial.serialutil.SerialException as e:
            print('Error. {}'.format(e))
            time.sleep(1)
    if device_init:
        device_init()


def com_close():
    if com.is_open:
        com.close()
        print('Com closed.')


def com_read():
    return com.read_until(EOL)


def com_send(cmd):
    if com.in_waiting > 0:
        msg = 'WARNING: Tried to send new cmd but there is still data in buffer from device. ' \
              'Num of bytes = {}'.format(com.in_waiting)
        #print(msg)
        raise BufferError(msg)
    else:
        cmd = cmd.encode() + EOC
        com.write(cmd)


def device_init():
    try:
        expect_response('dummy_init_device_cmd', code=CMDNOTFOUND, retry=True)
        print('Device init successful.')
    except (TimeoutError, BufferError, Exception) as e:
        print(e)
        raise IOError('ERROR. Device init unsuccessful.')


def expect_response(cmd, code=CMDOK, retry=True, timeout=10):
    com_send(cmd)
    r = com_read()
    t0 = datetime.datetime.now()
    if retry:
        retrying_info_shown = False
        while True:
            t1 = datetime.datetime.now()
            if (t1 - t0).total_seconds() > timeout:
                msg = 'Warning. Timeout ({}s). Could not get the expected response {} for cmd {}'.format(timeout, code, cmd)
                #print(msg)
                raise TimeoutError(msg)
            if code in r:
                # print('Response successful: {} in {}'.format(code, r))
                if retrying_info_shown:
                    print('Response issue resolved. Device responded with correct code.')
                break
            else:
                #print('Response failure: {} not in {}'.format(code, r))
                if not retrying_info_shown:
                    print('Some problem with response - retrying for {}s...'.format(timeout))
                    retrying_info_shown = True
                com_send(cmd)
                r = com_read()
    if com.in_waiting > 0:
        msg = 'WARNING: Still data in buffer from device. Num of bytes = {}'.format(com.in_waiting)
        #print(msg)
        raise BufferError(msg)
    return r


def request(cmd, code=CMDOK, retry=True):
    r = None
    try:
        print('SEND: {}'.format(cmd))
        if retry:
            r = expect_response(cmd, code, retry=True)
        else:
            r = expect_response(cmd, code, retry=False)
        print('RECV: {}'.format(r))
    except (TimeoutError, BufferError, Exception) as e:
        print(e)
    return r


if __name__ == '__main__':
    try:
        init_com(port=PORT, device_init=device_init)
    except (IOError, Exception) as e:
        print(e)
        exit(1)

    r = request('vol get')

    com_close()

