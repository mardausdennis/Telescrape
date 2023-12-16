import sys  
import csv
import os

def getInputPath():
    return os.path.join(os.path.dirname(__file__), '..', 'input')

def listChannels():
    channels = []
    try:
        with open(os.path.join(getInputPath(), 'channels.csv'), newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Kopfzeile überspringen
            for index, row in enumerate(reader, start=1):
                channels.append(row)
                print(f"{index}. {row[1]} (@{row[3]})")
        if not channels:
            print("Keine Channels vorhanden. Fügen Sie einen neuen Channel hinzu.")
            addChannel()
            return listChannels()  # Aktualisierte Liste nach dem Hinzufügen zurückgeben
    except FileNotFoundError:
        print("channels.csv Datei nicht gefunden. Erstellen einer neuen Datei.")
        addChannel()
        return listChannels()  # Aktualisierte Liste nach dem Erstellen zurückgeben
    return channels

def selectChannel(channels):
    print("\nOptionen:")
    print("  [Nummer] Einen spezifischen Channel wählen.")
    print("  [a/all] Alle Channels wählen.")
    print("  [n/neu] Einen neuen Channel hinzufügen.")
    user_input = input("Bitte wählen Sie eine Option: ").strip().lower()

    if user_input in ["n", "neu"]:
        addChannel()
        channels = listChannels()  # Kanäle erneut auflisten
        return selectChannel(channels)  # Auswahl erneut anzeigen

    if user_input.isdigit():
        choice = int(user_input)
        if 1 <= choice <= len(channels):
            return [channels[choice - 1]]  # Einzelne Auswahl

    if user_input in ["a", "all"]:
        return channels  # Alle auswählen

    print("Ungültige Eingabe. Alle Channels werden verwendet.")
    return channels  # Standardmäßig alle verwenden

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

def runScraper(mode, selected_ids_str):
    if mode.lower() == 'meta':
        os.system(f'{sys.executable} scrapeChannelMetadata.py {selected_ids_str}')
    else:
        os.system(f'{sys.executable} app.py {selected_ids_str}')

def main(mode):
    print("Verfügbare Channels:")
    channels = listChannels()  # Kanäle auflisten
    selected_channels = selectChannel(channels)  # Auswahl treffen
    selected_ids = [str(index) for index, _ in enumerate(channels, start=1) if _ in selected_channels]
    selected_ids_str = ' '.join(selected_ids)

    # Den Scraper mit den ausgewählten IDs und Modus als Argumente ausführen
    runScraper(mode, selected_ids_str)

if __name__ == "__main__":
    mode = sys.argv[1]  # Der Modus wird als erstes Argument übergeben
    main(mode)
