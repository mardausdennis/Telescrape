import sys
import time
import traceback
import logging
import os
import yaml
import csv

from utilities import getInputPath
from channel import Channel
from driver import Driver

def getChannelList(filename, selected_ids=None):
    """Initialises the CSV of channels to scrape given by ADDENDUM."""
    channelList = []
    with open(getInputPath() + '/' + filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Kopfzeile überspringen
        for index, row in enumerate(reader, start=1):
            if not selected_ids or str(index) in selected_ids:
                channelList.append(Channel(row[2], row[4]))
    return channelList

# Argumente von der Kommandozeile lesen und Listen initialisieren
mode = sys.argv[1]
selected_scrape_channel_ids = sys.argv[2:]
selected_post_channel_ids = sys.argv[3:]
config = yaml.safe_load(open("config.yaml"))
scrape_file = config["scrape_channel_file"]
post_file = config["post_channel_file"]
scrape_channels = getChannelList(scrape_file, selected_scrape_channel_ids)
post_channels = getChannelList(post_file, selected_post_channel_ids)

# Überprüfen, ob der Modus auf "CONTINUOUS_SCRAPE" gesetzt ist
if Channel.config.get("scrape_type") == "CONTINUOUS_SCRAPE":
    while True:
        for channel in scrape_channels:
            send_messages = mode.lower() == 'scrapeandsend'
            try:
                target_group_ids = [post_channel.username for post_channel in post_channels]
                channel.continuousScrape(target_group_ids, send_messages)
            except Exception as e:
                logging.error(f"Fehler beim kontinuierlichen Scraping: {e}")

        time.sleep(10)  # Pause für 10 Sekunden

else:
    for channel in scrape_channels:
        try:
            channel.processChannelMessages()
            if mode.lower() == 'scrapeandsend':
                target_group_ids = [post_channel.username for post_channel in post_channels]
                channel.sendMessagesToGroupsAsync(target_group_ids, channel.messages)
            channel.getChannelUsers()
            channel.writeCsv()
        except Exception as e:
            logging.error(f"Fehler bei der Verarbeitung des Channels: {e}")
            traceback.print_exc()

# Schließen Sie den Driver, wenn die Verarbeitung beendet wird
Driver.closeDriver()
