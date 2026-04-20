import os
import easyocr

reader = easyocr.Reader(["en"])

images_dir = "Images"
for filename in sorted(os.listdir(images_dir)):
    if filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        filepath = os.path.join(images_dir, filename)
        print(f"\n{'=' * 60}")
        print(f"FILE: {filename}")
        print(f"{'=' * 60}")

        result = reader.readtext(filepath)
        for bbox, text, confidence in result:
            print(f"  {text}  ({confidence:.2f})")
