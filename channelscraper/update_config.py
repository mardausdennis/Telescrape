import sys
import yaml

def update_config(scraper_dir, key, value):
    config_path = f"{scraper_dir}/config.yaml"
    with open(config_path) as file:
        config = yaml.safe_load(file)

    if key == 'mode':
        config['mode'] = value
    elif key == 'offset':
        config['scrape_mode'] = 'OFFSET_SCRAPE'
        config['scrape_offset'] = int(value)
    elif key == 'full':
        config['scrape_mode'] = 'FULL_SCRAPE'
    elif key == 'latest': 
        config['scrape_mode'] = 'LATEST_SCRAPE'

    with open(config_path, 'w') as file:
        yaml.dump(config, file)

if __name__ == "__main__":
    scraper_dir = sys.argv[1]
    key = sys.argv[2]
    value = sys.argv[3] if len(sys.argv) > 3 else None
    update_config(scraper_dir, key, value)
