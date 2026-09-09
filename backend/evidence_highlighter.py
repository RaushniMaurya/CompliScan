import cv2

def highlight_evidence(image, ocr_data, extracted_fields):
    """
    Draws bounding boxes on `image` around the words that produced each
    extracted field, so the result shows exactly where a declaration
    was found on the label.
    """
    annotated = image.copy()

    words = []
    n = len(ocr_data["text"])
    for i in range(n):
        word = ocr_data["text"][i].strip()
        if word:
            words.append({
                "text": word,
                "x": ocr_data["left"][i],
                "y": ocr_data["top"][i],
                "w": ocr_data["width"][i],
                "h": ocr_data["height"][i],
            })

    color = (16, 163, 74)  # green (BGR)
    thickness = 4

    for field_name, value in extracted_fields.items():
        if not value:
            continue

        search_tokens = [t.strip(".,:;()") for t in str(value).split() if t.strip(".,:;()")]

        matched_boxes = []
        for w in words:
            clean_word = w["text"].strip(".,:;()")
            for token in search_tokens:
                if token and (token in clean_word or clean_word in token):
                    matched_boxes.append(w)
                    break

        if not matched_boxes:
            continue

        min_x = min(w["x"] for w in matched_boxes)
        min_y = min(w["y"] for w in matched_boxes)
        max_x = max(w["x"] + w["w"] for w in matched_boxes)
        max_y = max(w["y"] + w["h"] for w in matched_boxes)

        pad = 8
        cv2.rectangle(
            annotated,
            (min_x - pad, min_y - pad),
            (max_x + pad, max_y + pad),
            color,
            thickness
        )

    return annotated