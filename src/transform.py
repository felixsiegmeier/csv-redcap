from pydantic import BaseModel
from typing import List, Dict, Any

class DataEntry(BaseModel):
    timestamp: str
    value: Any

class DataRow(BaseModel):
    field_name: str
    record_id: str
    redcap_event_name: str
    redcap_repeat_instrument: str
    redcap_repeat_instance: int
    entries: List[DataEntry]