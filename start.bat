@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

ECHO Willkommen beim Telegram Scraper.

:: Bestimme den Pfad zum Verzeichnis des Scrapers
SET "SCRAPER_DIR=%~dp0channelscraper"
SET "VENV_DIR=%~dp0venv"

:: Überprüfen, ob das Setup bereits ausgeführt wurde
IF NOT EXIST "%VENV_DIR%" (
    ECHO Setup wurde noch nicht ausgeführt. Starte Setup...
    CALL "%~dp0setup.bat"
    IF %ERRORLEVEL% NEQ 0 (
        ECHO Fehler beim Ausführen von setup.bat.
        EXIT /B
    )
)

:: Überprüfen, welcher Python-Befehl verfügbar ist
python --version >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    SET "PYTHON_CMD=python"
) ELSE (
    python3 --version >nul 2>&1
    IF %ERRORLEVEL% EQU 0 (
        SET "PYTHON_CMD=python3"
    ) ELSE (
        ECHO Weder Python noch Python3 ist verfügbar.
        EXIT /B
    )
)

:: Benutzer fragen, welcher Modus gestartet werden soll
SET /P MODE="Wähle den Modus (Normal/Meta): "
IF "%MODE%"=="" SET MODE=Normal
IF /I NOT "%MODE%"=="Meta" SET MODE=Normal

:: Aktivieren der virtuellen Umgebung
CALL "%VENV_DIR%\Scripts\activate"
IF %ERRORLEVEL% NEQ 0 (
    ECHO Fehler beim Aktivieren der virtuellen Umgebung.
    EXIT /B
)

:: Wechsle in das Verzeichnis des Scrapers
CD /D "%SCRAPER_DIR%"

:: Verwalten der Channels mit Python-Skript
ECHO Führe manage_channels.py aus...
%PYTHON_CMD% manage_channels.py %MODE%
IF %ERRORLEVEL% NEQ 0 (
    ECHO Fehler beim Ausführen von manage_channels.py.
    CALL "%VENV_DIR%\Scripts\deactivate"
    CD /D "%~dp0"
    EXIT /B
)

:: Zurück zum ursprünglichen Verzeichnis
CD /D "%~dp0"

:: Deaktivieren der virtuellen Umgebung
CALL "%VENV_DIR%\Scripts\deactivate"
ECHO Virtuelle Umgebung deaktiviert.

ECHO Vorgang abgeschlossen.
