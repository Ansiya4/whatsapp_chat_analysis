import re
import pandas as pd


def preprocess(data):
    pattern = r'^(\d{1,2}/\d{1,2}/\d{2}, \d{1,2}:\d{2}\s?[AP]M) - (.+)$'
    # Add the DOTALL flag to match across multiple lines
    pattern = re.compile(pattern, re.DOTALL)
    timestamps = []
    events = []
    lines = data.splitlines()
    for entry in lines:
        message = pattern.match(entry)
        if message:
            # print("inside if")
            timestamp = message.group(1)
            event = message.group(2)
            timestamps.append(timestamp)
            events.append(event)

    # Create DataFrame from the lists
    df = pd.DataFrame({'user_message': events, 'Date': timestamps})


    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(entry[0])
    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%y, %I:%M %p')

    # Extracting individual components of the datetime
    df['day_name'] = df['Date'].dt.day_name()
    df['only_date'] = df['Date'].dt.date
    df['Month'] = df['Date'].dt.month_name()
    df['Day'] = df['Date'].dt.day
    df['Year'] = df['Date'].dt.year
    df['Hour'] = df['Date'].dt.hour
    df['Minute'] = df['Date'].dt.minute
    df['AM/PM'] = df['Date'].dt.strftime('%p')
    period = []
    for hour, am_pm in zip(df['Hour'], df['AM/PM']):
        if hour == 12:
            period.append(f'12 {am_pm} - 1 {am_pm}')
        elif hour == 11:
            period.append(f'11 {am_pm} - 12 {am_pm}')
        elif hour == 0:
            period.append(f'12 {am_pm} - 1 {am_pm}')
        else:
            period.append(f'{hour} {am_pm} - {hour + 1} {am_pm}')
    df['period'] = period

    # Dropping the original 'Date' column
    # df.drop(['Date'], axis=1, inplace=True)

    return df
