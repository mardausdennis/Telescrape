import sys
from datetime import datetime
from datetime import timedelta
import traceback
import logging
import os
import yaml
import csv
import asyncio

from utilities import getInputPath
from channel import Channel
from driver import Driver

# Argumente von der Kommandozeile lesen
selected_scrape_channel_ids = sys.argv[1:] 
selected_post_channel_ids = sys.argv[2:] 

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

# Konfiguration und Kanalliste laden
config = yaml.safe_load(open("config.yaml"))
post_file = config["post_channel_file"]
scrape_file = config["scrape_channel_file"]
scrape_channels = getChannelList(scrape_file, selected_scrape_channel_ids)
post_channels = getChannelList(post_file, selected_post_channel_ids)


for channel in scrape_channels:
    if Channel.config.get("scrape_type") == "CONTINUOUS_SCRAPE":
        try:
            target_group_ids = [post_channel.username for post_channel in post_channels]
            channel.continuousScrape(target_group_ids)
        except Exception as e:
            logging.error(f"Fehler beim kontinuierlichen Scraping: {e}")
    else:
        try:
            channel.processChannelMessages()
        except:
            traceback.print_exc()
            pass

        try:
            target_group_ids = [post_channel.username for post_channel in post_channels]
            channel.sendMessagesToGroupsAsync(target_group_ids, channel.messages)  # Verwende die neue Funktio
        except Exception as e:
            logging.error(f"Fehler beim Senden von Nachrichten an die Zielgruppen: {e}")

        try:
            channel.getChannelUsers()
        except:
            traceback.print_exc()
            pass

        try:
            channel.writeCsv()
        except:
            traceback.print_exc()
            pass

Driver.closeDriver()
