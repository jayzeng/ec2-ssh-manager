#!/usr/bin/env python
from __future__ import unicode_literals

from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.shortcuts import get_input
from prompt_toolkit.history import History
from prompt_toolkit.filters import Always

import os
import boto.ec2
import subprocess
import netaddr

def get_ec2_instance():
    region = os.environ.get("AWS_EC2_REGION")
    aws_key = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret = os.environ.get("AWS_SECRET_ACCESS_KEY")
    region = os.environ.get("AWS_EC2_REGION")
    region = region and boto.ec2.get_region(region,
                                            aws_access_key_id=aws_key,
                                            aws_secret_access_key=aws_secret)

    return boto.ec2.connection.EC2Connection(aws_key, aws_secret, region=region)

def ec2_active_instances(label_tag, filters):
    instances = {}
    kwargs = {}

    if filters:
        kwargs['filters'] = filters

    ec2_instance = get_ec2_instance()
    reservations = ec2_instance.get_all_instances(**kwargs)
    for reservation in reservations:
        for instance in reservation.instances:
            if instance.ip_address:
                instances[instance.ip_address] = '%s (%s, %s)' % (instance.tags.get(label_tag), instance.instance_type, instance.ip_address)
            else:
                instances[instance.private_ip_address] = '%s (%s, %s)' % (instance.tags.get(label_tag), instance.instance_type, instance.ip_address)

    return instances

def cli():
    tag = "Name"
    filters = {}
    instances = ec2_active_instances(tag, filters)
    instances = instances.values()
    instances.sort()

    instance_completer = WordCompleter(instances, ignore_case=True)
    history = History()

    selecting_instance = True

    while selecting_instance:
        text = get_input('Pick an instance to ssh in: ', completer=instance_completer, history=history, enable_system_bindings=Always())
        ip = text.split(' ')[-1].replace(')', '')

        if netaddr.valid_ipv4(ip) == True:
            subprocess.call(['ssh', ip])
            selecting_instance = False

        else:
            print 'Invalid IP: %s' % ip

if __name__ == '__main__':
    cli()
