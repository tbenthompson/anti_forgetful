key_pair_name = 'tutorial_key_pair'
group_name = 'tutorial_group'
instance_type = 't2.micro'
# https://serverfault.com/questions/132970/can-i-automatically-add-a-new-host-to-known-hosts
no_strict_host_checking = True

#create_ami options
base_image_id = 'ami-428aa838'
root_volume_size = 30 # In GB
image_name = 'myimage'

def setup_images(s):
    s.copy_to_remote('docker-compose.yml')
    s.run_cmd('docker-compose pull')
