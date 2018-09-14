#!/bin/bash
#What is needed in order to execute simple BA commands on wavelet:
#- update pip
wget https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py --prefix=/usr/local/
sudo pip install virtualenv
#- create virtualenv i ba_com, will be 2.7...
virtualenv venv
echo  Do the rest manually.
#source venv/bin/activate
#- at this point, with pyton3 as 3.2, skip requirements.txt, install only pyserial
#pip install pyserial
#- Should be able to run cmd.py
#./cmd.py -p /dev/ttyAMA0 version
