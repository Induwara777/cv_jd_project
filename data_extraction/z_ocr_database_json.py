import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from . import z_1_ocr_databases


def extract_and_save(cv_folder="cv_files", output_path=os.path.join("row_ocr_output", "row_ocr_cv_deatils.json")):
    """Run OCR extraction on all CVs in cv_folder and save the raw text to output_path as JSON."""
    datafile = z_1_ocr_databases.text_save(cv_folder)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(datafile, f, indent=4)

    return datafile


if __name__ == "__main__":
    extract_and_save()