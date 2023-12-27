import sys  
import csv
import os
import yaml

def read_config():
    with open('config.yaml', 'r') as file:
        return yaml.safe_load(file)

def getInputPath():
    return os.path.join(os.path.dirname(__file__), '..', 'input')

def listChannels(channel_file, channel_type):
    channels = []
    try:
        with open(os.path.join(getInputPath(), channel_file), newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader, None)  # Sicherstellen, dass eine Header-Zeile vorhanden ist
            if not header:
                raise ValueError(f"Die Datei {channel_file} hat keinen Header.")
            for index, row in enumerate(reader, start=1):
                if len(row) < 4:  # Überprüfen, ob genügend Spalten vorhanden sind
                    continue
                channels.append(row)
                print(f"{index}. {row[1]} (@{row[3]})")
        if not channels:
            print(f"Keine {channel_type}-Channels vorhanden. Fügen Sie einen neuen Channel hinzu.")
            addChannel(channel_file, channel_type)
            return listChannels(channel_file, channel_type)
    except FileNotFoundError:
        print(f"{channel_file} Datei nicht gefunden. Erstellen einer neuen Datei mit Header.")
        header = ["Kategorie", "Name", "Link", "@", "Broadcast"]
        file_path = os.path.join(getInputPath(), channel_file)
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
        return listChannels(channel_file, channel_type)  # Liste aktualisieren und zurückgeben
    except ValueError as e:
        print(e)
        return []
    return channels


def addChannel(channel_file, channel_type):
    print(f"Bitte geben Sie die Daten für den {channel_type}-Channel ein:")
    kategorie = input("Kategorie: ")
    name = input("Name: ")
    link = input("Link: ")
    username = input("@: ")
    broadcast = input("Broadcast (TRUE/FALSE): ").strip().lower()
    broadcast = "TRUE" if broadcast in ["true", "1", "t"] else "FALSE"
    with open(os.path.join(getInputPath(), channel_file), 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([kategorie, name, link, username, broadcast])

def selectChannel(channels, channel_type):
    print("\nOptionen für " + channel_type + "-Channels:")
    print("  [Nummer] Einen spezifischen Channel wählen.")
    print("  [a/all] Alle Channels wählen.")
    print("  [n/neu] Einen neuen Channel hinzufügen.")
    print("  [d/löschen] Einen Channel löschen.")

    # Bestimme den Dateinamen basierend auf dem channel_type
    channel_file = 'post_channels.csv' if channel_type == 'Post' else 'scrape_channels.csv'

    user_input = input("Bitte wählen Sie eine Option: ").strip().lower()

    if user_input in ["n", "neu"]:
        addChannel(channel_file, channel_type)
        channels = listChannels(channel_file, channel_type)
        return selectChannel(channels, channel_type)

    if user_input in ["d", "löschen"]:
        deleteChannel(channels, channel_file, channel_type)
        channels = listChannels(channel_file, channel_type)
        return selectChannel(channels, channel_type)

    if user_input.isdigit():
        choice = int(user_input)
        if 1 <= choice <= len(channels):
            return [channels[choice - 1]]

    if user_input in ["a", "all"]:
        return channels

    print("Ungültige Eingabe. Alle Channels werden verwendet.")
    return channels


def deleteChannel(channels, channel_file, channel_type):
    print(f"Bitte geben Sie die ID des zu löschenden {channel_type}-Channels ein:")
    try:
        channel_id = int(input("ID: "))
        if 1 <= channel_id <= len(channels):
            del channels[channel_id - 1]
            with open(os.path.join(getInputPath(), channel_file), 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                for channel in channels:
                    writer.writerow(channel)
            print(f"{channel_type}-Channel gelöscht.")
        else:
            print("Ungültige Channel-ID.")
    except ValueError:
        print("Ungültige Eingabe. Bitte geben Sie eine Zahl ein.")


def runScraper(mode, selected_scrape_ids_str, selected_post_ids_str):
    if mode.lower() == 'scrape':
        os.system(f'{sys.executable} app.py scrape {selected_scrape_ids_str} {selected_post_ids_str}')
    elif mode.lower() == 'scrapeandsend':
        os.system(f'{sys.executable} app.py scrapeandsend {selected_scrape_ids_str} {selected_post_ids_str}')
    elif mode.lower() == 'meta':
        os.system(f'{sys.executable} scrapeChannelMetadata.py {selected_scrape_ids_str} {selected_post_ids_str}')
    else:
        print(f"Unbekannter Modus: {mode}")


def main():
    config = read_config()
    mode = config.get('mode', 'normal')

    print("Verfügbare Scrape-Channels:")
    scrape_channels = listChannels('scrape_channels.csv', 'Scrape')
    selected_scrape_channels = selectChannel(scrape_channels, 'Scrape')
    selected_scrape_ids = [str(index) for index, _ in enumerate(scrape_channels, start=1) if _ in selected_scrape_channels]

    print("\nVerfügbare Post-Channels:")
    post_channels = listChannels('post_channels.csv', 'Post')
    selected_post_channels = selectChannel(post_channels, 'Post')
    selected_post_ids = [str(index) for index, _ in enumerate(post_channels, start=1) if _ in selected_post_channels]

    selected_scrape_ids_str = ' '.join(selected_scrape_ids)
    selected_post_ids_str = ' '.join(selected_post_ids)

    runScraper(mode, selected_scrape_ids_str, selected_post_ids_str)

if __name__ == "__main__":
    main()
