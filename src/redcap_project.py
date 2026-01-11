from __future__ import annotations

from typing import List, Optional, Dict
from pydantic import BaseModel
import xml.etree.ElementTree as ET


class RedcapArm(BaseModel):
    arm_id: Optional[int]
    arm_name: Optional[str]


class RedcapEvent(BaseModel):
    event_id: Optional[int]
    event_name: Optional[str]
    unique_event_name: Optional[str]
    arm_id: Optional[int]
    arm_name: Optional[str]


class RedcapRepeating(BaseModel):
    instrument: Optional[str]
    event_unique_names: List[str] = []


class RedcapProject(BaseModel):
    arms: List[RedcapArm] = []
    events: List[RedcapEvent] = []
    repeating: List[RedcapRepeating] = []


def _text(elem: ET.Element | None) -> Optional[str]:
    if elem is None:
        return None
    t = (elem.text or "").strip()
    return t or None


def _first_child_text(elem: ET.Element, names: List[str]) -> Optional[str]:
    names_lower = {n.lower() for n in names}
    for child in list(elem):
        if child.tag.lower() in names_lower:
            return _text(child)
    return None


def parse_project_xml(xml_path: str) -> RedcapProject:
    """
    Parse a REDCap Project XML (exported from Project Setup) to extract:
    - Arms (id, name)
    - Events (id, name, unique_event_name, arm association)
    - Repeating instruments configuration (instrument name and event unique names)

    The XML schema can vary across REDCap versions; this parser is defensive and
    tries multiple common tag names. If a section is not found, it's returned empty.
    """
    try:
        tree = ET.parse(xml_path)
    except Exception:
        # File missing or unreadable: return empty project structure
        return RedcapProject()

    root = tree.getroot()

    arms: List[RedcapArm] = []
    events: List[RedcapEvent] = []
    repeating: List[RedcapRepeating] = []

    # Arms: try typical containers like <arms> with children <arm>
    for arms_container in root.findall('.//arms') + root.findall('.//Arms'):
        for arm_elem in arms_container.findall('.//arm') + arms_container.findall('.//Arm'):
            arm_name = _first_child_text(arm_elem, ['name', 'arm_name'])
            arm_id_text = _first_child_text(arm_elem, ['id', 'arm_id'])
            try:
                arm_id = int(arm_id_text) if arm_id_text else None
            except ValueError:
                arm_id = None
            arms.append(RedcapArm(arm_id=arm_id, arm_name=arm_name))

    # Events: try typical containers like <events> with children <event>
    for events_container in root.findall('.//events') + root.findall('.//Events'):
        for ev_elem in events_container.findall('.//event') + events_container.findall('.//Event'):
            event_name = _first_child_text(ev_elem, ['name', 'event_name'])
            unique_event_name = _first_child_text(ev_elem, ['unique_name', 'unique_event_name'])
            arm_name = _first_child_text(ev_elem, ['arm_name'])
            arm_id_text = _first_child_text(ev_elem, ['arm_id'])
            event_id_text = _first_child_text(ev_elem, ['id', 'event_id'])
            try:
                arm_id = int(arm_id_text) if arm_id_text else None
            except ValueError:
                arm_id = None
            try:
                event_id = int(event_id_text) if event_id_text else None
            except ValueError:
                event_id = None
            events.append(
                RedcapEvent(
                    event_id=event_id,
                    event_name=event_name,
                    unique_event_name=unique_event_name,
                    arm_id=arm_id,
                    arm_name=arm_name,
                )
            )

    # Repeating instruments/events: look for common containers
    # Some REDCap exports use <repeatingFormsEvents> with items containing form name and event names
    for rep_container in (
        root.findall('.//repeatingFormsEvents')
        + root.findall('.//RepeatingFormsEvents')
        + root.findall('.//repeatingInstruments')
        + root.findall('.//RepeatingInstruments')
    ):
        for item in list(rep_container):
            # Try to read instrument/form name
            instr = _first_child_text(item, ['instrument', 'form', 'form_name'])
            # Collect event unique names from child list elements
            event_unique_names: List[str] = []
            for child in list(item):
                # tags like <eventUniqueName> or <unique_event_name>
                txt = _first_child_text(child, ['eventUniqueName', 'unique_event_name'])
                if not txt and child.tag.lower() in {'eventuniquename', 'unique_event_name'}:
                    txt = _text(child)
                if txt:
                    event_unique_names.append(txt)
            # If no nested children, try attributes/text directly
            if not event_unique_names:
                txt = _first_child_text(item, ['eventUniqueName', 'unique_event_name'])
                if txt:
                    event_unique_names.append(txt)
            repeating.append(RedcapRepeating(instrument=instr, event_unique_names=event_unique_names))

    return RedcapProject(arms=arms, events=events, repeating=repeating)


def summarize_project(project: RedcapProject) -> Dict[str, List[str]]:
    """Return a simple summary dictionary for quick inspection/logging."""
    return {
        'arms': [a.arm_name or f"arm_{a.arm_id}" for a in project.arms],
        'events': [e.unique_event_name or e.event_name or f"event_{e.event_id}" for e in project.events],
        'repeating_instruments': [r.instrument or 'unknown' for r in project.repeating],
    }
