import os
import shutil
import uuid
import logging

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from data_extraction import z_ocr_database_json
from personal_data import z_personal_data, z_personal_data_excel
from masked_data import z_masked_text
from cv_extractions import run as cv_extraction_run
from score_function import db

logger = logging.getLogger(__name__)

app = FastAPI()

# Allow the React/Next.js frontend running on localhost:3000 to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_ROOT = "uploads"


@app.post("/analyze")
async def analyze(resumes: list[UploadFile] = File(...), job_spec: UploadFile = File(...)):
    session_id = str(uuid.uuid4())
    cv_folder = os.path.join(UPLOAD_ROOT, session_id, "cv_files")
    os.makedirs(cv_folder, exist_ok=True)

    # z_1_ocr_databases.text_save() reads files by path, so resumes are
    # written to disk first rather than processed in-memory.
    for resume in resumes:
        dest = os.path.join(cv_folder, resume.filename)
        with open(dest, "wb") as f:
            shutil.copyfileobj(resume.file, f)

    job_spec_path = os.path.join(UPLOAD_ROOT, session_id, job_spec.filename)
    with open(job_spec_path, "wb") as f:
        shutil.copyfileobj(job_spec.file, f)

    session_dir = os.path.join(UPLOAD_ROOT, session_id)
    ocr_output_path = os.path.join(session_dir, "row_ocr_cv_deatils.json")
    personal_output_path = os.path.join(session_dir, "full_personal_data.json")
    excel_output_path = os.path.join(session_dir, "candidate_details.xlsx")

    # Phase 0: OCR text extraction from resumes
    try:
        z_ocr_database_json.extract_and_save(cv_folder, ocr_output_path)
    except Exception as e:
        logger.exception(f"OCR EXTRACTION FAILED \n{type(e).__name__} \nError - {e}")
        return {"status": "error", "message": "Data extraction failed."}

    # Phase 1: send extracted text to Ollama, pull out name/location/phone/email
    try:
        z_personal_data.personal_data_json(ocr_output_path, personal_output_path)
    except Exception as e:
        logger.exception(f"PERSONAL DATA EXTRACTION FAILED \n{type(e).__name__} \nError - {e}")
        return {"status": "error", "message": "Personal data extraction failed."}

    # Phase 2: write personal details out to an Excel file
    try:
        z_personal_data_excel.personal_info(personal_output_path, excel_output_path)
    except Exception as e:
        logger.exception(f"EXCEL CREATION FAILED \n{type(e).__name__} \nError - {e}")
        return {"status": "error", "message": "Excel file creation failed."}
    
    masked_output_path = os.path.join(session_dir, "masked_all_text.json")

    # Phase 3: mask personal identifiers out of the extracted CV text
    try:
        z_masked_text.llm_text(personal_output_path, ocr_output_path, masked_output_path)
    except Exception as e:
        logger.exception(f"MASKING FAILED \n{type(e).__name__} \nError - {e}")
        return {"status": "error", "message": "Data masking failed."}

    # Phase 4: send each masked CV to the LLM for structured details
    cv_details_dir = os.path.join(session_dir, "cv_extractions")
    final_details_path = os.path.join(session_dir, "final_cv_details.json")
    try:
        cv_extraction_run.process_masked_texts_file(masked_output_path, cv_details_dir, final_details_path)
    except Exception as e:
        logger.exception(f"CV DETAILS EXTRACTION FAILED \n{type(e).__name__} \nError - {e}")
        return {"status": "error", "message": "CV details extraction failed."}

    # Frontend only needs to know extraction finished at this stage —
    # not the extracted text itself.
    return {"status": "completed", "session_id": session_id}


@app.get("/download/masked/{session_id}")
async def download_masked(session_id: str):
    file_path = os.path.join(UPLOAD_ROOT, session_id, "masked_all_text.json")

    if not os.path.exists(file_path):
        return {"status": "error", "message": "File not found."}

    return FileResponse(
        file_path,
        media_type="application/json",
        filename="masked_all_text.json",
    )


@app.get("/download/excel/{session_id}")
async def download_excel(session_id: str):
    file_path = os.path.join(UPLOAD_ROOT, session_id, "candidate_details.xlsx")

    if not os.path.exists(file_path):
        return {"status": "error", "message": "File not found."}

    return FileResponse(
        file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="candidate_details.xlsx",
    )

@app.get("/download/details/{session_id}")
async def download_details(session_id: str):
    file_path = os.path.join(UPLOAD_ROOT, session_id, "final_cv_details.json")

    if not os.path.exists(file_path):
        return {"status": "error", "message": "File not found."}

    return FileResponse(
        file_path,
        media_type="application/json",
        filename="final_cv_details.json",
    )

