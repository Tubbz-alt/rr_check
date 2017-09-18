#!/usr/bin/bash

echo "$USER ALL=(ALL) NOPASSWD:ALL" |sudo tee -a /etc/sudoers

sudo apt-get install python3-xlib python3-pip python3-setuptools libwnck-3-dev  python3-tk 
pip3 install --trusted-host pypi.douban.com -i http://pypi.douban.com/simple/ pandas

cd rr_check

python3 check_pkgs.py
