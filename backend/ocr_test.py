import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

image_path = "../data/test_img2.jpeg"
img = cv2.imread(image_path)

scale_percent = 250
width = int(img.shape[1] * scale_percent / 100)
height = int(img.shape[0] * scale_percent / 100)
resized = cv2.resize(img, (width, height), interpolation=cv2.INTER_CUBIC)

gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
denoised = cv2.medianBlur(gray, 3)
_, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

# image_to_data gives word-level bounding boxes, not just plain text
data = pytesseract.image_to_data(thresh, config="--oem 3 --psm 11", output_type=pytesseract.Output.DICT)

# Print each detected word with its position
for i in range(len(data["text"])):
    word = data["text"][i].strip()
    if word:  # skip empty entries
        x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
        print(f"'{word}'  →  x={x}, y={y}, w={w}, h={h}")