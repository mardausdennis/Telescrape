@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

ECHO Willkommen beim Telegram Scraper Setup.

:: Überprüfen, ob Python installiert ist
python --version 2>NUL
IF NOT ERRORLEVEL 1 SET PYTHON_CMD=python
IF ERRORLEVEL 1 (
    python3 --version 2>NUL
    IF NOT ERRORLEVEL 1 SET PYTHON_CMD=python3
)
IF NOT DEFINED PYTHON_CMD (
    ECHO Weder Python noch Python3 gefunden. Bitte installiere Python.
    EXIT /B
)

:: Überprüfen und Installieren von pip
%PYTHON_CMD% -m ensurepip --upgrade
IF %ERRORLEVEL% NEQ 0 (
    ECHO pip konnte nicht automatisch installiert werden. Bitte installiere pip manuell.
    EXIT /B
)

:: Überprüfen, ob venv existiert und erstellen, falls notwendig
IF NOT EXIST venv (
    %PYTHON_CMD% -m venv venv
    ECHO Virtuelle Umgebung erstellt.
) ELSE (
    ECHO Virtuelle Umgebung existiert bereits.
)

:: Aktivieren der virtuellen Umgebung und Installieren der Abhängigkeiten
CALL venv\Scripts\activate
ECHO Virtuelle Umgebung aktiviert.

pip install -r requirements.txt
ECHO Installation abgeschlossen.

:: Überprüfen, ob config.yaml existiert und erstellen, falls notwendig
IF NOT EXIST channelscraper\config.yaml (
    COPY channelscraper\config.example.yaml channelscraper\config.yaml
    ECHO config.yaml erstellt.
)

:: Benutzereingaben für API-Schlüssel und Telefonnummer anfordern
ECHO Bitte gib deine Telegram API-Informationen ein.

:: Benutzereingaben für API-Schlüssel und Telefonnummer anfordern
:API_ID_INPUT
SET /P api_id=API ID (8 Ziffern): 
IF "!api_id!"=="" GOTO API_ID_INPUT
ECHO !api_id! | FINDSTR /R "^[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]\>" >nul
IF ERRORLEVEL 1 GOTO API_ID_INPUT

:API_HASH_INPUT
SET /P api_hash=API Hash (32 Zeichen): 
IF "!api_hash!"=="" GOTO API_HASH_INPUT
SET "api_hash_length=0"
FOR /L %%A IN (0,1,31) DO (
    SET "char=!api_hash:~%%A,1!"
    IF "!char!" NEQ "" SET /A "api_hash_length+=1"
)
IF !api_hash_length! NEQ 32 (
    GOTO API_HASH_INPUT
)
SET "hex_characters=0123456789ABCDEFabcdef"
FOR /L %%A IN (0,1,31) DO (
    SET "char=!api_hash:~%%A,1!"
    IF "!char!" NEQ "" (
        SET "char=!char:~0,1!"
        SET "char=!char^^!"
        IF "!hex_characters:%%char:=!" NEQ "!hex_characters!" (
            GOTO API_HASH_INPUT
        )
    )
)

:PHONE_INPUT
SET /P phone=Telefonnummer (inkl. Vorwahl, z.B. 0043): 
IF "!phone!"=="" GOTO PHONE_INPUT
IF "!phone:~0,1!"=="+" SET phone=00!phone:~1!
ECHO !phone! | FINDSTR /R "^[0-9][0-9]*" >nul
IF ERRORLEVEL 1 GOTO PHONE_INPUT
IF "!phone:~10,1!"=="" GOTO PHONE_INPUT


:: Aktualisieren der config.yaml Datei mit den Benutzereingaben
(
ECHO #### API CREDENTIALS #####
ECHO # Credentials for telegram API
ECHO api_id: !api_id!
ECHO api_hash: !api_hash!
ECHO phone: !phone!
ECHO ### Scrape/Input CHANNEL FILES ###
ECHO scrape_channel_file: scrape_channels.csv
ECHO ### Post/Output CHANNEL FILES ###
ECHO post_channel_file: post_channels.csv
ECHO ### SCRAPING SETTINGS ####
ECHO # More extensive logging if true.
ECHO debug_mode: false
ECHO # Specify scrape mode: FULL_SCRAPE vs. OFFSET_SCRAPE vs. LATEST_SCRAPE vs. CONTINUOUS_SCRAPE
ECHO scrape_type: CONTINUOUS_SCRAPE
ECHO # Relevant on OFFSET_SCRAPE, LATEST_SCRAPE and CONTINUOUS_SCRAPE when no last message yet mode. Set the amount of days to go back in chat history.
ECHO scrape_offset: 30
ECHO # There is a different driver needed for aws.
ECHO driver_mode: "normal"
ECHO # If true, the script will run slower in order to avoid being blocked.
ECHO init: False
ECHO # If true, media files will be downloaded as well. On default those are photos. If you want something different edit source-code.
ECHO media_download: False
ECHO # Query comments.bot/app usernames. Attention: This can lead to a API-ban more likely.
ECHO query_users: False
) > channelscraper\config.yaml

ECHO Konfiguration abgeschlossen. Du kannst nun den Telegram Scraper starten.
CALL venv\Scripts\deactivate
ECHO Virtuelle Umgebung deaktiviert.
