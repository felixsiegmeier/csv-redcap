# START HERE — csv-redcap

Kurzüberblick, damit du in 2 Tagen schnell weitermachen kannst.

## Problem
- Für einen gültigen REDCap-Export fehlen aktuell Projekt-Metadaten: Arms/Events und Repeating-Konfiguration (`redcap_event_name`, `redcap_repeat_instrument`, `redcap_repeat_instance`).
- Diese Infos stehen nicht im Data Dictionary, sondern in der REDCap Project-XML (Export aus dem Project Setup).
- Die „assess_time_point“-Felder und deren Bedeutungen/Labels sind im Data Dictionary vorhanden, siehe [data/datadict.csv](data/datadict.csv).

## Zuletzt gemacht
- Parser-Skelett hinzugefügt: [src/redcap_project.py](src/redcap_project.py)
  - `parse_project_xml(path)`: Extrahiert Arms, Events (inkl. `unique_event_name`) und Repeating-Instrumente defensiv aus der Project-XML.
  - `summarize_project(project)`: Kurzübersicht für schnelle Prüfung.

## Deine nächsten Schritte
1. In REDCap die Project-XML exportieren (ohne Daten reicht):
   - Project Setup → Other Functionality → „Download the current project's XML file“
2. Datei speichern als [data/project.xml](data/project.xml).
3. Kurz prüfen, ob die Events/Arms erkannt werden:

```bash
# Mit uv (falls aktiv):
uv run python -c 'from src.redcap_project import parse_project_xml, summarize_project; print(summarize_project(parse_project_xml("data/project.xml")))'

# Alternativ direkt:
python -c 'from src.redcap_project import parse_project_xml, summarize_project; print(summarize_project(parse_project_xml("data/project.xml")))'
```

4. Wenn das passt, die Event-/Arm-Namen in den Templates/Transforms verwenden (z. B. `event_name`/`repeat_instrument` in [templates/example_template.yaml](templates/example_template.yaml) bzw. über [src/template.py](src/template.py)).
5. Optional: README-Ergänzung einbauen (Exportpfad/Beispielbefehle) und einen kleinen CLI-Checker schreiben.

## Notizen
- Systemfelder (`redcap_event_name`, `redcap_repeat_*`) kommen aus der Projektkonfiguration, nicht aus dem Data Dictionary.
- Die „assess_time_point“-Definitionen sind bereits in [data/datadict.csv](data/datadict.csv) enthalten (Dropdown mit Labels), d. h. ihre Bedeutungen sind abgedeckt.
- Sobald die XML vorliegt, kann der flexible Output vollständig generiert werden.

## TODO-Status (kurz)
- Parser-Skelett: vorhanden → siehe [src/redcap_project.py](src/redcap_project.py)
- Loader/README/Beispielscript: folgt nach XML-Export
