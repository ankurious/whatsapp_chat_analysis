import re
import pandas as pd


def preprocess(data):
    # Adjusted regex to capture broader formats (with or without narrow no-break space, with AM/PM)
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}(?:\u202f|\s)?[APMapm]{2}\s-\s'

    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Clean message_date column: replace special characters, strip whitespace
    df['message_date'] = df['message_date'].astype(str).str.replace('\u202f', ' ', regex=False).str.strip()

    # Flexible date parser
    def parse_date(s):
        for fmt in [
            '%d/%m/%Y, %I:%M %p -',
            '%d/%m/%y, %I:%M %p -',
            '%d/%m/%Y, %H:%M -',
            '%d/%m/%y, %H:%M -',
        ]:
            try:
                return pd.to_datetime(s, format=fmt)
            except:
                continue
        return pd.NaT

    df['message_date'] = df['message_date'].apply(parse_date)
    df = df.dropna(subset=['message_date'])

    df.rename(columns={'message_date': 'date'}, inplace=True)

    # Split into user and message
    users = []
    messages = []

    for message in df['user_message']:
        entry = re.split(r'^(.*?):\s', message, maxsplit=1)
        if len(entry) == 3:
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    # Enrich time-based features
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['month_num'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute
    df['only_date'] = df['date'].dt.date
    df['day_name'] = df['date'].dt.day_name()

    return df
