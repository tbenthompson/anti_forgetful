from instance import SessionInstance
from util import handle_cfg, get_image_id

def main():
    cfg = handle_cfg()
    image_id = get_image_id(cfg.image_name)
    with SessionInstance(cfg, image_id) as s:
        s.run_cmd('docker-compose up')

if __name__ == "__main__":
    main()
