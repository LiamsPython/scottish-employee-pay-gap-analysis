import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


# ------------------- Configuration -------------------
st.set_page_config(page_title="Scottish Gender Pay Gap Dashboard", layout="wide")

# ------------------- Top -------------------
                                                                                                                                                                                                                 
                                                                                                                                                                                                                     
ascii_art = """

<pre>

  _____       _                                  _______               _     __                          
 |_   _|     (_)                                |_   __ \             / |_  [  |                         
   | |       __    ,--.    _ .--..--.    .--.     | |__) |   _   __  `| |-'  | |--.     .--.    _ .--.   
   | |   _  [  |  `'_\ :  [ `.-. .-. |  ( (`\]    |  ___/   [ \ [  ]  | |    | .-. |  / .'`\ \ [ `.-. |  
  _| |__/ |  | |  // | |,  | | | | | |   `'.'.   _| |_       \ '/ /   | |,   | | | |  | \__. |  | | | |  
 |________| [___] \'-;__/ [___||__||__] [\__) ) |_____|    [\_:  /    \__/  [___]|__]  '.__.'  [___||__] 
                                         \__.'              \__.'                                        

                                                                                                                   ⓒ 
 
 </pre>           
            
"""

st.markdown(f"""
<style>
.ascii-container {{
    overflow-x: auto;
    white-space: pre;
    font-family: monospace;
    text-align: center;
    padding: 10px;
    border: 1px solid #44444422;
    border-radius: 6px;
    background-color: transparent;
    color: #39ff14; /* optional neon green */
    font-size: 16px;
}}

@media (max-width: 1200px) {{
    .ascii-container {{
        font-size: 14px;
    }}
}}

@media (max-width: 992px) {{
    .ascii-container {{
        font-size: 12px;
    }}
}}

@media (max-width: 768px) {{
    .ascii-container {{
        font-size: 10px;
    }}
}}

@media (max-width: 480px) {{
    .ascii-container {{
        font-size: 8px;
    }}
}}
</style>

<div class="ascii-container">
{ascii_art}
</div>
""", unsafe_allow_html=True)



# ------------------- Constants -------------------

CSV_PATH = "UK_Gender_Pay_Gap_Data_2023_to_2024.csv"
SCOTTISH_CITIES = [
    'Edinburgh', 'Glasgow', 'Aberdeen', 'Dundee', 'Inverness',
    'Perth', 'Stirling', 'Falkirk', 'Ayrshire', 'Highlands'
]
COLUMNS_TO_KEEP = [
    'EmployerName', 'Address', 'DiffMeanHourlyPercent', 'DiffMedianHourlyPercent',
    'MaleTopQuartile', 'FemaleTopQuartile',
    'MaleUpperMiddleQuartile', 'FemaleUpperMiddleQuartile',
    'MaleLowerMiddleQuartile', 'FemaleLowerMiddleQuartile',
    'MaleLowerQuartile', 'FemaleLowerQuartile'
]

# ------------------- Load & Clean Data -------------------
def load_and_clean_data(path):
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        st.error(f"CSV file not found at path: `{path}`")
        st.stop()

    is_scotland = df['Address'].str.contains('|'.join(SCOTTISH_CITIES), case=False, na=False)
    filtered_df = df[is_scotland]
    available_columns = [col for col in COLUMNS_TO_KEEP if col in filtered_df.columns]
    df_cleaned = filtered_df[available_columns].copy()

    percent_cols = [col for col in df_cleaned.columns if 'Percent' in col or 'Quartile' in col]
    df_cleaned[percent_cols] = df_cleaned[percent_cols].apply(pd.to_numeric, errors='coerce')
    df_cleaned.dropna(subset=['DiffMedianHourlyPercent'], inplace=True)

    return df_cleaned

# ------------------- Charts -------------------
def plot_summary_metrics(df):
    col1, col2 = st.columns(2)
    with col1:
        st.metric("**Average Median Pay Gap**", f"{df['DiffMedianHourlyPercent'].mean():.2f}%")
    with col2:
        st.metric("**Average Mean Pay Gap**", f"{df['DiffMeanHourlyPercent'].mean():.2f}%")

def plot_median_pay_gap_bar(df):
    st.markdown(
    "<h3 style='text-align: center; font-size: 32px; color: #FFFFFF;'>Median Gender Pay Gap by Employer</h3>",
    unsafe_allow_html=True)

    max_display = st.slider("Select number of employers to display:", 5, min(100, len(df)), 20, 5)
    df_sorted = df.sort_values(by='DiffMedianHourlyPercent', ascending=False).head(max_display)
    fig, ax = plt.subplots(figsize=(10, 0.4 * max_display))
    sns.barplot(x='DiffMedianHourlyPercent', y='EmployerName', data=df_sorted, palette='coolwarm', ax=ax)
    ax.set_xlabel("Median Pay Gap (%)")
    ax.set_ylabel("Employer")
    ax.set_title(f"Top {max_display} Organisations by Median Gender Pay Gap")
    st.pyplot(fig)
    st.markdown("""
**Interpretation:**  
This bar chart displays the top employers in Scotland ranked by their **median gender pay gap**. A higher percentage indicates that, on average, women earn significantly less than men at that company. The data is sorted in descending order to highlight the most unequal organisations.
""")


def plot_quartile_pie(df):
    st.markdown(
    "<h3 style='text-align: center; font-size: 32px; color: #FFFFFF;'>Median Gender Balance in Top Pay Quartile (Average)</h3>",
    unsafe_allow_html=True)

    fig, ax = plt.subplots()
    ax.pie([
        df['FemaleTopQuartile'].mean(),
        df['MaleTopQuartile'].mean()
    ], labels=['Female', 'Male'], autopct='%1.1f%%', colors=['#ff9999', '#66b3ff'], startangle=90)
    ax.set_title("Top Quartile Representation (Average %)")
    st.pyplot(fig)
    st.markdown("""
**Interpretation:**  
This pie chart shows the **average proportion of male and female employees** in the **top 25% of earners** within each organisation. Men make up over 60% of top earners, highlighting a persistent imbalance in senior and high-paying roles that contributes to the overall gender pay gap.
""")


def plot_boxplot(df):
    st.markdown(
        "<h3 style='text-align: center; font-size: 32px; color: #FFFFFF;'>Median Distribution of Median Gender Pay Gaps</h3>",
        unsafe_allow_html=True
    )

    fig, ax = plt.subplots()
    sns.boxplot(data=df['DiffMedianHourlyPercent'], ax=ax, color="skyblue")
    ax.set_title("Boxplot of Median Gender Pay Gaps")
    ax.set_xlabel("Median Pay Gap (%)")
    st.pyplot(fig)

    st.markdown("""
**Interpretation:**  
The boxplot shows the **distribution and spread** of median gender pay gaps across Scottish employers. The box represents the interquartile range (middle 50% of values), with outliers indicating companies with extreme disparities. Gaps close to 0% suggest pay equity, while values above or below indicate bias towards one gender.
""")


def plot_quartile_bars(df):
    st.markdown(
    "<h3 style='text-align: center; font-size: 32px; color: #FFFFFF;'>Median Gender Distribution Across Pay Quartiles</h3>",
    unsafe_allow_html=True)

    quartiles = {
        'Top': ['FemaleTopQuartile', 'MaleTopQuartile'],
        'Upper Middle': ['FemaleUpperMiddleQuartile', 'MaleUpperMiddleQuartile'],
        'Lower Middle': ['FemaleLowerMiddleQuartile', 'MaleLowerMiddleQuartile'],
        'Lower': ['FemaleLowerQuartile', 'MaleLowerQuartile']
    }
    data = {"Quartile": [], "Gender": [], "Average %": []}
    for label, cols in quartiles.items():
        for gender_col in cols:
            data["Quartile"].append(label)
            data["Gender"].append("Female" if "Female" in gender_col else "Male")
            data["Average %"].append(df[gender_col].mean())
    df_q = pd.DataFrame(data)
    fig, ax = plt.subplots()
    sns.barplot(data=df_q, x="Quartile", y="Average %", hue="Gender", palette=["#ff9999", "#66b3ff"], ax=ax)
    ax.set_title("Average Gender Distribution by Pay Quartile")
    st.pyplot(fig)
    st.markdown("""
**Interpretation:**  
This chart illustrates the **average gender balance** within each pay quartile across all organisations. Men are consistently overrepresented in the top and upper-middle quartiles, while women are more prevalent in the lower ones. This suggests a structural imbalance in pay progression and promotion opportunities.
""")


def plot_heatmap(df):
    st.markdown(
    "<h3 style='text-align: center; font-size: 32px; color: #FFFFFF;'>Median Correlation Between Key Metrics</h3>",
    unsafe_allow_html=True)

    corr_cols = [col for col in df.columns if 'Percent' in col or 'Quartile' in col]
    corr_matrix = df[corr_cols].corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', ax=ax)
    ax.set_title("Correlation Heatmap of Gender Pay Metrics")
    st.pyplot(fig)
    st.markdown("""
**Interpretation:**  
This correlation heatmap identifies relationships between gender pay metrics. A **positive correlation between male representation in top quartiles and high pay gaps** implies that organisational leadership skewed towards men is linked to wider disparities. Strong **negative correlations** with female quartile metrics confirm the inverse relationship.
""")


def show_best_and_worst(df):
    st.markdown(
        "<h3 style='text-align: center; font-size: 32px; color: #FFFFFF;'>Median Employers With Most Balanced Pay</h3>",
        unsafe_allow_html=True)

    best = df.nsmallest(5, 'DiffMedianHourlyPercent')
    worst = df.nlargest(5, 'DiffMedianHourlyPercent')
    st.markdown("### Lowest Median Pay Gaps")
    st.dataframe(best[['EmployerName', 'DiffMedianHourlyPercent']])
    st.markdown("### Highest Median Pay Gaps")
    st.dataframe(worst[['EmployerName', 'DiffMedianHourlyPercent']])
    st.markdown("""
**Interpretation:**  
These tables highlight the **employers with the smallest and largest median gender pay gaps**. Organisations with gaps near 0% are closest to achieving pay equality. Conversely, those at the bottom reflect the most significant disparities, often driven by leadership and role distribution.
""")


# ------------------- Main Application -------------------
df_cleaned = load_and_clean_data(CSV_PATH)
st.markdown("<h1 style='text-align: center; font-size: 72px;'>Scottish Employment Gender Pay Gap (2023–2024)</h1>", unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center; font-size: 30px;'>
This dashboard explores the <strong>MEDIAN</strong> and <strong>MEAN</strong> gender pay gaps in Scottish organisations based on the UK Government's 2023–2024 disclosure data.
</div>
""",unsafe_allow_html=True)
st.caption("Data Source: [UK Gov Gender Pay Gap Service](https://gender-pay-gap.service.gov.uk/)")
st.caption("Date Last Updated: June 2024")
st.success(f"Loaded data for **{len(df_cleaned)}** Scottish employers.")

with st.expander("Show Raw Filtered Data"):
    st.dataframe(df_cleaned)

with st.expander("ℹData Summary"):
    st.write(df_cleaned.describe())

plot_summary_metrics(df_cleaned)
plot_median_pay_gap_bar(df_cleaned)
plot_quartile_pie(df_cleaned)
plot_boxplot(df_cleaned)
plot_quartile_bars(df_cleaned)
plot_heatmap(df_cleaned)
show_best_and_worst(df_cleaned)
