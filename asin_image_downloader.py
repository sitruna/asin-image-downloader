{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
import pandas as pd\
import requests\
import zipfile\
import tempfile\
import os\
\
st.set_page_config(page_title="ASIN Image Downloader", layout="centered")\
\
st.title("ASIN Image Downloader")\
st.write("Upload your file with ASINs and multiple image columns. The app will download, rename, and zip everything for you.")\
\
# -------------------------------------------------------\
# FILE UPLOAD\
# -------------------------------------------------------\
uploaded_file = st.file_uploader("Upload your file", type=["xlsx", "csv"])\
\
if uploaded_file:\
    # Load file\
    if uploaded_file.name.endswith(".xlsx"):\
        df = pd.read_excel(uploaded_file)\
    else:\
        df = pd.read_csv(uploaded_file)\
\
    st.write("### Preview")\
    st.dataframe(df.head())\
\
    # Select ASIN column\
    asin_col = st.selectbox("Select ASIN Column", df.columns, index=list(df.columns).index("ASIN") if "ASIN" in df.columns else 0)\
\
    # Image columns (multi-select)\
    st.write("### Select Image Columns (in order)")\
    image_columns = st.multiselect(\
        "Choose columns with image URLs",\
        df.columns,\
        default=[c for c in df.columns if "Image" in c or "Swatch" in c]\
    )\
\
    # Button\
    if st.button("Generate ZIP"):\
        if not image_columns:\
            st.error("Please select at least one image column.")\
        else:\
            with st.spinner("Downloading images\'85"):\
                temp_dir = tempfile.mkdtemp()\
                zip_path = os.path.join(temp_dir, "asin_images.zip")\
                image_count = 0\
\
                # Naming rules\
                def get_image_suffix(column_name, index):\
                    if column_name.lower() == "main image":\
                        return "Main"\
                    if "swatch" in column_name.lower():\
                        return "Swatch"\
                    return f"PT\{index:02d\}"\
\
                with zipfile.ZipFile(zip_path, "w") as zipf:\
                    for _, row in df.iterrows():\
                        asin = str(row[asin_col]).strip()\
\
                        for idx, col in enumerate(image_columns, start=1):\
                            url = str(row[col]).strip()\
\
                            if not url or url.lower() == "nan":\
                                continue\
\
                            suffix = get_image_suffix(col, idx)\
                            filename = f"\{asin\}.\{suffix\}.jpg"  # always jpg since Amazon images are jpg\
\
                            try:\
                                response = requests.get(url, timeout=10)\
                                response.raise_for_status()\
\
                                file_path = os.path.join(temp_dir, filename)\
\
                                with open(file_path, "wb") as f:\
                                    f.write(response.content)\
\
                                zipf.write(file_path, filename)\
                                image_count += 1\
\
                            except Exception as e:\
                                st.warning(f"Failed to download \{url\} \'97 \{e\}")\
\
            st.success(f"Done! \{image_count\} images downloaded and zipped.")\
\
            with open(zip_path, "rb") as f:\
                st.download_button(\
                    label="Download ZIP",\
                    data=f,\
                    file_name="asin_images.zip",\
                    mime="application/zip"\
                )\
}