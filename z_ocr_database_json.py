import z_ocr_databases
import json

datafile = z_ocr_databases.text_save("cv_files")
with open("row_ocr_output\\row_ocr_cv_deatils.json","w",encoding="utf-8") as f:
    json.dump(datafile , f, indent=4)