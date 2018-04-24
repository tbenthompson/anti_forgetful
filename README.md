# Never forget your AWS instances! 

`anti_forgetful` is a simple and handy tool for launch a single AWS instance from the terminal and tying it's lifetime to the lifetime of the process on your machine that launched it. This helps to avoid situations where you forget your instance and leave it running for a month. That could be thousands of dollars!

Please let me know if you have issues!

# Just tell me how to use it!

First, if you haven't used AWS before:

1) Set up your AWS account.
2) Follow the first two steps ("Install the AWS CLI" and "Configure the AWS CLI") [here](https://docs.aws.amazon.com/cli/latest/userguide/tutorial-ec2-ubuntu.html).

Next, install `anti_forgetful`:

```
pip install anti_forgetful
```

Now, check out the `example` folder for an example of how to launch a Jupyter notebook server. To start building your instance, move to that directory and run:

```
anti_forgetful awscfg
```

This tells the launcher to use `awscfg.py` as your configuration file and starts to build your instance. It'll take a few minutes on a free `t2.micro` instance. After a few

# So how do I write on of these configuration files!

The configuration is specified as a Python file: 

```python
# The name of the public/private key pair and the security group created for
# your instance. If this key already exists, it won't be recreated.
key_pair_name = 'tutorial_key_pair' 
group_name = 'tutorial_group'

# What instance type do you want? https://aws.amazon.com/ec2/instance-types/
instance_type = 't2.micro'

# This option turns off strict host checking in SSH. This can be handy if you
# aren't worried about security and want to avoid some manual interaction 
# launching your instance.
no_strict_host_checking = True

# The base image to build from. You probably shouldn't change this. 
base_image_id = 'ami-428aa838'

# The disk size requested from AWS EBS. In GB.
root_volume_size = 30  

# Your instance will be given a name so that it can be started and stopped!
# Two instances with the same name could get messy... You've been warned.
instance_name = 'tutorial_instance'

# This function is run once when your instance is built. Build your docker
# images here or install any packages you might want.
def setup_images(s):
    # Copy a file from the local machine to the instance. Accepts an optional
    # parameter "dest_filepath" for remote destination.
    s.copy_to_remote('docker-compose.yml')
    # Run a shell command on the remote instance.
    s.run_cmd('docker-compose pull')

# This function is run every time your instance boots up. 
def start_containers(s):
    # Forward a port from the remote machine to the local machine through an
    # ssh tunnel.
    s.ssh_port_forward(8888, 8888)
    # Star the docker containers!
    s.run_cmd('docker-compose up')
```

# Just in case you still need to terminate some instances.

The `awsterminate` command will list all the instances you currently have running and give you the option of terminating them. 

# Miscellaneous

At the moment, this is pretty completely integrated with Docker. That could easily be changed.

I've only tried this on Ubuntu with Python 3.5 and Python 3.6.
