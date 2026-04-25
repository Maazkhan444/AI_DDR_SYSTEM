from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import datetime
import tempfile

def generate_pdf(text, images):
    # SimpleDocTemplate opens the file by path, so we create the temp file,
    # close it immediately to release the OS handle, and then pass the path.
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    tmp.close()
    output_path = tmp.name
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph("<b>Detailed Diagnostic Report (DDR)</b>", styles['Title']))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph(f"Generated on: {datetime.datetime.now().strftime('%d-%m-%Y')}", styles['Normal']))
    elements.append(Spacer(1, 15))

    # Content
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            elements.append(Spacer(1, 6))
            continue

        if line.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.")):
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(f"<b>{line}</b>", styles['Heading2']))
        else:
            elements.append(Paragraph(line, styles['Normal']))

    # Images
    if images:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("<b>Supporting Images</b>", styles['Heading2']))
        elements.append(Spacer(1, 10))

        for i, img in enumerate(images):
            try:
                elements.append(Image(img, width=400, height=250))
                elements.append(Spacer(1, 5))
                elements.append(Paragraph(f"Figure {i+1}: Observed issue (possible dampness or leakage)", styles['Normal']))
                elements.append(Spacer(1, 12))
            except:
                continue

    doc.build(elements)
    return output_path
