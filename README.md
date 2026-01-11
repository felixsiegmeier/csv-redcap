# csv-redcap

RedCap-Export-Helfer: mappt lokale CSV-Daten auf REDCap-kompatible Exporte unter Nutzung des Data Dictionary und der Projektkonfiguration.

**Aktueller Stand (11.01.2026)**
- Problem: REDCap-spezifische Felder (`redcap_event_name`, `redcap_repeat_instrument`, `redcap_repeat_instance`) stammen aus der Projektkonfiguration und fehlen ohne Project-XML.
- Neu: Parser-Skelett für die REDCap Project-XML in [src/redcap_project.py](src/redcap_project.py).
- Data Dictionary: vorhanden in [data/datadict.csv](data/datadict.csv); enthält u. a. `assess_time_point`-Definitionen mit Labels.
- Kurzanleitung zum Einstieg: siehe [STARTHERE.md](STARTHERE.md).

## Voraussetzungen
- Python-Umgebung aktiv (z. B. via `uv` oder `.venv`).
- Data Dictionary CSV: [data/datadict.csv](data/datadict.csv).
- Projekt-XML (ohne Daten reicht): [data/project.xml](data/project.xml) — muss aus REDCap exportiert werden.

## REDCap Project-XML beschaffen
Exportiere die Project-XML in REDCap:
- Project Setup → Other Functionality → „Download the current project's XML file“
- Speichere die Datei als [data/project.xml](data/project.xml)

Schnelltest des Parsers:

```bash
uv run python -c 'from src.redcap_project import parse_project_xml, summarize_project; print(summarize_project(parse_project_xml("data/project.xml")))'
```

Erwartet wird eine Übersicht über Arms, Events (`unique_event_name`) und Repeating-Instrumente.

## Templates & Mapping
- Beispiel-Template: [templates/example_template.yaml](templates/example_template.yaml)
- Template-Modell und Felder: [src/template.py](src/template.py)
- Data Dictionary Loader: [src/datadict.py](src/datadict.py)
- Transform-Strukturen (Zielzeilen): [src/transform.py](src/transform.py)

## App starten
### Desktop
```bash
uv run flet run
```

### Web
```bash
uv run flet run --web
```

Weitere Details: Flet [Getting Started Guide](https://docs.flet.dev/).

## Build (optional)
### Android
```bash
flet build apk -v
```
Mehr dazu: Flet [Android Packaging Guide](https://docs.flet.dev/publish/android/).

### iOS
```bash
flet build ipa -v
```
Mehr dazu: Flet [iOS Packaging Guide](https://docs.flet.dev/publish/ios/).

### macOS
```bash
flet build macos -v
```
Mehr dazu: Flet [macOS Packaging Guide](https://docs.flet.dev/publish/macos/).

### Linux
```bash
flet build linux -v
```
Mehr dazu: Flet [Linux Packaging Guide](https://docs.flet.dev/publish/linux/).

### Windows
```bash
flet build windows -v
```
Mehr dazu: Flet [Windows Packaging Guide](https://docs.flet.dev/publish/windows/).