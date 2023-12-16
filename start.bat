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

:: Aktivieren der virtuellen Umgebung
CALL "%VENV_DIR%\Scripts\activate"
IF %ERRORLEVEL% NEQ 0 (
    ECHO Fehler beim Aktivieren der virtuellen Umgebung.
    EXIT /B
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


:: Aktuelle Konfiguration anzeigen und Benutzer fragen, ob er sie ändern möchte
ECHO Lese aktuelle Konfiguration...
CALL %PYTHON_CMD% %SCRAPER_DIR%\read_config.py %SCRAPER_DIR%

:: Einstellungen aktualisieren
SET /P UPDATE_SETTINGS="Möchtest du die Einstellungen ändern (Ja/Nein)? "
SET UPDATE_SETTINGS_LOWER=!UPDATE_SETTINGS:~0,1!
IF /I "!UPDATE_SETTINGS_LOWER!"=="j" (
    GOTO UPDATE_CONFIG
) ELSE IF /I "!UPDATE_SETTINGS_LOWER!"=="1" (
    GOTO UPDATE_CONFIG
) ELSE (
    GOTO END_UPDATE
)

:UPDATE_CONFIG
:: Modus aktualisieren
:MODUS_AKTUALISIEREN
SET /P MODE="Wähle den Modus (Normal/Meta) oder drücke Enter, um den aktuellen beizubehalten: "
SET MODE_LOWER=!MODE:~0,1!
IF "%MODE%"=="" GOTO SCRAPE_MODUS_AKTUALISIEREN
IF /I "!MODE_LOWER!"=="n" (
    CALL %PYTHON_CMD% %SCRAPER_DIR%\update_config.py %SCRAPER_DIR% mode normal
) ELSE IF /I "!MODE_LOWER!"=="m" (
    CALL %PYTHON_CMD% %SCRAPER_DIR%\update_config.py %SCRAPER_DIR% mode meta
) ELSE (
    ECHO Ungültige Eingabe. Bitte wähle entweder 'normal' oder 'meta'.
    GOTO MODUS_AKTUALISIEREN
)

:SCRAPE_MODUS_AKTUALISIEREN
:: Scrape-Modus aktualisieren
SET /P SCRAPE_MODE="Scrape-Modus wählen (Full/Offset) oder drücke Enter, um den aktuellen beizubehalten: "
SET SCRAPE_MODE_LOWER=!SCRAPE_MODE:~0,1!
IF "%SCRAPE_MODE%"=="" GOTO SHOW_UPDATED_CONFIG
IF /I "!SCRAPE_MODE_LOWER!"=="f" (
    CALL %PYTHON_CMD% %SCRAPER_DIR%\update_config.py %SCRAPER_DIR% full
) ELSE IF /I "!SCRAPE_MODE_LOWER!"=="o" (
    :OFFSET_EINGEBEN
    SET /P OFFSET_DAYS="Gib die Anzahl der Tage für den Offset ein (0-9999): "
    SET /A OFFSET_DAYS=1*!OFFSET_DAYS!
    IF "!OFFSET_DAYS!"=="" SET OFFSET_DAYS=9999
    IF !OFFSET_DAYS! LSS 0 SET OFFSET_DAYS=0
    IF !OFFSET_DAYS! GTR 9999 SET OFFSET_DAYS=9999
    CALL %PYTHON_CMD% %SCRAPER_DIR%\update_config.py %SCRAPER_DIR% offset !OFFSET_DAYS!
) ELSE (
    ECHO Ungültige Eingabe. Bitte wähle entweder 'Full' oder 'Offset'.
    GOTO SCRAPE_MODUS_AKTUALISIEREN
)

:SHOW_UPDATED_CONFIG
ECHO Aktualisierte Konfiguration...
CALL %PYTHON_CMD% %SCRAPER_DIR%\read_config.py %SCRAPER_DIR%

GOTO END_UPDATE

:END_UPDATE



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
