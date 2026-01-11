import yaml
from pydantic import BaseModel
from typing import List, Optional, Dict
from enum import Enum
from pathlib import Path

from .datadict import DataDictionaryField, DataDictionary

# Simplified mapping: store semantic selectors and key columns directly

class AggregationMethod(str, Enum):
    FIRST = "first"
    LAST = "last"
    MEAN = "mean" # average value
    MEDIAN = "median" # middle value
    MIN = "min"
    MAX = "max"
    MODE = "mode" # most frequent value
    SUM = "sum"
    NEAREST = "nearest" # closest to reference timepoint

class ReferenceMode(str, Enum):
    CALENDAR_DAY = "calendar_day"
    FROM_TIMEPOINT = "from_timepoint"


class SourceMapping(BaseModel):
    """
    Defines how to extract a value and its timestamp from source data.
    Used both for main field mapping and for calculation variables.
    """
    query_string: Optional[str] = None     # pandas-compatible query to filter data 
    query_value: Optional[str] = None      # column name to read after query
    timestamp: Optional[str] = None        # timestamp column name
    constant: Optional[str] = None         # fixed value OR reference to another variable like "{weight}" (takes precedence over query)


class TemplateField(DataDictionaryField):
    """
    Extends DataDictionaryField with mapping logic for data processing.
    Contains both REDCap metadata and source data mapping information.
    """
    visible: Optional[bool] = True  # Whether to include this field in the aggregated output

    # REDCap structure (field-specific)
    event_name: Optional[str] = None  # Column name or fixed value
    repeat_instrument: Optional[str] = None  # For repeating instruments
    repeat_instance: Optional[str] = None  # Column name for instance number
    
    # Query-based mapping (simple & robust)
    source: Optional[SourceMapping] = None  # how to extract value and timestamp from data
    
    # Optional calculation based on intermediate variables
    # Note: 'calculation' field (inherited from DataDictionaryField) is REDCap's built-in calculation
    # 'calculation_expr' is a user-defined expression for deriving field values from source data
    use_calculation: Optional[bool] = False  # Whether this field uses a user-defined calculation
    calculation_expr: Optional[str] = None  # user-defined calc, e.g. "({dose_ml_h} / {kg} / 60) * {conc_mg_ml} * 1000"
    calc_vars: Optional[Dict[str, SourceMapping]] = None  # var name -> SourceMapping (with optional constant)
 
    # Aggregation/time settings
    aggregation: Optional[AggregationMethod] = None # How to aggregate multiple source values
    time_interval: Optional[int] = None  # e.g., 1, 4, 24 (hours)
    reference: Optional[ReferenceMode] = None # How to interpret time intervals
    reference_column: Optional[str] = None # Column name for reference timepoint
    outlier_filter: Optional[float] = None  # Percentile for outlier removal

class Template(BaseModel):
    """
    Complete template for mapping source data to REDCap format.
    Contains all necessary REDCap metadata and mapping logic.
    """
    version: str = "1.0"
    name: str
    datadict_hash: Optional[str] = None  # For validation against original DataDict
    
    # Global settings
    record_id_column: str = "record_id"  # Column name for patient/record ID
    arm: Optional[str] = None  # Fixed arm or null for runtime selection
    
    fields: List[TemplateField]
    
    @classmethod
    def from_yaml(cls, file_path: str) -> "Template":
        """Load template from YAML file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return cls(**data)
    
    def to_yaml(self, file_path: str) -> None:
        """Save template to YAML file"""
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(
                self.model_dump(exclude_none=True, mode='python'),
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False
            )
    
    @classmethod
    def from_datadict(cls, datadict: DataDictionary, name: str) -> "Template":
        """
        Create a new template from a DataDictionary.
        All fields will need mapping configuration added.
        """
        fields = [
            TemplateField(**field.model_dump())
            for field in datadict.fields
        ]
        
        return cls(
            name=name,
            record_id_column="record_id",
            fields=fields
        )
