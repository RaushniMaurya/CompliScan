import re

def extract_fields(ocr_text):
    """
    Extracts key Legal Metrology declarations from raw OCR text.
    Uses tolerant regex patterns to handle common OCR misreads.
    """
    fields = {}

    # --- MRP ---
    # Matches: "MAX RETAIL PRICE Rs. 10.00", "MRP Rs 99", "M R P : ₹50"
    mrp_match = re.search(
        r"(?:MAX\s*RETAIL\s*PRICE|M\.?\s*R\.?\s*P\.?)\D{0,10}(\d+[.,]?\d*)",
        ocr_text, re.IGNORECASE
    )
    if mrp_match:
        fields["mrp"] = mrp_match.group(1)

    # --- Net Quantity/Weight ---
    # Tolerant of OCR noise like "netwr", "net wt", "net qty"
    qty_match = re.search(
        r"net\s*w?[trq][a-z]{0,3}\.?\s*[:.]?\s*(\d+\.?\d*)\s*(g|kg|ml|l|gm)\b",
        ocr_text, re.IGNORECASE
    )
    if qty_match:
        fields["net_quantity"] = f"{qty_match.group(1)} {qty_match.group(2)}"

    # --- Consumer Care / Customer Care ---
    care_match = re.search(
        r"(?:consumer|customer)\s*care.{0,50}?(\d[\d\-\s]{7,})",
        ocr_text, re.IGNORECASE
    )
    if care_match:
        fields["consumer_care"] = care_match.group(1).strip()

    # --- Manufacturer (basic keyword-based) ---
    mfg_match = re.search(
        r"(?:made\s*by|manufactured\s*by|mfd\.?\s*by)\s*[:\-]?\s*([A-Za-z0-9\s.,&]{5,60})",
        ocr_text, re.IGNORECASE
    )
    if mfg_match:
        fields["manufacturer"] = mfg_match.group(1).strip().split("\n")[0]

    return fields


# --- Test it directly ---
if __name__ == "__main__":
    sample_text = """
    MAX RETAIL PRICE Rs. 10.00
    (INCL. OF ALL TAXES)
    netwr. 30 g
    MADE BY KELLOGG INDIA PVT. LTD.
    consumer care 1800-22-3500
    """
    result = extract_fields(sample_text)
    print("----- EXTRACTED FIELDS -----")
    for key, value in result.items():
        print(f"{key}: {value}")