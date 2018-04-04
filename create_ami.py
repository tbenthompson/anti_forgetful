from instance import SessionInstance
from util import handle_cfg

def main():
    cfg = handle_cfg()
    with SessionInstance(cfg, cfg.base_image_id) as s:
        install_docker(s)
        cfg.setup_images(s)
        s.save_to_image(cfg.image_name)

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
