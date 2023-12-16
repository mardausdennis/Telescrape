@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

ECHO Willkommen beim Telegram Scraper.

:: Bestimme den Pfad zum Verzeichnis des Scrapers
SET "SCRAPER_DIR=%~dp0channelscraper"

:: Überprüfen, ob das Setup bereits ausgeführt wurde
IF NOT EXIST venv (
    ECHO Setup wurde noch nicht ausgeführt. Starte Setup...
    CALL setup.bat
    IF %ERRORLEVEL% NEQ 0 (
        ECHO Fehler beim Ausführen von setup.bat.
        EXIT /B
    )
)

:: Überprüfen, welcher Python-Befehl verfügbar ist
python --version 2>NUL
IF NOT ERRORLEVEL 1 SET PYTHON_CMD=python
IF ERRORLEVEL 1 (
    python3 --version 2>NUL
    IF NOT ERRORLEVEL 1 SET PYTHON_CMD=python3
)
IF NOT DEFINED PYTHON_CMD (
    ECHO Weder Python noch Python3 ist verfügbar.
    EXIT /B
)

:: Aktivieren der virtuellen Umgebung
CALL venv\Scripts\activate
IF %ERRORLEVEL% NEQ 0 (
    ECHO Fehler beim Aktivieren der virtuellen Umgebung.
    EXIT /B
)

:: Wechsle in das Verzeichnis des Scrapers
CD /D "%SCRAPER_DIR%"

:: Verwalten der Channels mit Python-Skript
ECHO Führe manage_channels.py aus...
%PYTHON_CMD% manage_channels.py
IF %ERRORLEVEL% NEQ 0 (
    ECHO Fehler beim Ausführen von manage_channels.py.
    CALL venv\Scripts\deactivate
    EXIT /B
)

:: Benutzer fragen, welcher Modus gestartet werden soll
SET /P MODE=Wähle den Modus (Normal/Meta): 
IF /I "%MODE%"=="Meta" (
    ECHO Starte Meta-Daten Scraping...
    %PYTHON_CMD% scrapeChannelMetadata.py
) ELSE (
    ECHO Starte normalen Scraper...
    %PYTHON_CMD% app.py
)

:: Zurück zum ursprünglichen Verzeichnis
CD /D "%~dp0"

:: Deaktivieren der virtuellen Umgebung
CALL venv\Scripts\deactivate
ECHO Virtuelle Umgebung deaktiviert.

ECHO Vorgang abgeschlossen.
