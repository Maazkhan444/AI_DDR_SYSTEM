import fitz
import os

def extract_images(pdf_path, prefix):
    output_dir = "outputs/images"
    os.makedirs(output_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    images = []

    for i, page in enumerate(doc):
        for j, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base = doc.extract_image(xref)

            w = base.get("width", 0)
            h = base.get("height", 0)

            # filter small icons/logos
            if w < 300 or h < 300:
                continue

            path = f"{output_dir}/{prefix}_{i}_{j}.png"

            with open(path, "wb") as f:
                f.write(base["image"])

            images.append(path)

            # limit images
            if len(images) >= 4:
                return images

    return images
