import pandas as pd
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum
import re
from datetime import datetime

def date_homogenizer(date_str: str) -> Optional[datetime]:
    """
    Converts various date string formats into a standardized datetime object.
    Returns None if the input is invalid or cannot be parsed.
    """
    if not date_str or not isinstance(date_str, str):
        return None

    date_formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%m-%d-%Y",
        "%Y.%m.%d",
        "%d.%m.%Y",
        "%m.%d.%Y",
    ]

    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    return None

def datetime_homogenizer(datetime_str: str) -> Optional[datetime]:
    """
    Converts various datetime string formats into a standardized datetime object.
    Returns None if the input is invalid or cannot be parsed.
    """
    if not datetime_str or not isinstance(datetime_str, str):
        return None

    datetime_formats = [
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%d-%m-%Y %H:%M:%S",
        "%m-%d-%Y %H:%M:%S",
        "%Y.%m.%d %H:%M:%S",
        "%d.%m.%Y %H:%M:%S",
        "%m.%d.%Y %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%d/%m/%Y %H:%M",
        "%m/%d/%Y %H:%M",
        "%Y/%m/%d %H:%M",
        "%d-%m-%Y %H:%M",
        "%m-%d-%Y %H:%M",
        "%Y.%m.%d %H:%M",
        "%d.%m.%Y %H:%M",
        "%m.%d.%Y %H:%M",
    ]

    for fmt in datetime_formats:
        try:
            return datetime.strptime(datetime_str, fmt)
        except ValueError:
            continue

    return None
