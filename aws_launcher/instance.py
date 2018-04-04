import time
import boto3
from .util import handle_cfg, run

class SessionInstance:
    def __init__(self, cfg, image_id):
        self.cfg = cfg
        self.image_id = image_id

    def __enter__(self):
        self.ec2_resource = boto3.resource('ec2')
        self.instance = self.ec2_resource.create_instances(
            BlockDeviceMappings = [
                {"DeviceName": "/dev/xvda", "Ebs" : {
                    "VolumeSize": self.cfg.root_volume_size
                }}
            ],
            ImageId = self.image_id,
            MinCount = 1, MaxCount = 1,
            InstanceType = self.cfg.instance_type,
            SecurityGroups = [self.cfg.group_name],
            KeyName = self.cfg.key_pair_name
        )[0]
        try:
            print('Creating instance: ', self.instance.id)
            print('Waiting for instance to initialize')
            self.instance.wait_until_running()
            self.instance.reload()
            self.wait_until_ssh_accessible()
        except:
            self.instance.terminate()
            raise
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.instance.terminate()

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

    def wait_until_ssh_accessible(self):
        while self.run_cmd('echo "Checking if instance is up and running"') != 0:
            print('Retrying ssh')

    def ssh(self):
        pdns = self.instance.public_dns_name
        cmd = 'ssh -i %s.pem ec2-user@%s' % (self.cfg.key_pair_name, pdns)
        return run(cmd)

    def save_to_image(self, image_name):
        image = self.instance.create_image(
            Description = 'string',
            DryRun = False,
            Name = image_name,
            # If we don't reboot when making an image, pieces of the image
            # will be seriously broken. Files will just be missing, etc.
            NoReboot = False
        )

        # It is critical to wait for the image to be created before returning,
        # because otherwise the instance might be terminated while the image is
        # still being created. That results in a broken image
        print('Waiting for instance image to be created', end = '')
        while True:
            time.sleep(2)
            image.reload()
            print('.', end = '', flush = True)
            if image.state == 'available':
                break
        print('Created new image:', image.id)

if __name__ == "__main__":
    main()
