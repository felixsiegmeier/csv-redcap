import pandas as pd
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Tuple
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

class ValidationType(str, Enum):
    INTEGER = "integer"
    NUMBER = "number"
    NUMBER_1DP = "number_1dp"
    NUMBER_2DP = "number_2dp"
    DATE_DMY = "date_dmy"
    DATETIME_DMY = "datetime_dmy"
    TIME = "time"
    ALPHA_ONLY = "alpha_only"

class DataDictionaryField(BaseModel):
    field_name: str
    form_name: str
    field_type: FieldType
    field_label: Optional[str]
    choices: Optional[Dict[str, int]]
    calculation: Optional[str]
    validation_type: Optional[ValidationType]
    validation_minimum: Optional[str | int | float]
    validation_maximum: Optional[str | int | float]
    identifier: Optional[bool]
    branching_logic: Optional[List[Dict[str, Any]]]
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
                field_label=row.get(find_col(r'.*field.*label')),
                field_type=row.get(find_col(r'.*field.*type')),
                choices=cls._parse_choices(row.get(find_col(r'.*choices.*calculations.*slider'))),
                calculation=cls._parse_calculation(row.get(find_col(r'.*choices.*calculations.*slider'))),
                validation_type=cls._parse_validataion_type(row.get(find_col(r'.*validation.*type.*slider'))),
                validation_minimum=cls._parse_validation_limit(row.get(find_col(r'.*validation.*min'))),
                validation_maximum=cls._parse_validation_limit(row.get(find_col(r'.*validation.*max'))),
                identifier=row.get(find_col(r'.*identifier')) == "y", # "y" indicates true
                branching_logic=cls._parse_branching_logic(row.get(find_col(r'.*branching.*logic'))),
                required_field=row.get(find_col(r'.*required.*field')) == "y", # "y" indicates true
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
    # Parses validation type from string to ValidationType enum
    def _parse_validataion_type(val_type_str: str) -> Optional[str]:
        if pd.isna(val_type_str) or not str(val_type_str).strip():
            return None
        val_type_str = val_type_str.strip().lower()
        mapping = {
            "integer": ValidationType.INTEGER,
            "number": ValidationType.NUMBER,
            "number_1dp": ValidationType.NUMBER_1DP,
            "number_2dp": ValidationType.NUMBER_2DP,
            "date_dmy": ValidationType.DATE_DMY,
            "datetime_dmy": ValidationType.DATETIME_DMY,
            "time": ValidationType.TIME,
            "alpha_only": ValidationType.ALPHA_ONLY,
        }
        return mapping.get(val_type_str, None)
    

    @staticmethod
    # Parses branching logic into a list of condition dictionaries
    def _parse_branching_logic(logic_str: str) -> Optional[List[Dict[str, Any]]]:
        if pd.isna(logic_str) or not str(logic_str).strip():
            return None
        
        logic_str = str(logic_str).strip()
        conditions = []
        
        # Match: [field_name] operator 'value' or [field_name(123)] >= value
        # Operators: =, <, >, <=, >=, <>
        pattern = r"\[([a-zA-Z_][a-zA-Z0-9_]*(?:\(\d+\))?)\]\s*([=<>!]+)\s*['\"]?([^'\"<>=\[\]]+)['\"]?"
        
        for match in re.finditer(pattern, logic_str):
            field_name, operator, value = match.groups()
            value = value.strip()
            
            try:
                value = int(value)
            except ValueError:
                pass
            
            conditions.append({
                "field": field_name,
                "operator": operator,
                "value": value
            })
        
        return conditions or None