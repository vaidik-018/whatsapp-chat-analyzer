import streamlit as st
import pandas as pd
from collections import Counter
import emoji

st.set_page_config(page_title="WhatsApp Analyzer", layout="wide")

st.title("📊 WhatsApp Chat Analyzer")

uploaded_file = st.file_uploader("Upload your WhatsApp chat (.txt)", type="txt")

# 🔹 Function to parse chat
def parse_chat(file):
    lines = file.read().decode("utf-8").split("\n")
    data = []

    for line in lines:
        if " - " in line and ": " in line:
            try:
                date_time, msg = line.split(" - ", 1)
                author, message = msg.split(": ", 1)
                data.append([date_time, author.strip(), message.strip()])
            except:
                continue

    df = pd.DataFrame(data, columns=["datetime", "author", "message"])
    return df


# 🔹 Main logic
if uploaded_file:
    df = parse_chat(uploaded_file)

    # 📌 Basic Stats
    st.subheader("📌 Basic Stats")
    col1, col2 = st.columns(2)

    col1.metric("Total Messages", len(df))
    col2.metric("Total Users", df["author"].nunique())

    # 👥 Messages per User
    st.subheader("👥 Messages per User")
    user_counts = df["author"].value_counts()
    st.bar_chart(user_counts)

    # 😂 Emoji Analysis
    st.subheader("😂 Top Emojis")
    emojis = []
    for msg in df["message"]:
        for char in msg:
            if char in emoji.EMOJI_DATA:
                emojis.append(char)

    emoji_counts = Counter(emojis).most_common(5)
    st.write(emoji_counts)

    # 📝 Most Used Words
    st.subheader("📝 Most Used Words")
    words = " ".join(df["message"]).lower().split()
    common_words = Counter(words).most_common(10)
    st.write(common_words)