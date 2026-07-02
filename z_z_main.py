import ollama
import re
import z_ocr_fun
import z_text_preprocess
import z_cv_extraction_set
import z_personal_data_excel
import json
import spacy
import os
from openai import OpenAI
import requests


if __name__ == "__main__":
    # Getting OCR text
    text_data = z_ocr_fun.extraction("y_Associate Data Scientist Induwara Dilshan.pdf")

    # Personal details are MASKED
    final_data = z_text_preprocess.llm_text(text=text_data,y="y_Associate Data Scientist Induwara Dilshan.pdf")

    # JSON files are created
    json_file = z_cv_extraction_set.collection(final_data)

    # Personal details are saved in an excel file
    z_personal_data_excel.personal_info("y_Associate Data Scientist Induwara Dilshan.pdf")

