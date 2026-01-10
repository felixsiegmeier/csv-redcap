import pandas as pd
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum
import re
from datetime import datetime

class FieldType(str, Enum):
    TEXT = "text"
    RADIO = "radio"
    CHECKBOX = "checkbox"
    DROPDOWN = "dropdown"
    CALC = "calc"
    YESNO = "yesno"
    NOTES = "notes"
    DESCRIPTIVE = "descriptive"

class DataDictionaryField(BaseModel):
    field_name: str
    form_name: str
    field_type: FieldType
    choices: Optional[Dict[str, int]]
    calculation: Optional[str]
    validation_type: Optional[str]
    validation_minimum: Optional[str | int | float]
    validation_maximum: Optional[str | int | float]
    identifier: Optional[bool]
    branching_logic: Optional[str]
    required_field: Optional[bool]

class DataDictionary(BaseModel):
    fields: List[DataDictionaryField]

    @classmethod
    # Parses a REDCap data dictionary CSV file into a DataDictionary instance
    def from_csv(cls, file_path: str) -> "DataDictionary":
        df = pd.read_csv(file_path, sep=None, engine='python', encoding='utf-8')
        df = df.where(pd.notna(df), None)
        
        # Find columns once
        def find_col(pattern: str) -> Optional[str]:
            for col in df.columns:
                if re.search(pattern, col, re.IGNORECASE):
                    return col
            return None
        
        field_name_col = find_col(r'.*field.*name|.*variable.*name')
        
        fields = []
        for _, row in df.iterrows():
            if not row.get(field_name_col):
                continue
                
            field = DataDictionaryField(
                field_name=row.get(field_name_col),
                form_name=row.get(find_col(r'.*form.*name')),
                field_type=row.get(find_col(r'.*field.*type')),
                choices=cls._parse_choices(row.get(find_col(r'.*choices.*calculations.*slider'))),
                calculation=cls._parse_calculation(row.get(find_col(r'.*choices.*calculations.*slider'))),
                validation_type=cls._parse_validataion_type(row.get(find_col(r'.*validation.*type.*slider'))),
                validation_minimum=cls._parse_validation_limit(row.get(find_col(r'.*validation.*min'))),
                validation_maximum=cls._parse_validation_limit(row.get(find_col(r'.*validation.*max'))),
                identifier=row.get(find_col(r'.*identifier')) == "y",
                branching_logic=row.get(find_col(r'.*branching.*logic')),
                required_field=row.get(find_col(r'.*required.*field')) == "y",
            )
            fields.append(field)
        return cls(fields=fields)

    @staticmethod
    # Parses choices if present in the format "1, Yes | 0, No"
    def _parse_choices(choices_str: str) -> Dict[str, int] | None:
        choices = {}
        if pd.isna(choices_str) or not str(choices_str).strip():
            return None
        try:
            for item in str(choices_str).split('|'):
                item = item.strip()
                if not item:
                    continue
                parts = item.split(',', 1)
                if len(parts) != 2:
                    continue
                value_str, label = parts
                value_str = value_str.strip()
                label = label.strip()
                # Skip calculated keys like {oak_spec_o}
                if re.match(r"^\{.*\}$", label):
                    continue
                try:
                    value = int(value_str)
                    choices[label] = value  # "BIPAP" -> 1
                except ValueError:
                    # value is not an integer, skip this entry
                    continue
        except Exception as e:
            print(f"Warning: Error parsing choices '{choices_str}': {e}")
            return None
        return choices or None
    
    @staticmethod
    # Parses calculation if present in the format "{field1} + {field2}"
    def _parse_calculation(calc_str: str) -> Optional[str]:
        if pd.isna(calc_str) or not str(calc_str).strip() or not re.match(r"^{.*}$", str(calc_str).strip()):
            return None
        return calc_str.strip() or None
    
    @staticmethod
    # Parses validation limits which can be int, float, or date
    def _parse_validation_limit(limit_str: str) -> Optional[str | int | float]:
        if pd.isna(limit_str) or not str(limit_str).strip():
            return None
        try:
            if re.match(r"\d+-\d+-\d+", limit_str):
                # Keep dates as ISO string for YAML serialization
                return limit_str
            if re.match(r"\d+[,\.]?\d*", limit_str):
                if not '.' in limit_str and not ',' in limit_str:
                    return int(limit_str)
                return float(limit_str.replace(',', '.'))
        except Exception as e:
            print(f"Warning: Error parsing validation limit '{limit_str}': {e}")
            return None
    
    @staticmethod
    # to be implemented next
    def _parse_validataion_type(val_type_str: str) -> Optional[str]:
        return val_type_str or None
    
    