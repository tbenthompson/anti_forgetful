import argparse
import boto3
from botocore.exceptions import ClientError
from cfg_handler import handle_cfg

def main():
    cfg = handle_cfg()
    create_key_pair(cfg.key_pair_name)
    create_security_group(cfg.group_name)

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

if __name__ == "__main__":
    main()
