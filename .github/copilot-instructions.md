# Copilot Instructions for Groupe_5

## Project Overview
This project collects, processes, and analyzes event data for Las Vegas in October 2025. It consists of Python scripts for scraping, enriching, and transforming event data, with outputs stored as JSON and loaded into pandas DataFrames for analysis.

## Key Components
- `APIscrapping.py`: Scrapes event data from Bandsintown for each day in October 2025, saving results as JSON in `data_json/`. Handles retries, random user agents, and event deduplication.
- `json_to_pandas.py`: Loads all JSON event files from `data_json/` into a single pandas DataFrame. Handles encoding issues and skips malformed files.
- `enrichissement_type_salle.py`: Enriches the DataFrame by classifying venue types using custom rules based on venue names.
- `data_json/`: Contains daily event JSON files, named by date (e.g., `october_evt_lv_20251007.json`).

## Data Flow
1. **Scraping**: Run `APIscrapping.py` to fetch and store event data for each day.
2. **Loading**: Use `load_all_events()` from `json_to_pandas.py` to aggregate all event data into a DataFrame.
3. **Enrichment**: Run `enrichissement_type_salle.py` to classify venues and add the `venueType` column.

## Developer Workflows
- **Scraping**: Run `APIscrapping.py` as a script. It will fetch all days in October and save to `data_json/`.
- **Data Loading**: Import `load_all_events` in analysis scripts to get a DataFrame of all events.
- **Enrichment**: Run `enrichissement_type_salle.py` after scraping and loading to add venue type information.

## Conventions & Patterns
- All event data is stored as JSON, keyed by a unique event ID.
- Data enrichment is performed in separate scripts, not during scraping.
- Use pandas for all tabular data manipulation.
- Handle encoding errors gracefully when loading JSON.
- Venue type classification uses simple keyword-based rules.

## Examples
- To load all events:
  ```python
  from json_to_pandas import load_all_events
  df = load_all_events()
  ```
- To enrich venue types, run:
  ```bash
  python enrichissement_type_salle.py
  ```

## Integration Points
- External API: Bandsintown (see `APIscrapping.py` for endpoint and parameters)
- Data exchange between scripts is via JSON files and pandas DataFrames.

## Tips for AI Agents
- Always check for new or updated files in `data_json/` before analysis.
- If adding new enrichment, create a new script following the pattern in `enrichissement_type_salle.py`.
- For new data sources, follow the structure in `APIscrapping.py` for scraping and saving.

---
_Last updated: 2025-10-14_
