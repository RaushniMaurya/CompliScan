from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
import shutil
import os

from full_pipeline import run_pipeline
from database import init_db, save_scan, get_history, get_scan_by_id
from report_generator import generate_pdf_report

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
ANNOTATED_DIR = "annotated"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(ANNOTATED_DIR, exist_ok=True)

app.mount("/annotated", StaticFiles(directory=ANNOTATED_DIR), name="annotated")

init_db()


@app.get("/")
def home():
    return {"message": "CompliScan backend is running!"}


@app.post("/scan")
async def scan_product(file: UploadFile = File(...)):
    save_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    report = run_pipeline(save_path)
    scan_id = save_scan(file.filename, report)
    report["scan_id"] = scan_id

    return report


@app.get("/history")
def scan_history():
    return get_history()


@app.get("/report/{scan_id}")
def download_report(scan_id: int):
    scan = get_scan_by_id(scan_id)
    if scan is None:
        return {"error": "Scan not found"}

    pdf_buffer = generate_pdf_report(scan)
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=compliscan_report_{scan_id}.pdf"}
    )