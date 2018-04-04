from instance import SessionInstance
from util import handle_cfg, get_image_id
from create_ami import install_docker

def main():
    cfg = handle_cfg()
    with SessionInstance(cfg, cfg.base_image_id) as s:
        install_docker(s)
        s.copy_to_remote('docker-compose.yml')
        s.ssh()
        # s.run_cmd('docker-compose up')

if __name__ == "__main__":
    main()
