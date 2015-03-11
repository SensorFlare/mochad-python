#!/bin/bash

apt-get install python-pip git-core  python-setuptools git-core

easy_install pip

# pika library for rabbitmq
pip install pika==0.9.8
