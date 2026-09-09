import cv2
import pytesseract
import os
import uuid
from extract_fields import extract_fields
from compliance_engine import check_compliance
from evidence_highlighter import highlight_evidence

import shutil

tesseract_path = shutil.which("tesseract")

if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
ANNOTATED_DIR = "annotated"
os.makedirs(ANNOTATED_DIR, exist_ok=True)


def run_pipeline(image_path):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Image not found: {image_path}")
        return

    scale_percent = 250
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    resized = cv2.resize(img, (width, height), interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    denoised = cv2.medianBlur(gray, 3)
    _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    custom_config = r"--oem 3 --psm 11"
    ocr_data = pytesseract.image_to_data(thresh, config=custom_config, output_type=pytesseract.Output.DICT)
    raw_text = " ".join(w for w in ocr_data["text"] if w.strip())

    fields = extract_fields(raw_text)

    report = check_compliance(fields)
    report["extracted_fields"] = fields

    annotated = highlight_evidence(resized, ocr_data, fields)
    annotated_filename = f"{uuid.uuid4().hex}.jpg"
    annotated_path = os.path.join(ANNOTATED_DIR, annotated_filename)
    cv2.imwrite(annotated_path, annotated)
    report["annotated_image"] = annotated_filename

    print(f"\n========== SCAN RESULT: {image_path} ==========")
    print(f"\nExtracted Fields: {fields}")
    print(f"\nOverall Status: {report['overall_status']}")
    print(f"Missing Required Declarations: {report['missing_required_count']}\n")

    for item in report["details"]:
        mark = "✅" if item["status"] == "PASS" else ("⚠️" if item["status"] == "NOT_APPLICABLE" else "❌")
        print(f"{mark} {item['label']}: {item['status']} (Detected: {item['detected_value']})")

    return report


if __name__ == "__main__":
    run_pipeline("../data/test_image.jpg")