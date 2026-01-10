# REDCap Import-Tool – Architecture Reference

> This file provides GitHub Copilot (and human developers) with a complete overview of the project.
> Place in `docs/ARCHITECTURE.md` or project root.

## 1. Project Purpose

A desktop tool (Flet UI) to transform clinical time-series data (CSV, long format) into REDCap-compatible import files.

**Two-phase workflow:**
1. **Template Builder** – Create a reusable mapping template (DataDict → source columns, aggregation, calculations)
2. **Data Processor** – Apply template to a dataset and export REDCap-ready CSV

---

## 2. Directory Structure

```
redcap-import-tool/
├── app.py                  # Flet entry point
├── pyproject.toml          # Dependencies (uv/pip)
├── .gitignore
├── README.md
│
├── src/                    # Backend logic
│   ├── __init__.py
│   ├── logger.py           # Logging setup (console + file)
│   ├── datadict.py         # Parse REDCap DataDict CSV
│   ├── template.py         # Load/save/validate YAML templates (Pydantic)
│   ├── aggregation.py      # Time-based aggregation engine
│   ├── calculation.py      # Safe expression evaluator (simpleeval)
│   ├── validation.py       # Data type & value validation
│   ├── export.py           # Generate REDCap CSV
│   └── utils.py            # Date parsing, converters, helpers
│
├── ui/                     # Flet UI components
│   ├── __init__.py
│   ├── template_builder.py # Wizard for template creation
│   ├── data_processor.py   # Apply template & export
│   ├── components.py       # Reusable widgets (upload, dropdown, table)
│   └── styles.py           # Colors, typography, spacing
│
├── tests/                  # pytest unit tests
│   ├── test_datadict.py
│   ├── test_template.py
│   ├── test_aggregation.py
│   ├── test_calculation.py
│   ├── test_export.py
│   └── test_validation.py
│
├── notebooks/              # Interactive development & testing
│   ├── 01_datadict_exploration.ipynb
│   ├── 02_aggregation_testing.ipynb
│   ├── 03_export_validation.ipynb
│   └── 04_end_to_end_test.ipynb
│
├── templates/              # Example YAML templates
│   ├── vitals_template.yaml
│   └── ecmo_template.yaml
│
├── data/                   # Git-ignored, local test data
│   ├── input/
│   └── output/
│
└── docs/
    ├── ARCHITECTURE.md     # ← This file
    ├── konzept.md
    ├── calculation_examples.md
    └── screenshots/
```

## 3. Module Responsibilities

| Module | Purpose |
|--------|----------|
| `datadict.py` | Parse REDCap DataDict CSV; extract field types, choice codes, required fields, date formats, checkbox columns, key columns (record_id, redcap_event_name, etc.) |
| `template.py` | Pydantic models for YAML template schema; load/save/validate templates |
| `aggregation.py` | Group data by time intervals (1h–24h); support calendar-day and from-timepoint references; methods: first, last, mean, min, max, median, mode, sum, nearest |
| `calculation.py` | Evaluate Python-like expressions safely via `simpleeval`; variable syntax `{var}` → `row['var']`; handle NULL values |
| `validation.py` | Validate data types (int, float, date, text), value ranges, choice codes, date formats, required fields |
| `export.py` | Generate REDCap CSV with correct key columns; auto-set `redcap_repeat_instrument`; number `redcap_repeat_instance` per patient starting at 1; convert dates to DD/MM/YYYY (Australian format) |
| `utils.py` | Flexible date parser, type converters, string cleaners, user-friendly error messages |

---

## 4. Template Schema (YAML)

```yaml
# Example: templates/vitals_template.yaml
version: "1.0"
name: "Vitals Template"
datadict_hash: "abc123..."  # For validation
arm: "arm_1"                 # Optional: fixed arm or null for runtime selection
overwrite_strategy: "merge"  # merge | replace

key_mapping:
  record_id: patient_id_column
  redcap_event_name: event_column  # Or fixed value

parameter_mapping:
  rr_sys:
    source: rr_systolisch
    time_interval: 1h           # null | 1h | 2h | 4h | 6h | 8h | 12h | 24h
    reference: calendar_day     # calendar_day | from_timepoint
    reference_column: null      # Required if from_timepoint
    aggregation: mean           # first | last | mean | min | max | median | mode | sum | nearest
    outlier_filter: null        # null | 2.5 | 5 | 10 (percentile)
  
  nora_dosis:
    type: calculated
    formula: "({laufrate_ml_h} / {gewicht_kg} / 60) * {konz_mg_ml} * 1000"
    source_params: [laufrate_ml_h, gewicht_kg, konz_mg_ml]
    aggregation: mean
  
  geschlecht:
    source: sex
    choice_mapping:
      "m": 1
      "männlich": 1
      "w": 2
      "weiblich": 2
```

---

## 5. REDCap Key Columns

| Column | Description |
|--------|-------------|
| `record_id` | Unique patient identifier |
| `redcap_event_name` | Event + arm (e.g., `baseline_arm_1`, `day1_arm_2`) |
| `redcap_repeat_instrument` | Instrument name for repeating forms |
| `redcap_repeat_instance` | Instance number (starts at 1 per patient per instrument) |

## 6. Aggregation Reference

| Method | Use Case |
|--------|-----------|
| `first` | First recorded value in window |
| `last` | Most recent value |
| `mean` | Average (vitals, doses) |
| `median` | Robust average (outlier-resistant) |
| `min` / `max` | Extreme values |
| `mode` | Most frequent (categorical data) |
| `sum` | Cumulative (volumes, doses over time) |
| `nearest` | Closest to reference timepoint (from_timepoint only) |

**Reference modes:**
- `calendar_day`: Aggregate by calendar day (00:00–23:59)
- `from_timepoint`: Aggregate relative to event (e.g., ECMO start, ICU admission)

---

## 7. Calculation Syntax

```python
# Variables: {column_name}
# Arithmetic: + - * /
# Comparison: == != > < >= <=
# Logic: and or not
# Conditional: value if condition else alternative

# Examples:
{laufrate_ml_h} / {gewicht_kg} / 60 * 1000
1 if {vasopressor_dose} > 0 else 0
{'P1': 0, 'P2': 1, 'P3': 2}.get({impella_level}, None)
```

---

## 8. Non-Importable Field Types

These REDCap field types are automatically disabled:
- `calc` (calculated fields)
- `descriptive` (labels/instructions)
- `file` (file uploads)
- `signature` (signature fields)

---

## 9. Development Phases

| Phase | Goal | Dependencies |
|-------|------|---------------|
| 0 | Setup & infrastructure | – |
| 1 | DataDict parser + template schema | Phase 0 |
| 2 | Aggregation MVP + export | Phase 1 |
| 3 | Minimal UI (Template Builder) | Phase 2 |
| 4 | Calculation engine + validation | Phase 3 |
| 5 | Data Processor UI | Phase 4 |
| 6 | Testing (parallel to 4-5) | – |
| 7 | Documentation & deployment | Phase 5-6 |

---

## 10. Tech Stack

- **UI:** Flet (Flutter for Python)
- **Backend:** Python 3.11+, Pandas, Pydantic
- **Expression Eval:** simpleeval
- **Config:** YAML (PyYAML)
- **Testing:** pytest
- **Packaging:** PyInstaller or Flet Build
```