import os
import re
from openai import OpenAI
import fitz
import z_ocr_fun
import json
import z_text_preprocess
import cv_extractions.z_cv_extraction_set 

# Catching all names in a folder
def file_name(folder):
    names = [f for f in os.listdir(folder) if f.endswith(".pdf") ]
    return names


# Return json file for each CV
def one_json(y):
    text = z_ocr_fun.extraction(f"{y}.pdf")
    file = cv_extractions.z_cv_extraction_set.collection(text)
    return file

# Call json files for all CV.
def json_file(output_folder):
    try:

        names_of_cv = file_name(output_folder)

        os.makedirs(output_folder,exist_ok=True)
        
        for i,x in enumerate(names_of_cv,start = 1):
            
            json_path = os.path.join(output_folder,f"{x}.json")
            if os.path.exists(json_path):
                continue

            llm_json = one_json(x)
            llm_json["candidate_num"] = i
            llm_json.update(z_text_preprocess.preprocess(f"{x}.pdf"))

            with open(f"file_json_filess\\{x}.json","w",encoding="utf-8") as f:
                json.dump(llm_json,f,indent = 4)
    except Exception as e:
        print(f"Error : {e}")
    
if __name__ == "__main__":
    json_file("file_cvs")