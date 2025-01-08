import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

df = pd.read_csv('funding-manifests.csv')
def extract_json_column(column_name):
    return df[column_name].apply(lambda x: json.loads(x) if isinstance(x, str) else {})
def get_project_names(row):
    try:
        manifest_json = json.loads(row['manifest_json']) if isinstance(row['manifest_json'], str) else row['manifest_json']
        return manifest_json.get('projects', [{}])[0].get('name', 'Unknown Project')
    except Exception as e:
        return 'Unknown Project'

df['project_name'] = df.apply(get_project_names, axis=1)

df['funding_requested'] = extract_json_column('manifest_json').apply(
    lambda x: sum([plan.get('amount', 0) for plan in x.get('funding', {}).get('plans', [])]) if 'funding' in x else 0
)

# Sort projects by total funding requested 
sorted_projects_df = df[['project_name', 'funding_requested']].sort_values(by='funding_requested', ascending=False)

# all projects sorted by funding requested
st.write("### All Projects Sorted by Funding Requested")
st.dataframe(sorted_projects_df)

# Display the total funding requested
total_funding_requested = df['funding_requested'].sum()
st.write(f"### Total Funding Requested: ${total_funding_requested:,.2f}")
total_projects = df['project_name'].nunique()
st.write(f"### Total Projects: {total_projects}")

# Display the spread of funding requested across the range (0 - 100k USD)
st.write("### Funding Requested Spread (0 - 100k USD)")
funding_histogram = df['funding_requested'].clip(upper=100000)
fig, ax = plt.subplots(figsize=(8, 6))
sns.histplot(funding_histogram, bins=20, kde=True, ax=ax)
ax.set_title('Funding Requested Distribution (0 - 100k USD)')
ax.set_xlabel('Funding Requested (USD)')
ax.set_ylabel('Requests')
st.pyplot(fig)

# Plotting the funding distribution by top 30 projects
st.write("### Funding Requested distribution over top 30 projects")
top_30_projects_df = sorted_projects_df.head(30)

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x='funding_requested', y='project_name', data=top_30_projects_df, ax=ax, palette='viridis')
ax.set_title('Top 30 Projects by Funding Requested')
ax.set_xlabel('Funding Requested (USD)')
ax.set_ylabel('Project Name')
st.pyplot(fig)
# Extract funding history data and explode into rows
funding_history = pd.json_normalize(df['manifest_json'].apply(lambda x: json.loads(x) if isinstance(x, str) else x).apply(
    lambda x: x.get('funding', {}).get('history', [])
).explode()).dropna()

# Pie chart for funding channels
st.write("### Funding Channel Distribution")
funding_channels = pd.json_normalize(df['manifest_json'].apply(
    lambda x: json.loads(x) if isinstance(x, str) else x).apply(
    lambda x: x.get('funding', {}).get('channels', [])
).explode()).dropna()

channel_counts = funding_channels['type'].value_counts()
fig = px.pie(channel_counts, values='count', names=channel_counts.index, title="Distribution of Funding Channels")
st.plotly_chart(fig)

