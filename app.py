import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import emoji

st.set_page_config(page_title="Whatsapp Analyzer", layout="wide")
st.title("whatsapp chat analyzer")
uploaded_file=st.file_uploader("upload chat file",type="txt")

def parse_chat(file):
    lines=file.read().decode("utf-8").split("\n")
    data=[]
    for line in lines:
        if "-" in line and ":" in line:
            try:
                date_time, msg = line.split(" - ", 1)
                author, message = msg.split(":", 1)
                data.append([date_time, author.strip(),message,strip()])
            except:
                continue
    df=pd.DataFrame(date, columns=["datetime", "author", "message"])
    return df


if uploaded_file:
    df=parse_chat(uploaded_file)
    st.subheader("basic stats")
    col1, col2 = st.columns(2)
    col1.metric("total message", len(df))
    col2.metric("total users", df["author"].nunique())
    st.subheader("message per user")
    user_counts=df["author"].value_counts()
    st.bar_chart(user_counts)
    emojis=[]
    for msg in df["message"]:
        for char in msg:
            if char in emoji.EMOJI_DATA:
                emojis.append(char)
    emoji_count=Counter(emojis).most_common(5)
    st.write(emoji_count)

    st.subheader("most used words")
    words="".join(df["message"]).lower().split()
    common_words=Counter(words).most_common(10)
    st.write(common_words)
 