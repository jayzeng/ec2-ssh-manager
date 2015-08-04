#!/usr/bin/env python
from __future__ import unicode_literals

from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.shortcuts import get_input
import os
import boto.ec2
import subprocess

_ec2 = None
region = os.environ.get("AWS_EC2_REGION")
aws_key = os.environ.get("AWS_ACCESS_KEY_ID")
aws_secret = os.environ.get("AWS_SECRET_ACCESS_KEY")
region = os.environ.get("AWS_EC2_REGION")
tag = "Name"
region = region and boto.ec2.get_region(region,
                                        aws_access_key_id=aws_key,
                                        aws_secret_access_key=aws_secret)

_ec2 = boto.ec2.connection.EC2Connection(aws_key, aws_secret, region=region)

def ec2_active_instances(label_tag, filters):
    instances = []
    kwargs = {}

    if filters:
        kwargs['filters'] = filters

    reservations = _ec2.get_all_instances(**kwargs)
    for reservation in reservations:
        for instance in reservation.instances:
            if instance.ip_address:
                pair = ('name: %s. size: %s. ip: %s' % (instance.tags.get(label_tag), instance.instance_type, instance.ip_address))
            else:
                pair = ('name: %s. size: %s. ip: %s' % (instance.tags.get(label_tag), instance.instance_type, instance.private_ip_address))

            instances.append(pair)
    return instances

tag = "Name"
filters = {}
instances = ec2_active_instances(tag, filters)

instance_completer = WordCompleter(instances, ignore_case=True)

def main():
    text = get_input('Pick an instance to ssh in: ', completer=instance_completer)
    subprocess.call(['ssh', text.split(' ')[-1]])

if __name__ == '__main__':
    main()
