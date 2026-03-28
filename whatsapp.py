# whatsapp.py
import re
from datetime import datetime
from collections import Counter, defaultdict
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import emoji
import string

nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)

# ------------- Parser -------------
# Adaptable regex for different date formats
# Examples matched: "25/10/2025, 10:53 - Name: Message" or "10/25/2025, 10:53 - Name: Message"
TIMESTAMP_REGEX = r'^(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}),?\s+(\d{1,2}:\d{2}\s?(?:am|pm|AM|PM| am| pm)?)\s*[-–]\s*(.*)$'

# A second regex to separate author and message when author present
AUTHOR_MSG_REGEX = r'^(.*?):\s(.*)$'

def parse_whatsapp_txt(file_path, ts_regex=TIMESTAMP_REGEX):
    lines = open(file_path, encoding='utf-8', errors='ignore').read().splitlines()
    messages = []
    current = None  # tuple (timestamp_str, rest_of_line)

    ts_re = re.compile(ts_regex)
    for line in lines:
        if not line.strip():
            if current:
                current['message'] += '\n'
            continue

        m = ts_re.match(line)
        if m :
            datepart = m.group(1).strip()
            timepart = m.group(2).strip()
            rest = m.group(3).strip()
            if current:
                messages.append(current)
            current = {'date': datepart, 'time': timepart, 'raw': rest, 'message': rest}
        else:
            if current:
                current['message'] += '\n' + line
            else:
                continue
    if current:
        messages.append(current)

    parsed = []
    for m in messages:
        raw = m['message']
        auth_match = re.match(AUTHOR_MSG_REGEX, raw)
        if auth_match:
            author = auth_match.group(1).strip()
            message_text = auth_match.group(2).strip()
        else:
            author = None
            message_text = raw

        dt = None
        date_time_str = f"{m['date']} {m['time']}"
        for fmt in [
            '%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M', '%m/%d/%Y %H:%M:%S', '%m/%d/%Y %H:%M',
            '%d-%m-%Y %H:%M:%S', '%d-%m-%Y %H:%M', '%Y-%m-%d %H:%M',
            '%d/%m/%Y %I:%M %p', '%m/%d/%Y %I:%M %p', '%d/%m/%y %I:%M %p', '%m/%d/%y %I:%M %p'
        ]:
            try:
                dt = datetime.strptime(date_time_str, fmt)
                break
            except Exception:
                continue

        parsed.append({'datetime': dt, 'author': author, 'message': message_text, 'raw': m['raw']})

    df = pd.DataFrame(parsed)
    return df

# ------------- Analysis helpers -------------

def basic_stats(df):
    stats = {}
    stats['total_messages'] = len(df)
    stats['start_date'] = df['datetime'].min()
    stats['end_date'] = df['datetime'].max()
    stats['messages_per_user'] = df['author'].value_counts(dropna=False).to_dict()
    return stats

def top_words(df, n=30, extra_stopwords=None):
    stop = set(stopwords.words('english'))
    if extra_stopwords:
        stop |= set(extra_stopwords)
    words = []
    for text in df['message'].dropna():
        tokens = nltk.word_tokenize(text.lower())
        for t in tokens:
            t = t.strip(string.punctuation + "“”’'`")
            if not t or t in stop or t.isdigit():
                continue
            words.append(t)
    c = Counter(words)
    return c.most_common(n)

def emoji_counts(df, n=20):
    c = Counter()
    for text in df['message'].dropna():
        for ch in text:
            if ch in emoji.EMOJI_DATA:
                c[ch] += 1
    return c.most_common(n)

def hourly_activity(df):
    by_hour = df.groupby(df['datetime'].dt.hour).size()
    return by_hour.reindex(range(24), fill_value=0)

def weekday_activity(df):
    by_wd = df.groupby(df['datetime'].dt.weekday).size()
    return by_wd.reindex(range(7), fill_value=0)

def sentiment_per_user(df):
    analyzer = SentimentIntensityAnalyzer()
    sents = defaultdict(list)
    for _, row in df.dropna(subset=['message']).iterrows():
        score = analyzer.polarity_scores(row['message'])['compound']
        sents[row['author']].append(score)
    out = {user: (sum(scores)/len(scores) if scores else 0) for user, scores in sents.items()}
    return out

# ------------- Visualization examples -------------
def plot_messages_per_user(df, top_n=10):
    vc = df['author'].value_counts().head(top_n)
    vc.plot(kind='bar', figsize=(8,4))
    plt.title(f'Messages per user (top {top_n})')
    plt.ylabel('Messages')
    plt.tight_layout()
    plt.show()

def plot_hourly(df):
    h = hourly_activity(df)
    h.plot(kind='bar', figsize=(10,4))
    plt.title('Messages by hour of day')
    plt.xlabel('Hour (0-23)')
    plt.tight_layout()
    plt.show()

def make_wordcloud(df):
    text = " ".join(df['message'].dropna().astype(str).tolist())
    wc = WordCloud(width=800, height=400).generate(text)
    plt.figure(figsize=(12,6))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.show()

# ------------- Example usage -------------
if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python whatsapp.py path/to/chat.txt")
        sys.exit(1)
    path = sys.argv[1]
    df = parse_whatsapp_txt(path)
    df.to_csv('parsed_whatsapp.csv', index=False)
    print("Saved parsed_whatsapp.csv, total messages:", len(df))
    print(basic_stats(df))
    print("Top words:", top_words(df, 20))
    print("Top emojis:", emoji_counts(df, 20))
    print("Sentiment average per user:", sentiment_per_user(df))
    plot_messages_per_user(df)
    plot_hourly(df)
    # make_wordcloud(df)

# To check first few lines of chat.txt
with open("chat.txt", encoding="utf-8") as f:
    for i in range(5):
        print(f.readline().strip())
