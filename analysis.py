import pandas as pd
import os
import matplotlib.pyplot as plt

def graph(chart_type, x, y, xlabel, ylabel, title):
    plt.figure(figsize=(6,6))
    if chart_type == "bar":
        plt.bar(x, y)
    elif chart_type == "line":
        plt.plot(x, y, marker='o')
    elif chart_type == "barh":
        plt.barh(x, y)
    elif chart_type == "scatter":
        plt.scatter(x, y)
    elif chart_type == "pie":
        plt.pie(y, labels = x, autopct='%1.1f%%')
    
    if chart_type != "pie":
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.gca().set_axisbelow(True) 
    
    plt.title(title)
    plt.tight_layout()
    safe_title = title.lower().replace(" ", "_")
    os.makedirs("images", exist_ok=True)
    plt.savefig(f"images\\{safe_title}.png")
    plt.show()

full_df = pd.read_csv('data\\marketing_campaign_data_cleaned.csv')
df = full_df.copy()

# 1. channel with highest conversion
df = df[~df['channel_flag']]
df = df[~df['conversions_flag']]
channel_conversion = df.groupby('channel')['conversions'].sum()
print(f'1. {channel_conversion.sort_values(ascending=False).index[0]} generated the highest conversions.')
graph('bar', channel_conversion.index, channel_conversion.values, 'Channel', 'Conversions', 'Conversion by Channel')

# 2. channel with highest spend
channel_spend = df.groupby('channel')['spend'].sum()
print(f'2. {channel_spend.sort_values(ascending=False).index[0]} had highest spend.')
graph('barh', channel_spend.index, channel_spend.values, 'Channel', 'Spend', 'Spend by Channel')

# 3. campaigns with poor ROI
df = df[df['spend']>0]
df['roi'] = df['conversions'] / df['spend']
poor_campaigns = df.sort_values('roi').iloc[0]
print(f'3. {poor_campaigns["campaign_name"]} had poor ROI of {poor_campaigns["roi"]:.2f}.')
graph('scatter', df['spend'], df['conversions'], 'Spend', 'Conversions', 'Conversions vs Spend')

# 4. channel with highest engagement
df = df[df['impressions']>0]
df['ctr'] = df['clicks'] / df['impressions']
channel_engagement = df.groupby('channel')['ctr'].mean()
print(f'4. {channel_engagement.sort_values(ascending=False).index[0]} had the highest engagement (CTR).')
graph('bar', channel_engagement.index, channel_engagement.values, 'Channel', 'CTR', 'Engagement by Channel')

# 5. best performing season
best_seasons = df.groupby('season')['roi'].mean()
print(f'5. {best_seasons.sort_values(ascending=False).index[0]} is the best performing season.')
graph('pie', best_seasons.index, best_seasons.values, 'Seasons', 'ROI', 'ROI by Seasons')

# 6. campaign duration analysis
df = df[~df['start_date_flag']]
df['start_date'] = pd.to_datetime(df['start_date'])
df['end_date'] = pd.to_datetime(df['end_date'])
campaign_duration = (df['end_date'] - df['start_date']).dt.days
correlation = campaign_duration.corr(df['conversions'])
print(f'6. Correlation between campaign duration and conversions: {correlation:.2f}.')
if correlation < -0.3:
    print('Campaign duration has a moderate to strong negative relationship with conversions.')
elif correlation < 0.3:
    print('Campaign duration has little to no relationship with conversions.')
else:
    print('Campaign duration has a positive relationship with conversions.')
graph('scatter', campaign_duration, df['conversions'], 'Campaign Duration (days)', 'Conversions', 'Conversions vs Campaign Duration')

# 7. active vs inactive campaign performance
performance = df.groupby('active')[['conversions', 'spend', 'ctr']].mean()
print(performance)
if(performance.loc[True, 'conversions'] > performance.loc[False, 'conversions']):
    print('7. Active campaigns generate more conversions.')
else:
    print('7. Inactive campaigns generate more conversions.')

if(performance.loc[True, 'spend'] > performance.loc[False, 'spend']):
    print('   Active campaigns spend more money.') 
else:
    print('   Inactive campaigns spend more money.')

if(performance.loc[True, 'ctr'] > performance.loc[False, 'ctr']):
    print('   Active campaigns have higher average CTR.')
else:
    print('   Inactive campaigns have higher average CTR.')

# 8. missing channel investigation
full_df['roi'] = full_df['conversions'] / full_df['spend']
missing_channel = full_df[full_df['channel_flag']]
normal_channel = full_df[~full_df['channel_flag']]
if(missing_channel['conversions'].mean() > normal_channel['conversions'].mean()):
    print('8. Missing channel campaigns were more successful in generating conversions.')
else:
    print('8. Missing channel campaigns were less successful in generating conversions.')
if(missing_channel['spend'].mean()> normal_channel['spend'].mean()):
    print('   Missing channel campaigns had higher average spend.')
else:
    print('   Missing channel campaigns had lower average spend.')
if(missing_channel['roi'].mean() > normal_channel['roi'].mean()):
    print('   Missing channel campaigns behaved better in comparison to normal channels.')
else:
    print('   Missing channel campaigns behaved worse in comparison to normal channels.')

# 9. outlier campaign investigation
'''
Spend outliers were capped during preprocessing to reduce their influence on analysis. 
Since no outlier flag was retained, individual outlier campaigns cannot be identified in the cleaned dataset.
'''

# 10. conversion efficiency
df = df[df['clicks']>0]
df['conversion_rate'] = df['conversions'] / df['clicks']
best_channel = df.groupby('channel')['conversion_rate'].mean().sort_values(ascending=False)
print(f'10. {best_channel.index[0]} is the best converting channel.')
print(f'   {df.sort_values("conversion_rate").head(5)["campaign_name"].tolist()} are the campaigns which waste clicks.')

# 11. budget efficiency tiers
df['budget_tier'] = pd.cut(df['spend'], bins = [0,1000,5000,float('inf')], labels = ['Low Budget', 'Medium Budget', 'High Budget'])
budget_analysis = df.groupby('budget_tier')[['ctr', 'conversions', 'roi']].mean()
print('11. Budget Efficiency Tiers:')
print(budget_analysis)
graph('bar', budget_analysis.index, budget_analysis['ctr'], 'Budget Tier', 'Average CTR', 'CTR by Budget Tier')
graph('bar', budget_analysis.index, budget_analysis['conversions'], 'Budget Tier', 'Average Conversions', 'Conversions by Budget Tier')
graph('bar', budget_analysis.index, budget_analysis['roi'], 'Budget Tier', 'Average ROI', 'ROI by Budget Tier')
print('   High budget campaigns have the highest average CTR and conversions,\n   but low budget campaigns have the highest average ROI,\n   indicating better cost efficiency.')
