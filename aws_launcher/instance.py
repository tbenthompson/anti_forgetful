import time
import boto3
from .util import handle_cfg, run

class SessionInstance:
    def __init__(self, cfg, instance_id = None, image_id = None):
        self.cfg = cfg
        self.image_id = image_id
        self.instance_id = instance_id

    def __enter__(self):
        self.ec2_resource = boto3.resource('ec2')
        if self.instance_id is None:
            self.create_instance()
            print('Creating instance: ', self.instance.id)
        else:
            self.start_instance()
            print('Starting instance: ', self.instance.id)
        try:
            print('Waiting for instance to boot up')
            self.instance.wait_until_running()
            self.instance.reload()
            self.wait_until_ssh_accessible()
        except:
            self.__exit__(None, None, None)
            raise
        return self

    def create_instance(self):
        self.instance = self.ec2_resource.create_instances(
            BlockDeviceMappings = [
                {
                    "DeviceName": "/dev/xvda",
                    "Ebs" : {
                        "VolumeSize": self.cfg.root_volume_size
                    }
                }
            ],
            ImageId = self.image_id,
            MinCount = 1, MaxCount = 1,
            InstanceType = self.cfg.instance_type,
            SecurityGroups = [self.cfg.group_name],
            KeyName = self.cfg.key_pair_name,
            TagSpecifications=[{
                'ResourceType': 'instance',
                'Tags': [{'Key': 'Name', 'Value': self.cfg.instance_name}]
            }],
        )[0]

    def start_instance(self):
        self.instance = self.ec2_resource.Instance(self.instance_id)
        if self.instance.state['Name'] == 'stopping':
            print('Instance is currently stopping. Waiting until it is stopped to restart.')
            self.instance.wait_until_stopped()
            self.instance.reload()
        self.instance.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('Stopping instance...')
        self.instance.stop()

    def run_cmd(self, remote_cmd):
        pdns = self.instance.public_dns_name
        base_ssh = ['ssh']
        # https://serverfault.com/questions/132970/can-i-automatically-add-a-new-host-to-known-hosts
        if self.cfg.no_strict_host_checking:
            base_ssh += ['-o', 'StrictHostKeyChecking=no']
        return run(' '.join(
            base_ssh + [
                '-t', '-i', '%s.pem' % self.cfg.key_pair_name,
                'ec2-user@%s' % pdns,
                '"%s"' % remote_cmd
            ]
        ))

    def copy_to_remote(self, filepath, dest_filepath = '~/'):
        pdns = self.instance.public_dns_name
        run(' '.join([
            'scp', '-r', '-i', '%s.pem' % self.cfg.key_pair_name,
            filepath, 'ec2-user@%s:%s' % (pdns, dest_filepath)
        ]))

    def ssh_port_forward(self, local_port, remote_port):
        pdns = self.instance.public_dns_name
        run(' '.join([
            'ssh', '-i', '%s.pem' % self.cfg.key_pair_name,
            '-L', '%s:localhost:%s' % (local_port, remote_port),
            'ec2-user@%s' % pdns,
            '-f', '-N'
        ]))


    def wait_until_ssh_accessible(self):
        while self.run_cmd('echo "Checking if instance is up and running"') != 0:
            print('Retrying ssh')

    def ssh(self):
        pdns = self.instance.public_dns_name
        cmd = 'ssh -i %s.pem ec2-user@%s' % (self.cfg.key_pair_name, pdns)
        return run(cmd)

if __name__ == "__main__":
    main()
