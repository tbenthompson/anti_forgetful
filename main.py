import os
import time
import boto3
import subprocess
from botocore.exceptions import ClientError

# Cobbled together from boto3 docs.
# https://boto3.readthedocs.io/en/latest/guide/migrationec2.html#launching-new-instances
# https://gist.github.com/dastergon/b4994c605f76d528d0c4

ec2_client = boto3.client('ec2')

def get_statuses():
    response = ec2_resource.meta.client.describe_instance_status()
    return {
        v['InstanceId']:v
        for v in response['InstanceStatuses']
    }

def count_instances(states):
    instances = ec2_resource.instances.filter(Filters=[{
        'Name': 'instance-state-name',
        'Values': states
    }])

    n_instances = sum([1 for i in instances])
    return n_instances

def count_launched_instances():
    return count_instances(['running', 'pending', 'initializing'])

def count_running_instances():
    return count_instances(['running'])

def list_running_instances():
    print('listing running instances')
    for instance in ec2_resource.instances.all():
        if instance.id in get_statuses():
            ip = instance.public_ip_address
            pdns = instance.public_dns_name
            print(instance.id, instance.instance_type, ip, pdns)

def get_first_running_instance():
    for instance in ec2_resource.instances.all():
        if instance.id in get_statuses():
            return instance
    return None

def ssh(inst):
    if inst is None:
        print('fail')
    else:
        pdns = inst.public_dns_name
        os.system('ssh -i %s.pem ec2-user@%s' % (key_pair_name, pdns))

def run(cmd):
    print('running', cmd)
    subprocess.run(cmd, shell = True)

def run_remote_cmd(instance, remote_cmd):
    pdns = instance.public_dns_name
    run(' '.join([
        'ssh', '-t', '-i', '%s.pem' % key_pair_name,
        'ec2-user@%s' % pdns,
        '"%s"' % remote_cmd
    ]))

def copy_to_remote(instance, filepath, dest_filepath = '~/'):
    pdns = instance.public_dns_name
    run(' '.join([
        'scp', '-i', '%s.pem' % key_pair_name,
        filepath,
        'ec2-user@%s:%s' % (pdns, dest_filepath)
    ]))

def setup_docker():
    # This could be nice to do with ansible instead.
    # Following:
    # https://docs.aws.amazon.com/AmazonECS/latest/developerguide/docker-basics.html#install_docker
    # https://docs.docker.com/compose/install/#install-compose
    cmds = [
        'sudo yum update -y',
        'sudo yum install -y docker',
        'sudo service docker start',
        'sudo usermod -a -G docker ec2-user',
        'docker info',
        'sudo curl -L https://github.com/docker/compose/releases/download/1.20.1/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose',
        'sudo chmod +x /usr/local/bin/docker-compose',
        'docker-compose --version'
    ]
    inst = get_first_running_instance()
    for c in cmds:
        run_remote_cmd(inst, c)

def main():
    if count_launched_instances() == 0:
        print('no running instances')
        create_instance()
        print('waiting for instance to initialize', end = '', flush = True)
        while count_running_instances() == 0:
            print('.', end = '', flush = True)
            time.sleep(2.0)
        print('')
        setup_docker()

    list_running_instances()
    print('')

    inst = get_first_running_instance()
    # copy_to_remote(inst, 'docker-compose.yml')
    # run_remote_cmd(inst, 'docker-compose up')
    ssh(inst)

if __name__ == "__main__":
    main()
