# scrape.ps1

# Aktiviere die virtuelle Umgebung
.\venv\Scripts\activate

# Wechsle in das Verzeichnis channelscraper
cd .\channelscraper

# Führe app.py aus, oder scrapeChannelMetadata.py, wenn 'meta' als Argument übergeben wird
if ($args.Length -eq 0) {
    python app.py
} else {
    if ($args[0] -eq "meta") {
        python scrapeChannelMetadata.py
    }
}

# Deaktiviere die virtuelle Umgebung
Deactivate
