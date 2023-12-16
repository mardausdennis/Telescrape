import csv
import os

def getInputPath():
    return os.path.join(os.path.dirname(__file__), '..', 'input')

def listChannels():
    try:
        with open(os.path.join(getInputPath(), 'channels.csv'), newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            channels = list(reader)
            if len(channels) <= 1:
                print("Es wurden noch keine Channels eingetragen.")
            else:
                print("Verfügbare Channels:")
                for row in channels[1:]:
                    print(f"- {row[1]} (@{row[3]})")
            addChannelPrompt()
    except FileNotFoundError:
        print("channels.csv Datei nicht gefunden. Erstellen einer neuen Datei.")
        addChannel()

def addChannelPrompt():
    user_input = input("Möchten Sie einen neuen Channel hinzufügen? (Ja/Nein): ").strip().lower()
    if user_input in ["ja", "j", "yes", "y"]:
        addChannel()

def addChannel():
    print("Bitte geben Sie die Channel-Daten ein:")
    kategorie = input("Kategorie: ")
    name = input("Name: ")
    link = input("Link: ")
    username = input("@: ")
    broadcast = input("Broadcast (TRUE/FALSE): ").strip().lower()

    # Konvertierung der Broadcast-Eingabe
    if broadcast in ["true", "1", "t"]:
        broadcast = "TRUE"
    elif broadcast in ["false", "0", "f"]:
        broadcast = "FALSE"
    else:
        print("Ungültige Eingabe für Broadcast. Standardmäßig auf TRUE gesetzt.")
        broadcast = "TRUE"

    with open(os.path.join(getInputPath(), 'channels.csv'), 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([kategorie, name, link, username, broadcast])

if __name__ == "__main__":
    listChannels()
