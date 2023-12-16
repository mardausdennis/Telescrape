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
selected_channel_ids = sys.argv[1:]  # Erstes Element überspringen, da es den Skriptnamen enthält

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
input_file = config["input_channel_file"]
channels = getChannelList(input_file, selected_channel_ids)


for channel in channels:
    channelPath = getInputPath() + "/" + channel.username
    logging.info("Collecting channel: " + channel.username)
    logging.info("-> Collecting messages")
    # Scrape Channels
    try:
        channel.scrape()
    except:
        traceback.print_exc()
        pass

    try:
        channel.getChannelUsers()
    except:
        traceback.print_exc()
        pass

    # WriteCsv
    try:
        channel.writeCsv()
    except:
        traceback.print_exc()
        pass

Driver.closeDriver()
