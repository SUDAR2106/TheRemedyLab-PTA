import os
import json
import pandas as pd
from typing import Dict
from config import STRUCTURED_DIR, RECORDS_FILENAME

# Update the filename to end with `.jsonl`
JSON_FILENAME = RECORDS_FILENAME.replace(".csv", ".jsonl")

class Consolidator:
    def __init__(self, json_dir=STRUCTURED_DIR, filename=JSON_FILENAME):
        self.json_dir = json_dir
        self.filename = filename

        # Ensure the directory exists
        os.makedirs(self.json_dir, exist_ok=True)

        # Ensure the full path to the JSON file is set
        self.json_path = os.path.join(self.json_dir, self.filename)

    def save_structured_record(self,patient_info: Dict[str, str], metrics: Dict[str, tuple]):

  # Combine patient info and metric values (as nested dicts: {value, color})
        record = {**patient_info}
        for k, (value, color) in metrics.items():
            record[k] = {
                "value": str(value),
                "color": color
            }

        # Sort keys for consistency (optional)
        record = dict(sorted(record.items()))

        # Write as JSON line
        with open(self.json_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


# from consolidator import Consolidator
# consolidator = Consolidator()
# consolidator.save_structured_record(patient_info, metrics)
