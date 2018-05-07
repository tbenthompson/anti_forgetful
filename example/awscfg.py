key_pair_name = 'tutorial_key_pair'
group_name = 'tutorial_group'
instance_type = 't2.micro'
region = 'us-east-2'
no_strict_host_checking = True

base_image_id = 'ami-428aa838'
root_volume_size = 30 # In GB
instance_name = 'tutorial_instance'

def setup_images(s):
    s.copy_to_remote('docker-compose.yml')
    s.run_cmd('docker-compose pull')

def start_containers(s):
    s.ssh_port_forward(8888, 8888)
    s.run_cmd('docker-compose up')
