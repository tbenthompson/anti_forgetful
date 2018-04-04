import os
import argparse
import boto3

def main():
    parser = argparse.ArgumentParser(description = 'Terminate all active AWS EC2 instances.')
    args = parser.parse_args()

    ec2_resource = boto3.resource('ec2')
    # instances = ec2_resource.instances.filter(Filters=[{
    #     'Name': 'instance-state-name',
    #     'Values': ['running', 'pending', 'initializing']
    # }])
    instances = ec2_resource.instances.all()
    print('Planning to terminate:')
    print_instances(instances)
    if input('confirm (y,N): ') == 'y':
        print('Terminating')
        instances.terminate()

def print_instances(instances):
    os.system("aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,PublicIpAddress,State.Name]' --output table")

# def print_instances(instances):
#     for i in instances:
#         if i.id in get_statuses(ec2_resource):
#             ip = i.public_ip_address
#             pdns = i.public_dns_name
#             print(i.id, i.instance_type, ip, pdns)

if __name__ == "__main__":
    main()
