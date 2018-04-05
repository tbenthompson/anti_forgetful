import boto3
from botocore.exceptions import ClientError
from .instance import SessionInstance
from .util import handle_cfg

def main():
    cfg = handle_cfg()
    instance_id = get_instance_id(cfg)
    if instance_id is None:
        instance_id = setup_instance(cfg)
    with SessionInstance(cfg, instance_id = instance_id) as s:
        s.run_cmd('sudo service docker start')
        cfg.start_containers(s)

def get_instance_id(cfg):
    ec2_resource = boto3.resource('ec2')
    for i in ec2_resource.instances.all():
        if i.tags == None:
            continue
        for t in i.tags:
            if t['Key'] != 'Name':
                continue
            if t['Value'] != cfg.instance_name:
                continue
            if i.state['Name'] == 'terminated':
                continue
            return i.id
    return None

def setup_instance(cfg):
    create_key_pair(cfg.key_pair_name)
    create_security_group(cfg.group_name)
    with SessionInstance(cfg, image_id = cfg.base_image_id) as s:
        install_docker(s)
        cfg.setup_images(s)
        return s.instance.id

def create_key_pair(key_pair_name):
    try:
        ec2_resource = boto3.resource('ec2')
        response = ec2_resource.create_key_pair(KeyName = key_pair_name)
        assert(response.name == key_pair_name)
        filename = key_pair_name + '.pem'
        print('saving ' + key_pair_name + ' to ' + filename)
        open(filename, 'w').write(response.key_material)
    except ClientError as e:
        print(e)

def create_security_group(group_name):
    ec2_client = boto3.client('ec2')
    response = ec2_client.describe_vpcs()
    vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')

    try:
        response = ec2_client.create_security_group(
            GroupName = group_name,
            Description = 'tutorial security group',
            VpcId = vpc_id
        )
        security_group_id = response['GroupId']
        print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))

        data = ec2_client.authorize_security_group_ingress(
            GroupId = security_group_id,
            IpPermissions = [{
                'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            }]
        )
        print('Ingress Successfully Set %s' % data)
    except ClientError as e:
        print(e)

def install_docker(s):
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
    for c in cmds:
        s.run_cmd(c)

if __name__ == "__main__":
    main()
