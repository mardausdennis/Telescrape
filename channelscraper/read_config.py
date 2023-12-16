import sys
import yaml

def read_config(scraper_dir):
    config_path = f"{scraper_dir}/config.yaml"
    with open(config_path) as file:
        config = yaml.safe_load(file)

    print(f"Aktueller Modus: {config.get('mode', 'Normal')}")
    print(f"Aktueller Scrape-Modus: {config.get('scrape_mode', 'FULL_SCRAPE')}")
    if 'scrape_offset' in config:
        print(f"Aktueller Scrape-Offset: {config['scrape_offset']} Tage")

if __name__ == "__main__":
    scraper_dir = sys.argv[1]
    read_config(scraper_dir)
