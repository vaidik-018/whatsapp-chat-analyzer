import streamlit as st
import pandas as pd
st.title("whatsapp chat analyzer")
uploaded_file=st.file_uploader("upload chat file",type="txt")

if uploaded_file:
    data=uploaded_file.read().decode("utf-8")
    lines=data.split("\n")

    st.write("total messages:",len(lines))