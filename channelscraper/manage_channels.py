import sys  
import csv
import os
import yaml

def read_config():
    with open('config.yaml', 'r') as file:
        return yaml.safe_load(file)

def getInputPath():
    return os.path.join(os.path.dirname(__file__), '..', 'input')

def listChannels():
    channels = []
    try:
        with open(os.path.join(getInputPath(), 'channels.csv'), newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  
            for index, row in enumerate(reader, start=1):
                channels.append(row)
                print(f"{index}. {row[1]} (@{row[3]})")
        if not channels:
            print("Keine Channels vorhanden. Fügen Sie einen neuen Channel hinzu.")
            addChannel()
            return listChannels() 
    except FileNotFoundError:
        print("channels.csv Datei nicht gefunden. Erstellen einer neuen Datei.")
        addChannel()
        return listChannels()  
    return channels

def selectChannel(channels):
    print("\nOptionen:")
    print("  [Nummer] Einen spezifischen Channel wählen.")
    print("  [a/all] Alle Channels wählen.")
    print("  [n/neu] Einen neuen Channel hinzufügen.")
    print("  [d/löschen] Einen Channel löschen.")
    user_input = input("Bitte wählen Sie eine Option: ").strip().lower()

    if user_input in ["n", "neu"]:
        addChannel()
        channels = listChannels()  
        return selectChannel(channels)  

    if user_input in ["d", "löschen"]:
        deleteChannel(channels)
        channels = listChannels()
        return selectChannel(channels)

    if user_input.isdigit():
        choice = int(user_input)
        if 1 <= choice <= len(channels):
            return [channels[choice - 1]]  

    if user_input in ["a", "all"]:
        return channels 

    print("Ungültige Eingabe. Alle Channels werden verwendet.")
    return channels  

def addChannel():
    print("Bitte geben Sie die Channel-Daten ein:")
    kategorie = input("Kategorie: ")
    name = input("Name: ")
    link = input("Link: ")
    username = input("@: ")
    broadcast = input("Broadcast (TRUE/FALSE): ").strip().lower()
    broadcast = "TRUE" if broadcast in ["true", "1", "t"] else "FALSE"
    with open(os.path.join(getInputPath(), 'channels.csv'), 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([kategorie, name, link, username, broadcast])

def deleteChannel(channels):
    print("Bitte geben Sie die ID des zu löschenden Channels ein:")
    try:
        channel_id = int(input("ID: "))
        if 1 <= channel_id <= len(channels):
            del channels[channel_id - 1]
            with open(os.path.join(getInputPath(), 'channels.csv'), 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                for channel in channels:
                    writer.writerow(channel)
            print("Channel gelöscht.")
        else:
            print("Ungültige Channel-ID.")
    except ValueError:
        print("Ungültige Eingabe. Bitte geben Sie eine Zahl ein.")

def runScraper(mode, selected_ids_str):
    if mode.lower() == 'meta':
        os.system(f'{sys.executable} scrapeChannelMetadata.py {selected_ids_str}')
    else:
        os.system(f'{sys.executable} app.py {selected_ids_str}')

def main():
    config = read_config()
    mode = config.get('mode', 'normal')  
    print("Verfügbare Channels:")
    channels = listChannels()  
    selected_channels = selectChannel(channels)  
    selected_ids = [str(index) for index, _ in enumerate(channels, start=1) if _ in selected_channels]
    selected_ids_str = ' '.join(selected_ids)

    runScraper(mode, selected_ids_str)

if __name__ == "__main__":
    main()
