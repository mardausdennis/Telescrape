import asyncio
import csv
import logging
import os
import time
import traceback
import glob

from datetime import datetime

import telethon.tl.types.messages
from bots import Bots
from client import Client
from config import Config
from message import Message
from utilities import concat, wait, calcDateOffset, getOutputPath, create_path_if_not_exists, extractUrls


class Channel:
    config = Config.getConfig()
    client = Client.getClient()
    logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                        level=logging.INFO)

    def __init__(self, link, isBroadcastingChannel):
        self.id = None

        self.users = list()
        if isBroadcastingChannel == "True":
            self.isBroadcastingChannel = True
        else:
            self.isBroadcastingChannel = False
        self.username = link.rsplit('/', 1)[-1]

        self.path = getOutputPath() + "/" + self.username
        self.messages = list()

    def processChannelMessages(self):
        create_path_if_not_exists(self.path)

        if Channel.config.get("scrape_type") == "OFFSET_SCRAPE":
            self.getRecentChannelMessages()
        elif Channel.config.get("scrape_type") == "FULL_SCRAPE":
            self.getAllChannelMessages()
        elif Channel.config.get("scrape_type") == "LATEST_SCRAPE":
            self.getLatestChannelMessages()
        else:
            raise AttributeError("Invalid scraping mode set in config file.")

    async def sendMessagesToGroups(self, group_ids, messages_to_send):
        """ Sendet Nachrichten an mehrere spezifizierte Gruppen. """
        async with Channel.client:
            for group_id in group_ids:
                for message in messages_to_send:  # Verwende die übergebene Nachrichtenliste
                    try:
                        if message.media and os.path.exists(f"{self.path}/media/{message.id}.jpg"):
                            media_path = f"{self.path}/media/{message.id}.jpg"
                            await Channel.client.send_file(group_id, media_path, caption=message.text)
                        elif message.text:
                            await Channel.client.send_message(group_id, message.text)
                    except Exception as e:
                        logging.error(f"Fehler beim Senden der Nachricht/Medien an Gruppe {group_id}: {e}")

    def sendMessagesToGroupsAsync(self, group_ids, messages_to_send):
        """ Führt die asynchrone sendMessagesToGroups Funktion aus, sendet Nachrichten in umgekehrter Reihenfolge. """
        loop = asyncio.get_event_loop()
        reversed_messages = list(reversed(messages_to_send)) 
        loop.run_until_complete(self.sendMessagesToGroups(group_ids, reversed_messages))



    def continuousScrape(self, target_group_ids):
        """ Continuously scrapes new messages and sends them to target groups. """
        last_timestamp, last_content = self.getLastMessageInfo()
        first_run = True

        if last_timestamp is None:
            self.getRecentChannelMessages()
            self.writeCsv(append=False)  # Erstelle eine neue CSV-Datei
            last_timestamp, last_content = self.getLastMessageInfo()  # Aktualisiere die Werte
            first_run = False  # Nach getRecentChannelMessages ist es nicht mehr der erste Durchlauf

        async def fetchMessages():
            nonlocal last_timestamp, last_content, first_run
            while True:
                new_messages = []  # Speichert neue Nachrichten

                async for message in Channel.client.iter_messages(self.username, offset_date=last_timestamp, reverse=True):
                    if isinstance(message, telethon.tl.types.Message):
                        message_time = message.date.replace(tzinfo=None)
                        if last_timestamp is None or (message_time > last_timestamp or (message_time == last_timestamp and message.text != last_content)):
                            await self.parseMessage(message)
                            new_messages.append(message)
                            last_timestamp, last_content = message_time, message.text

                if new_messages:
                    self.writeCsv(append=not first_run)
                    if first_run:
                        first_run = False

                    # Sendet die neuen Nachrichten an die Zielgruppen
                    await self.sendMessagesToGroups(target_group_ids, new_messages)

                await asyncio.sleep(10)  # Warte 10 Sekunden

        with Channel.client:
            try:
                Channel.client.loop.run_until_complete(fetchMessages())
            except Exception as e:
                logging.error(f"Error during continuous scrape: {e}")



    # Collects LATEST messages and comments from a given channel.
    def getLatestChannelMessages(self):
        """ Scrapes messages of a channel since the last saved message and saves the information in the channel object.
        """

        async def main():
            last_timestamp, last_content = self.getLastMessageInfo()

            if last_timestamp is None:
                await self.getRecentChannelMessages()
                return

            if last_timestamp:
                async for message in Channel.client.iter_messages(self.username, offset_date=last_timestamp, reverse=True):
                    if type(message) == telethon.tl.types.Message:
                        message_time = message.date.replace(tzinfo=None)
                        if message_time > last_timestamp or (message_time == last_timestamp and message.text != last_content):
                            await self.parseMessage(message)

        with Channel.client:
            try:
                Channel.client.loop.run_until_complete(main())
            except telethon.errors.ServerError:
                logging.info("Server error: Passed")
                pass
            except telethon.errors.FloodWaitError as e:
                logging.info("FloodWaitError: Sleep for " + str(e.seconds))
                time.sleep(e.seconds)

        self.messages = list(reversed(self.messages))



    # Collects messages and comments from a given channel with OFFSET.
    def getRecentChannelMessages(self):
        """ Scrapes messages of a channel of the last X days and saves the information in the channel object.
        """

        async def main():
            async for message in Channel.client.iter_messages(self.username, offset_date=calcDateOffset(
                    Channel.config.get("scrape_offset")), reverse=True):
                if type(message) == telethon.tl.types.Message:
                    await self.parseMessage(message)

        with Channel.client:
            try:
                Channel.client.loop.run_until_complete(main())
            except telethon.errors.ServerError:
                logging.info("Server error: Passed")
                pass
            except telethon.errors.FloodWaitError as e:
                logging.info("FloodWaitError: Sleep for " + str(e.seconds))
                time.sleep(e.seconds)

        self.messages = list(reversed(self.messages))

    # Collects ALL messages and comments from a given channel.
    def getAllChannelMessages(self):
        """ Scrapes all messages of a channel and saves the information in the channel object.
        """

        async def main():
            async for message in Channel.client.iter_messages(self.username):
                if type(message) == telethon.tl.types.Message:
                    await self.parseMessage(message)

        with Channel.client:
            try:
                Channel.client.loop.run_until_complete(main())
            except telethon.errors.ServerError:
                logging.info("Server error: Passed")
                pass
            except telethon.errors.FloodWaitError as e:
                logging.info("FloodWaitError: Sleep for " + str(e.seconds))
                time.sleep(e.seconds)


    def getLastMessageInfo(self):
        try:
            # Finde die neueste CSV-Datei, die mit "chatlogs" beginnt
            list_of_files = glob.glob(self.path + '/chatlogs*.csv')

            if not list_of_files:
                raise FileNotFoundError("Keine CSV-Datei gefunden")

            latest_file = max(list_of_files, key=os.path.getctime)

            # Lese den Timestamp und Inhalt aus der letzten Zeile der neuesten CSV-Datei
            with open(latest_file, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                last_line = None
                for line in csv_reader:
                    last_line = line
                if last_line:
                    last_timestamp_str = last_line["timestamp"]
                    if '+' in last_timestamp_str:
                        last_timestamp_str = last_timestamp_str.split('+')[0]
                    last_timestamp = datetime.strptime(last_timestamp_str, '%Y-%m-%d %H:%M:%S')
                    last_content = last_line["content"]
                    return last_timestamp, last_content
        except FileNotFoundError:
            logging.info("Keine CSV-Datei bzw. LastMessage gefunden. Hole alle Nachrichten der letzten " + str(Channel.config.get("scrape_offset")) + " Tage zuerst.")
        except Exception as e:
            logging.error(f"Fehler beim Lesen der letzten Nachrichteninformationen: {e}")

        return None, None



    async def parseMessage(self, message):
        # Wait to prevent getting blocked
        await wait()

        new_message = Message()
        new_message.id = message.id
        new_message.sender = message.sender_id
        try:
            first_name = message.sender.first_name
            last_name = message.sender.last_name
        except AttributeError:
            first_name = ""
            last_name = ""
        new_message.sender_name = concat(first_name, last_name)
        try:
            new_message.username = message.sender.username
        except AttributeError:
            pass
        new_message.replyToMessageId = message.reply_to_msg_id
        new_message.edit_date = message.edit_date
        new_message.entities = message.entities
        new_message.post_author = message.post_author
        new_message.timestamp = message.date
        new_message.text = message.text
        new_message.views = message.views
        new_message.media = type(message.media)
        self.member_count = message.chat.participants_count

        # Saves the channel from which the message was forwarded.
        try:
            await self.__parseForward(message, new_message)
        except AttributeError:
            pass

        if type(message.media) == telethon.types.MessageMediaPhoto and Channel.config.get("media_download"):
            mediapath = self.path + "/media/" + str(new_message.id)
            if not os.path.exists(mediapath + ".jpg"):
                try:
                    await message.download_media(mediapath)
                except telethon.errors.FloodWaitError as e:
                    logging.info("Waiting " + str(e.seconds) + " seconds: FloodWaitError")
                    await asyncio.sleep(e.seconds)
                except telethon.errors.RpcCallFailError:
                    pass
                await asyncio.sleep(1)

        # Checks which kind of comment bot is used by the provider of the group a uses the correct scraper.
        #   --> then fills the comment list for each messages with the comments (prints "no comments" if no comment
        #   bot is used.
        comments = list()
        if message.buttons is not None and message.forward is None:
            buttons = message.buttons

            for button in buttons:
                button_url = None
                try:
                    button_url = button[0].button.url[:21]
                except AttributeError:
                    pass

                if button_url == 'https://comments.bot/':
                    logging.info("---> Found comments.bot...")
                    new_message.hasComments = True
                    new_message.bot_url = button[0].button.url
                    try:
                        comments.extend(Bots.scrapeCommentsBot(new_message.bot_url, self.users, message.id))
                    except Exception:
                        traceback.print_exc()
                elif button[0].text[-8:] == 'comments':
                    logging.info("---> Found comments.app...")
                    new_message.hasComments = True
                    new_message.bot_url = button[0].button.url
                    try:
                        commentsAppComments, commentsAppUsers = \
                            await Bots.scrapeCommentsApp(new_message.bot_url, message.id,
                                                         Channel.config.get("query_users"))
                        comments.extend(commentsAppComments)
                        self.users.extend(commentsAppUsers)
                    except Exception:
                        traceback.print_exc()

            new_message.comments = comments
        self.messages.append(new_message)


    def writeCsv(self, append=False):
        # Basispfad für die Dateien
        chatlogs_base = self.path + "/chatlogs_"
        users_base = self.path + "/users_"

        if append:
            # Liste alle Dateien im Verzeichnis auf, die dem Muster entsprechen
            chatlogs_files = glob.glob(chatlogs_base + "*.csv")
            users_files = glob.glob(users_base + "*.csv")

            # Wähle die neuesten Dateien, falls vorhanden
            chatlogs_csv = max(chatlogs_files, key=os.path.getctime, default=None)
            users_csv = max(users_files, key=os.path.getctime, default=None)

            # Erstelle neue Dateien, falls keine vorhanden sind
            if chatlogs_csv is None or users_csv is None:
                append = False

        if not append:
            # Erstelle neue Dateien mit Zeitstempel im Namen
            current_time_str = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
            chatlogs_csv = chatlogs_base + current_time_str + ".csv"
            users_csv = users_base + current_time_str + ".csv"

        # Schreiben der Nachrichten in chatlogs_csv
        with open(chatlogs_csv, "a" if append else "w", encoding="utf-8", newline='') as chatFile:
            writer = csv.writer(chatFile)
            if not append:  # Schreibe Kopfzeile nur beim ersten Mal
                writer.writerow(Message.getMessageHeader())

            # Kehre die Reihenfolge der Nachrichten um, bevor sie geschrieben werden
            for message in reversed(self.messages):
                message.urls = extractUrls(message)
                writer.writerow(message.getMessageRow(self.username, self.member_count, self.isBroadcastingChannel))
                for comment in message.comments:
                    comment.urls = extractUrls(comment)
                    writer.writerow(comment.getMessageRow(self.username, self.member_count, self.isBroadcastingChannel))

        # Schreiben der Benutzerinformationen in users_csv
        with open(users_csv, "a" if append else "w", encoding="utf-8", newline='') as usersFile:
            writer = csv.writer(usersFile)
            if not append:  # Schreibe Kopfzeile nur beim ersten Mal
                writer.writerow(Message.getUserHeader())
            for user in reversed(self.users):
                writer.writerow([self.username, user.id, user.first_name, user.last_name, concat(user.first_name, user.last_name), user.phone, user.bot, user.verified, user.username])

        # Leeren der Nachrichten- und Benutzerlisten nach dem Schreiben
        self.messages.clear()
        self.users.clear()



    async def __parseForward(self, message, new_message):
        if message.forward is not None:
            if message.forward.chat is not None:
                new_message.forward = message.forward.chat.username
                new_message.forwardId = message.forward.chat.id
                if new_message.forwardId is None:
                    new_message.forwardId = message.forward.channel_id
            elif message.forward.sender is not None:
                sender = message.forward.sender
                new_message.forward = concat(sender.first_name, sender.last_name)
                new_message.forwardId = sender.id
            else:
                new_message.forward = "Unknown"
                new_message.forwardId = "Unknown"

            if message.forward.original_fwd is not None:
                new_message.forward_msg_id = message.forward.original_fwd.channel_post
                new_message.forward_msg_date = message.forward.date

    def getChannelUsers(self):
        """ Scrape the users of a channel, if it is not a broadcasting channel."""
        if self.isBroadcastingChannel:
            return

        async def main():
            async for user in Channel.client.iter_participants(self.username, aggressive=True):
                if type(user) == telethon.types.User:
                    if user not in self.users:
                        self.users.append(user)

        with Channel.client:
            try:
                Channel.client.loop.run_until_complete(main())
            except telethon.errors.FloodWaitError as e:
                print("FloodWaitError: Sleep for " + str(e.seconds))
                time.sleep(e.seconds)
