import streamlit as st
import fitz
from pipeline.llm_engine import generate_ddr
from pipeline.extractor import extract_images
from utils.pdf_generator import generate_pdf

st.set_page_config(layout="wide")

st.title("AI DDR Report Generator")

inspection_file = st.file_uploader("Upload Inspection PDF", type="pdf")
thermal_file = st.file_uploader("Upload Thermal PDF", type="pdf")

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    return "".join([p.get_text() for p in doc])

if st.button("Generate DDR"):

    if inspection_file and thermal_file:

        with open("temp1.pdf", "wb") as f:
            f.write(inspection_file.read())

        with open("temp2.pdf", "wb") as f:
            f.write(thermal_file.read())

        st.info("Generating report...")

        text1 = extract_text("temp1.pdf")
        text2 = extract_text("temp2.pdf")

        report = generate_ddr(text1, text2)

        imgs1 = extract_images("temp1.pdf", "inspection")
        imgs2 = extract_images("temp2.pdf", "thermal")

        all_images = imgs1 + imgs2

        # GENERATE PDF FIRST
        pdf_file = generate_pdf(report, all_images)

        # DOWNLOAD BUTTON AT TOP
        with open(pdf_file, "rb") as f:
            st.download_button(label="Download DDR Report (PDF)",data=f,file_name="DDR_Report.pdf",mime="application/pdf")

        st.success("Report Ready")

        col1, col2 = st.columns([2,1])

        with col1:
            st.subheader("DDR Report")
            st.write(report)

        with col2:
            st.subheader("Images")

            if not all_images:
                st.write("No relevant images")

            for img in all_images:
                st.image(img)

    else:
        st.warning("Upload both PDFs")
