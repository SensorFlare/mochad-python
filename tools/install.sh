#!/bin/bash

apt-get install python-pip git-core  python-setuptools git-core

easy_install pip

# pika library for rabbitmq
pip install pika==0.9.8
# hautomation_x10 library for communication with mochad
pip install -e git+https://github.com/jpardobl/hautomation_x10.git#egg=hautomation_x10
