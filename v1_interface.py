import streamlit as st
from streamlit_tags import st_tags, st_tags_sidebar
import pandas as pd
import time
from application_v1 import main
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer, PageBreak, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.graphics.shapes import Drawing, Line
from reportlab.lib.enums import TA_JUSTIFY
import re
from streamlit_pdf_viewer import pdf_viewer

# Title
st.title("Web Page Analyzer")

# Sidebar
st.sidebar.header("Input Type")
input_type = st.sidebar.radio("Choose input type:", ("URL", ".docx File"))

# Input settings based on selection
if input_type == "URL":
    st.sidebar.header("URL Input")
    url = st.sidebar.text_input("Enter URL")
elif input_type == ".docx File":
    st.sidebar.header("File Upload")
    uploaded_file = st.sidebar.file_uploader("Upload .docx file", type=["docx"])

# Caution words input
caution_words = st_tags_sidebar(
    label='# Enter Keywords:',
    text='Press enter to add more',
    value=["Best", "Specialist", "Specialised", "Finest", "Most experienced",
                                "Superior", "Principle", "Expert", "Amazing", "Speciality",
                                "leader", "leaders", "service", "implantologist"
            ],
    maxtags=20,
    key='1'
)

# Analyze button
if st.sidebar.button("Analyze"):
    with st.spinner('Analyzing...'):
        try:
            if input_type == "URL":
                if url:
                    res_dict, pdf_content = main(url,input_type=input_type)
                else:
                    st.error("Please enter a URL.")
                    st.stop()
            elif input_type == ".docx File":
                if uploaded_file:
                    # Save the uploaded file temporarily
                    with open("uploaded_file.docx", "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    # Replace `main` with a function that handles .docx files if necessary
                    res_dict, pdf_content = main("uploaded_file.docx",input_type=input_type)
                else:
                    st.error("Please upload a .docx file.")
                    st.stop()

            with open(pdf_content, "rb") as pdf_file:
                pdf_data = pdf_file.read()
                st.download_button(
                    label="Download PDF",
                    data=pdf_data,
                    file_name="analysis_report.pdf",
                    mime="application/pdf"
                ) 
                
            pdf_viewer(pdf_content)
            # df = pd.DataFrame(res_dict)
            # st.header("Analysis Results")
            # st.write(df)
            
            # st.header("Caution Words Results")
            # for word in caution_words:
            #     results = [item for item in content_list if word.lower() in item.lower()]
            #     if results:
            #         with st.expander(f"**{word}** found in:"):
            #             for result in results:
            #                 st.write(result)
            
            # st.error(f"**Warning:** DataFrame contains {df.shape[0]} rows.")
        
        except FileNotFoundError:
            st.error("File not found")
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Main panel
