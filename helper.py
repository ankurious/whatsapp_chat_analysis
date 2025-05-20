from urlextract import URLExtract
from collections import Counter
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
import re, string,emoji

def fetch_stats(selected_user,df):
    if selected_user != 'Overall':
        df=df[df['user'] == selected_user] #gets selected user from app and its values are stores in df
        #we could have used another new variable but not necessary
    #1. no. of messages
    num_messages = df.shape[0]
    #2. no. of words
    words=[]
    for message in df['message']: #each message in message column of dataframe
        words.extend(message.split()) #splitted on basis of spaces, added in words list

    nums_media=df[df['message']=='<Media omitted>\n'].shape[0] #no. of media file

    #no. of links
    extractor = URLExtract()
    y = []
    for message in df['message']:
        y.extend(extractor.find_urls(message))

    return num_messages, len(words),nums_media,len(y)
#------------------------------------------------------------------------------------------------------------------

def most_busy_users(df):
    x=df['user'].value_counts().head(10)
    df=round((df['user'].value_counts()/df.shape[0])*100,2).reset_index().rename(columns={'index':'name','user':'percent'})

    return x,df

#------------------------------------------------------------------------------------------------------------------

def load_custom_stopwords(file_path='stop_hinglish.txt'):
    with open(file_path, 'r', encoding='utf-8') as f:
        return set(word.strip().lower() for word in f if word.strip())

def remove_code_messages(df):
    code_keywords = [
        "public", "class", "static", "void", "int", "String", "Scanner",
        "System", "import", "package", "return", "new", "throws", "try", "catch","public",
        "private", "protected", "class", "interface", "extends", "implements",
        "static", "final", "void", "int", "long", "float", "double", "boolean", "char",
        "String", "System", "out", "println", "main", "args", "return", "new", "this", "super",
        "if", "else", "while","https","youtube", "for", "do", "switch", "case", "break", "continue", "default",
        "try", "catch", "finally", "throw", "throws", "import", "package", "true", "false",
        "null", "Scanner", "nextInt", "nextLine", "next", "in", "java", "util", "print",
        "array", "length", "equals", "hashCode", "valueOf", "toString", "instanceof",
        "binarysearch", "findrange","deleted", "code", "mid", "e", "s", "ar", "sc"
    ]

    # Regex to match code-like patterns
    code_pattern = re.compile(
        r"|".join([
            r";",                     # any line with semicolon
            r"\{|\}",                # curly braces
            r"import\s+\w+",         # import statements
            r"public\s+static\s+void\s+main",  # main method
            r"\w+\s+\w+\s*\(.*\)",   # method definitions
            r"<.*>",                 # generics
        ] + code_keywords),
        flags=re.IGNORECASE
    )

    # Keep only rows that do not match the code pattern
    df = df[df['message'] != '<Media omitted>\n']
    df = df[df['user'] != 'group_notification']
    df_cleaned = df[~df['message'].str.contains(code_pattern)]
    return df_cleaned

#------------------------------------------------------------------------------------------------------

def create_wordcloud(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Filter out media messages and group notifications
    # df = df[df['message'] != '<Media omitted>\n']
    # df = df[df['user'] != 'group_notification']
    df=remove_code_messages(df)
    text = df['message'].str.cat(sep=" ")

    # Define stopwords
    stopwords = set(STOPWORDS)
    stopwords.update(load_custom_stopwords())

    if not text.strip():  # if text is empty or whitespace only
        return None  # no wordcloud possible
    # Generate word cloud
    wc = WordCloud(
        width=800,
        height=400,
        background_color='white',
        colormap='viridis',
        min_font_size=10,
        max_words=200,
        contour_color='steelblue',
        contour_width=1.5,
        stopwords=stopwords
    )
    wc_img = wc.generate(text)
    return wc_img

#---------------------------------------------------------------------------------------------------

def most_common_words(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # df = df[df['message'] != '<Media omitted>\n']
    # df = df[df['user'] != 'group_notification']
    temp = remove_code_messages(df)
    text = temp['message'].str.cat(sep=" ")
    # Define stopwords
    stopwords = set(STOPWORDS)
    stopwords.update(load_custom_stopwords())
    stopwords.update(string.punctuation)

    words=[]
    for message in temp['message']:
        for word in message.lower().split():
            cleaned_word = word.strip(string.punctuation + " \n\t\r")
            if cleaned_word and cleaned_word not in stopwords:
                words.append(cleaned_word)

    return_df = pd.DataFrame(Counter(words).most_common(15))
    return_df.columns = ['Word', 'Count']
    return return_df

#-------------------------------------------------------------------------------------------------

def emoji_count(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    emojis=[]
    for message in df['message']:
        emojis.extend([c for c in message if emoji.is_emoji(c)])

    emoji_df=pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    return emoji_df
#----------------------------------------------------------------------

def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))
    timeline['time'] = time
    return timeline

def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    daily_timeline=df.groupby('only_date').count()['message'].reset_index()
    return daily_timeline

def week_activity(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['day_name'].value_counts()

def month_activity(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['month'].value_counts()

def activity_heatmap_period(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    #periods 00-01,01-02...
    df['period'] = df['hour'].apply(lambda x: f"{x:02d}–{(x + 1) % 24:02d}")
    heatmap_data = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)
    # ORDered days
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    period_order = [f"{i:02d}–{(i + 1) % 24:02d}" for i in range(24)]
    heatmap_data = heatmap_data.reindex(index=day_order, columns=period_order,fill_value=0)
    return heatmap_data

