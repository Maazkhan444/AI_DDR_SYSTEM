import fitz
import os

def extract_images(pdf_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    doc = fitz.open(pdf_path)
    image_paths = []

    for i, page in enumerate(doc):
        images = page.get_images(full=True)
        for j, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]

            img_name = f"img_{i}_{j}.png"
            img_path = os.path.join(output_folder, img_name)

            with open(img_path, "wb") as f:
                f.write(image_bytes)

            if os.path.getsize(img_path) > 15000:
                image_paths.append(img_path)

    return image_paths
