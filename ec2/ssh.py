#!/usr/bin/env python
from __future__ import unicode_literals

from prompt_toolkit import AbortAction
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.completion import Completion
from prompt_toolkit.filters import Always
from prompt_toolkit.history import History
from prompt_toolkit.shortcuts import get_input

import os
import boto.ec2
import subprocess
import netaddr
import collections

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
            instance_key = '%s (%s)' % (instance.tags.get(label_tag), instance.instance_type)
            instances[instance_key] = instance.id

    return collections.OrderedDict(sorted(instances.items()))

from tabulate import tabulate
def get_instance_info(instance_id):
    ec2_instance = get_ec2_instance()
    reservations =  ec2_instance.get_all_instances([instance_id])

    instance = reservations[0].instances[0]

    # only return a handful of useful fields
    return [['Private IP', instance.private_ip_address], ['Public IP', instance.ip_address], ['Host name', instance.public_dns_name],
            ['Type', instance.instance_type], ['State', instance.state], ['Architecture', instance.architecture], ['AZ', instance.placement]]

def cli():
    tag = "Name"
    filters = {}
    instances = ec2_active_instances(tag, filters)

    instance_ips = [item for sublist in instances.values() for item in sublist]

    instance_completer = WordCompleter(instances.keys(), meta_dict=instances, match_middle=True, WORD=True, ignore_case=True)
    history = History()

    selecting_instance = True

    supported_commands = ['ssh', 'info']

    while selecting_instance:
        try:
            input = get_input('Pick an instance: ', completer=instance_completer, history=history,
                           on_abort=AbortAction.RETRY,
                           enable_system_bindings=Always())

            command = ''
            hostname = input
            if input.find(' ') >= 0:
                input_parts = input.split(' ')

                if input_parts[0].lower() in supported_commands:
                    hostname = ' '.join(input_parts[1:])
                    command = input_parts[0].lower()

            instance_id = instances[hostname]
            instance_info = get_instance_info(instance_id)

            if command.startswith('info'):
                print tabulate(instance_info)
            else:
                # Always try with public ip
                if instance_info[1][1]:
                    ip = instance_info[1][1]
                else:
                    ip = instance_info[0][1]
                if netaddr.valid_ipv4(ip) == True:
                    subprocess.call(['ssh', ip])
                    selecting_instance = False
                else:
                    print 'Invalid IP: %s' % ip
        except EOFError:
             break  # Control-D pressed.

if __name__ == '__main__':
    cli()
