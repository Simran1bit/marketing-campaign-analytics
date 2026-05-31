import pandas as pd
import numpy as np

df = pd.read_csv('data\\marketing_campaign_data_messy.csv')

print(df.info())
# === header ===
'''
strip() - removes leading and trailing whitespace
lower() - converts all characters to lowercase
replace(" ","_") - replaces spaces with underscores
'''
print(df.columns.tolist()) #before
df.columns = df.columns.str.strip().str.lower().str.replace(" ","_")
print(df.columns.tolist()) #after

# drop duplicates
df = df.drop_duplicates(subset=['campaign_id'], keep='first') 

# === type conversion and currency cleaning (spend) ===
'''
astype(str) - converts the 'spend' column to string type
str.contains(r'\$') - checks if the string contains a dollar sign, returning a boolean
str.replace(r'[^\d.-]', '', regex=True) - removes any characters that are not digits, decimal points, or negative signs
pd.to_numeric(..., errors='coerce') - converts the cleaned string to a numeric type, coercing any errors to NaN
'''
dirty_spend = df['spend'].astype(str).str.contains(r'\$')
print(df.loc[dirty_spend, ['campaign_id','spend']]) #before
df['spend'] = df['spend'].astype(str).str.replace(r'[^\d.-]', '', regex=True)
df['spend'] =pd.to_numeric(df['spend'], errors='coerce')
print(df.loc[dirty_spend, ['campaign_id','spend']]) #after

# === categorical handling (channel) ===
print(df['channel'].unique()) #before
clean_channel = {
    'Insta_gram': 'Instagram',
    'Facebok': 'Facebook',
    'Tik_Tok': 'TikTok',
    'Gogle': 'Google Ads',
    'E-mail': 'Email',
    'N/A': np.nan
}
df['channel'] = df['channel'].replace(clean_channel)
print(df['channel'].unique()) #after
df['channel_flag'] = df['channel'].isna() # flag missing values in channel column

# === boolean handling (active) ===
print(df['active'].unique()) #before
active_bool = {
    'Y': True,
    'No': False,
    '0': False,
    '1': True,
    'Yes': True,
    'False': False,
    'True': True
}
df['active'] = df['active'].replace(active_bool)
df['active'] = df['active'].astype(bool)
print(df['active'].unique()) #after

# === date handling (start_date, end_date) ===
df['start_date'] = pd.to_datetime(df['start_date'], dayfirst = False, errors='coerce')
df['start_date_flag'] = df['start_date'].isna()
df['end_date'] = pd.to_datetime(df['end_date'], dayfirst = False, errors='coerce')

# === logical integrity (clicks, impressions) ===
'''
we had 2 columns named 'clicks' so we had to drop the duplicate columns
df.loc[] - allows us to access a group of rows and columns by labels
[:, ~df.columns.duplicated()] - selects all columns that are not duplicated

impressions = number of times the ad was shown to users
clicks = number of times users clicked on the ad
clicks > impressions is logically impossible
'''
df = df.loc[:, ~df.columns.duplicated()] # drop duplicate columns
impossible_mask = df['clicks'] > df['impressions']
print(df.loc[impossible_mask, ['campaign_id', 'clicks', 'impressions']].head()) #before + after (DF is unchanged)

# === logical integrity (start_date, end_date) ===
'''
start_date = the date when the campaign started
end_date = the date when the campaign ended
end_date < start_date is logically impossible

assumption: end_date is 30 days after start_date
pd.Timedelta(days=30) - creates a time delta of 30 days that can be added to the start_date to correct the end_date
'''
date_mask = df['end_date'] < df['start_date']
print(df.loc[date_mask, ['campaign_id', 'start_date', 'end_date']].head()) #before
df.loc[date_mask, 'end_date'] = df.loc[date_mask, 'start_date'] + pd.Timedelta(days=30)

print(df.loc[date_mask, ['campaign_id', 'start_date', 'end_date']].head()) #after

# === handling outliers (spend) ===
'''
outliers are extreme values that can skew the analysis and lead to misleading insights
upper_bound = q3 + (3 * iqr): we are using 3 times the IQR to identify outliers, 
which is an extreme threshold in data analysis. *1.5 is more common, but using 3 can help to identify more extreme outliers.
Values above this upper bound are considered outliers.

df.loc[outliers_mask, 'spend'] = upper_bound: we are capping the outlier values at the upper bound instead of removing them.
This way, we retain the data points while mitigating their impact on the analysis.
'''
q1 = df['spend'].quantile(0.25)
q3 = df['spend'].quantile(0.75)

iqr = q3 - q1
upper_bound = q3 + (3 * iqr) # 3 is a common multiplier for outliers
outliers_mask = df['spend'] > upper_bound
print(df.loc[outliers_mask, ['campaign_id', 'spend']].head()) #before
df.loc[outliers_mask, 'spend'] = upper_bound
print(df.loc[outliers_mask, ['campaign_id', 'spend']].head()) #after

# === string parsing (campaign_name)===
'''
create a new column based on existing one
r'Q\d_([^_]+)_' - regex pattern to extract the season from the campaign_name
Q\d - matches 'Q' followed by a digit (e.g., Q1, Q2, Q3, Q4)
([^_]+) - captures a group of characters that are not underscores, which represents the season name
_ - matches the underscore that follows the season name
'''
print(df['campaign_name'].head()) #before
df['season'] = df['campaign_name'].str.extract(r'Q\d_([^_]+)_')
print(df[['campaign_name', 'season']].head()) #after

# === conversions ===
'''
df.loc[df['clicks'] == 0, 'conversions'] = 0
we are setting conversions to 0 for any campaign that has 0 clicks

but the dataset shows no changes meaning that this is not the reason why we have NaN values in the conversions column
so we are going to flag the rows with NaN values in the conversions column to investigate further
'''
df['conversions_flag'] = df['conversions'].isna()


df.info() 

df.to_csv('data\\marketing_campaign_data_cleaned.csv', index=False)
