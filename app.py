import streamlit as st
import fitz
import tempfile
import os
import logging
from pipeline.llm_engine import generate_ddr
from pipeline.extractor import extract_images
from utils.pdf_generator import generate_pdf

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
PDF_MAGIC = b"%PDF"

st.set_page_config(layout="wide")

st.title("AI DDR Report Generator")

inspection_file = st.file_uploader("Upload Inspection PDF", type="pdf")
thermal_file = st.file_uploader("Upload Thermal PDF", type="pdf")


def validate_pdf(uploaded_file):
    """Validate file size and PDF magic bytes. Returns (ok, error_message, data).

    data is the full file bytes on success (so the caller can reuse them without
    a second read), or None on failure.
    """
    # Check size first using the attribute to avoid loading the entire file
    size = getattr(uploaded_file, "size", None)
    if size is not None and size > MAX_FILE_SIZE:
        return False, f"File '{uploaded_file.name}' exceeds the 50 MB size limit.", None

    # Read only the first 4 bytes to verify PDF magic bytes
    header = uploaded_file.read(4)
    if not header.startswith(PDF_MAGIC):
        logger.warning("Rejected upload '%s': invalid PDF magic bytes", uploaded_file.name)
        uploaded_file.seek(0)
        return False, f"File '{uploaded_file.name}' does not appear to be a valid PDF.", None

    # Read the rest of the file now that basic checks passed
    rest = uploaded_file.read()
    data = header + rest

    # Fallback size check when the .size attribute is unavailable
    if len(data) > MAX_FILE_SIZE:
        return False, f"File '{uploaded_file.name}' exceeds the 50 MB size limit.", None

    uploaded_file.seek(0)
    return True, None, data


def extract_text(pdf_path):
    """Extract all text from a PDF file."""
    try:
        doc = fitz.open(pdf_path)
        try:
            return "".join([p.get_text() for p in doc])
        finally:
            doc.close()
    except Exception as exc:
        logger.error("Failed to extract text from '%s': %s", pdf_path, exc)
        raise


if st.button("Generate DDR"):

    if inspection_file and thermal_file:

        # Validate both files before doing any processing
        ok1, err1, data1 = validate_pdf(inspection_file)
        ok2, err2, data2 = validate_pdf(thermal_file)

        if not ok1:
            st.error(err1)
        elif not ok2:
            st.error(err2)
        else:
            tmp_inspection = None
            tmp_thermal = None
            tmp_report = None
            try:
                # Write to secure temporary files that are only readable by the current user
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp1:
                    tmp_inspection = tmp1.name
                    tmp1.write(data1)

                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp2:
                    tmp_thermal = tmp2.name
                    tmp2.write(data2)

                logger.info("Saved uploaded PDFs to secure temp files")

                st.info("Generating report...")

                text1 = extract_text(tmp_inspection)
                text2 = extract_text(tmp_thermal)

                report = generate_ddr(text1, text2)

                imgs1 = extract_images(tmp_inspection, "inspection")
                imgs2 = extract_images(tmp_thermal, "thermal")

                all_images = imgs1 + imgs2

                # Generate output PDF to a secure temp file
                tmp_report = generate_pdf(report, all_images)

                with open(tmp_report, "rb") as f:
                    st.download_button(
                        label="Download DDR Report (PDF)",
                        data=f,
                        file_name="DDR_Report.pdf",
                        mime="application/pdf",
                    )

                st.success("Report Ready")

                col1, col2 = st.columns([2, 1])

                with col1:
                    st.subheader("DDR Report")
                    st.write(report)

                with col2:
                    st.subheader("Images")

                    if not all_images:
                        st.write("No relevant images")

                    for img in all_images:
                        st.image(img)

            except Exception as exc:
                logger.error("Error during DDR generation: %s", exc)
                st.error(f"An error occurred while generating the report: {exc}")

            finally:
                # Always clean up sensitive temporary files
                for path in [tmp_inspection, tmp_thermal, tmp_report]:
                    if path and os.path.exists(path):
                        try:
                            os.remove(path)
                            logger.info("Removed temporary file '%s'", path)
                        except OSError as exc:
                            logger.warning("Could not remove temporary file '%s': %s", path, exc)

    else:
        st.warning("Upload both PDFs")
