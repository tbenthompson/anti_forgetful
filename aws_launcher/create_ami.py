import boto3
from botocore.exceptions import ClientError
from .instance import SessionInstance
from .util import handle_cfg

def main():
    cfg = handle_cfg()
    create_key_pair(cfg.key_pair_name)
    create_security_group(cfg.group_name)
    with SessionInstance(cfg, image_id = cfg.base_image_id) as s:
        s.ssh()
        # install_docker(s)
        # cfg.setup_images(s)
        # s.save_to_image(cfg.image_name)

def create_volume(cfg):
    ec2_resource = boto3.resource('ec2')
    ec2_client = boto3.client('ec2')
    response = ec2_client.describe_availability_zones()
    zone = response['AvailabilityZones'][0]['ZoneName']
    volume = ec2_resource.create_volume(
        AvailabilityZone = zone,
        Size = cfg.root_volume_size,
        VolumeType = 'gp2',
        TagSpecifications=[{
            'ResourceType': 'volume',
            'Tags': [{'Key': 'Name', 'Value': cfg.volume_name}]
        }]
    )
    pass

def create_key_pair(key_pair_name):
    try:
        ec2_resource = boto3.resource('ec2')
        response = ec2_resource.create_key_pair(KeyName = key_pair_name)
        assert(response.name == key_pair_name)
        filename = key_pair_name + '.pem'
        print('saving ' + key_pair_name + ' to ' + filename)
        open(filename, 'w').write(response.key_material)
    except ClientError as e:
        print('Key already exists')
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
            GroupId=security_group_id,
            IpPermissions=[
                {'IpProtocol': 'tcp',
                 'FromPort': 8888,
                 'ToPort': 8888,
                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                # {'IpProtocol': 'tcp',
                #  'FromPort': 80,
                #  'ToPort': 80,
                #  'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                {'IpProtocol': 'tcp',
                 'FromPort': 22,
                 'ToPort': 22,
                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
            ])
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
