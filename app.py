import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression
import numpy as np

# --- Page Config & Theme ---
st.set_page_config(
    page_title="Aswini Diagnostic Services Dashboard",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- CSS Design System ---
css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    /* Wisteria Bloom Palette */
    --lavender: #D3D3FF;
    --deep-violet: #9400D3;
    --dusty-lavender: #D8BFD8;
    --wisteria-pink: #ED80E9;
    
    --bg-main: #FCFCFF; /* Extremely light lavender-tinted white for generous whitespace */
    --surface-white: #FFFFFF;
    --text-primary: #1A1A24;
    --text-secondary: #5F5F6E;
    --border-soft: #EAEAF2;
    --radius-soft: 12px;
    --shadow-subtle: 0 4px 12px rgba(148, 0, 211, 0.06);
    --shadow-hover: 0 6px 16px rgba(148, 0, 211, 0.12);
}

header[data-testid="stHeader"], #MainMenu, footer, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"], .stDeployButton {
    display: none !important;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main, .block-container, section[data-testid="stMain"] {
    background-color: var(--bg-main) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}
.block-container {
    padding: 2rem 2.5rem 3rem !important;
    max-width: 1400px !important;
}

/* Sticky Tabs */
[data-testid="stTabs"] > div:first-child, [data-baseweb="tab-list"] {
    position: sticky !important;
    top: 0px !important;
    z-index: 999 !important;
    background-color: var(--bg-main) !important;
    padding-top: 10px;
}

/* Elegant KPI Cards */
.metric-card { 
    background: var(--surface-white); 
    border: 1px solid var(--border-soft); 
    border-radius: var(--radius-soft); 
    padding: 1.5rem; 
    box-shadow: var(--shadow-subtle);
    height: 100%;
}
.metric-label { font-size: 0.85rem; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;}
.metric-value { font-size: 2rem; font-weight: 700; color: var(--deep-violet); line-height: 1.1; }

/* Clean Chart Wraps */
.chart-wrap { 
    background: var(--surface-white); 
    border: 1px solid var(--border-soft); 
    border-radius: var(--radius-soft); 
    padding: 1.5rem; 
    box-shadow: var(--shadow-subtle); 
    margin-bottom: 1.5rem; 
}
.chart-title { font-size: 1.1rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.5rem; }

/* Readable Tables */
.data-table { width: 100%; border-collapse: separate; border-spacing: 0; font-size: 0.9rem; margin-bottom: 1.5rem; }
.data-table th { text-align: left; padding: 1rem; color: var(--deep-violet); font-weight: 600; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.02em; border-bottom: 2px solid var(--lavender); background: var(--surface-white); }
.data-table td { padding: 0.85rem 1rem; color: var(--text-primary); border-bottom: 1px solid var(--border-soft); background: var(--surface-white); }
.data-table tr:last-child td { border-bottom: none; }
.data-table tr:hover td { background-color: var(--lavender); color: var(--deep-violet); transition: background-color 0.15s ease; }

/* Inputs and Filters */
[data-baseweb="select"] > div, [data-baseweb="input"] > div, [data-testid="stCheckbox"] > div {
    border: 1px solid var(--lavender) !important;
    border-radius: 8px !important;
    background: var(--surface-white) !important;
    transition: border-color 0.2s ease;
}
[data-baseweb="select"] > div:focus-within, [data-baseweb="input"] > div:focus-within {
    border-color: var(--deep-violet) !important;
}

/* Fix text visibility for Filter Labels, Checkboxes, and Inputs */
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p,
[data-testid="stCheckbox"] label span,
.stCheckbox p {
    color: #111111 !important;
}

[data-baseweb="input"] input, 
[data-baseweb="select"] div,
[data-baseweb="select"] span {
    color: #111111 !important;
}

/* Secondary text for descriptions/helpers */
small, .st-bb, .st-bd {
    color: #333333 !important;
}

.brand-name { font-size: 1.4rem; font-weight: 700; color: var(--deep-violet); vertical-align: middle; margin-left: 12px; letter-spacing: -0.01em;}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# --- Plotly Configuration ---
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#5F5F6E", size=13),
    margin=dict(l=0, r=0, t=10, b=0),
    xaxis=dict(
        gridcolor="#EAEAF2",
        zerolinecolor="#EAEAF2",
        tickfont=dict(size=12, color="#5F5F6E"),
    ),
    yaxis=dict(
        gridcolor="#EAEAF2",
        zerolinecolor="#EAEAF2",
        tickfont=dict(size=12, color="#5F5F6E"),
    ),
    colorway=["#9400D3", "#ED80E9", "#D8BFD8"] # Deep Violet, Pink, Dusty Lavender
)

def metric_card(label, value):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

def render_table(df, key):
    df = df.copy()
    df.insert(0, 'Position', range(1, len(df) + 1))
    
    search_term = st.text_input("🔍 Filter Table:", key=f"search_{key}")
    if search_term:
        mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
        df = df[mask]
        
    st.dataframe(df, use_container_width=True, hide_index=True)

# --- Header ---
st.markdown("""
<div class="brand" style="display:flex; align-items:center; justify-content: center; width: 100%; background: var(--surface-white); padding: 15px 20px; border-radius: var(--radius-soft); box-shadow: var(--shadow-subtle); border: 1px solid var(--border-soft);">
    <img src="https://www.aswinicalicut.net/assets/img/logo/logo.png" height="55" style="object-fit:contain; margin-right: 15px;"/>
    <span class="brand-name" style="font-size: 2.2rem; font-weight: 800; letter-spacing: 0.02em;">ADS - DOCTORS ANALYSIS</span>
</div>
""", unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_data
def load_data():
    df = pd.read_pickle('dashboard_data.pkl')
    df.rename(columns={'Degree': 'Qualification'}, inplace=True)
    outliers_df = pd.read_pickle('outliers_data.pkl')
    
    # Expand tests array for easier analysis
    test_rows = []
    for _, row in df.iterrows():
        for t in row['Tests']:
            test_rows.append({
                'Month': row['Month'],
                'Doctor Name': row['Doctor Name'],
                'Qualification': row['Qualification'],
                'Mark_Exec': row['Mark_Exec'],
                'Total Volume': row['Total Volume'],
                'Total Amount': row['Total Amount'],
                'Test Name': t['Test Name'],
                'Test Count': t['Count'],
                'Test Amount': t['Amount']
            })
    test_df = pd.DataFrame(test_rows)
    
    # Generate Month sorting key
    month_order = ['August 2025', 'September 2025', 'October 2025', 'November 2025', 'December 2025', 
                   'January 2026', 'February 2026', 'March 2026', 'April 2026', 'May 2026', 'June 2026', 'July 2026']
    df['Month_Idx'] = df['Month'].apply(lambda x: month_order.index(x) if x in month_order else 99)
    test_df['Month_Idx'] = test_df['Month'].apply(lambda x: month_order.index(x) if x in month_order else 99)
    
    try:
        self_df = pd.read_pickle('self_data.pkl')
        self_df['Month_Idx'] = self_df['Month'].apply(lambda x: month_order.index(x) if x in month_order else 99)
    except Exception:
        self_df = pd.DataFrame(columns=['Month', 'Test Name', 'Test Count', 'Test Amount', 'Month_Idx'])
        
    return df, test_df, outliers_df, self_df, month_order

try:
    df_full, test_df_full, outliers_df_full, self_df_full, month_order = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}. Please ensure data_prep.py has been run.")
    st.stop()

# Callbacks for Select All functionality
def handle_select_all(key_prefix):
    select_all_val = st.session_state.get(f"{key_prefix}_select_all", True)
    for i in range(len(month_order)):
        st.session_state[f"{key_prefix}_m_{i}"] = select_all_val

def handle_month_change(key_prefix):
    all_checked = all(st.session_state.get(f"{key_prefix}_m_{i}", True) for i in range(len(month_order)))
    st.session_state[f"{key_prefix}_select_all"] = all_checked

# Helper function to render section-specific filters
def render_filters(key_prefix):
    st.markdown("##### Select Month and Top N Doctors")
    
    # Initialize states if not present
    if f"{key_prefix}_select_all" not in st.session_state:
        st.session_state[f"{key_prefix}_select_all"] = True
        for i in range(len(month_order)):
            st.session_state[f"{key_prefix}_m_{i}"] = True

    # Select All Checkbox
    st.checkbox("Select All Months", key=f"{key_prefix}_select_all", on_change=handle_select_all, args=(key_prefix,))
    
    # Checkbox layout for months
    cols = st.columns(6)
    selected_months = []
    for i, m in enumerate(month_order):
        if cols[i % 6].checkbox(m, key=f"{key_prefix}_m_{i}", on_change=handle_month_change, args=(key_prefix,)):
            selected_months.append(m)
            
    top_n = st.number_input("Top N items to analyze:", min_value=5, max_value=200, value=50, step=5, key=f"{key_prefix}_topn")
    
    if not selected_months:
        st.warning("Please select at least one month.")
        return [], 0, None, None, None
        
    f_df = df_full[df_full['Month'].isin(selected_months)]
    f_test_df = test_df_full[test_df_full['Month'].isin(selected_months)]
    f_self_df = self_df_full[self_df_full['Month'].isin(selected_months)]
    
    f_monthly_doc_summary = f_df.groupby(['Doctor Name', 'Month', 'Month_Idx', 'Qualification', 'Mark_Exec'], dropna=False).agg({
        'Total Amount': 'sum',
        'Total Volume': 'sum'
    }).reset_index()
    
    return selected_months, top_n, f_df, f_test_df, f_self_df, f_monthly_doc_summary


# Tabs
t1, t_walkin, t2, t3, t4, t5, t6, t7, t8 = st.tabs([
    "Top N Doctors", 
    "Patient Source Analysis",
    "Unassigned Steady Docs", 
    "Top N Tests", 
    "Growth Forecast", 
    "Churn & Drop Analysis",
    "Top Tests & Strategy",
    "Outliers (Institutions)",
    "Doctor Test Share"
])

# --- Tab 1: Top N Doctors ---
with t1:
    selected_months, top_n, df, test_df, self_df, monthly_doc_summary = render_filters("t1")
    if selected_months:
        st.markdown(f"### Top {top_n} Doctors (10,000+ amount in most months)")
        
        high_value = monthly_doc_summary[monthly_doc_summary['Total Amount'] >= 10000]
        doc_month_counts = high_value.groupby('Doctor Name').size()
        threshold = max(1, len(selected_months) // 2)
        steady_docs = doc_month_counts[doc_month_counts >= threshold].index
        
        steady_doc_totals = monthly_doc_summary[monthly_doc_summary['Doctor Name'].isin(steady_docs)].groupby('Doctor Name')['Total Amount'].sum()
        top_n_steady = steady_doc_totals.nlargest(top_n).reset_index()
        
        c1, c2, c3 = st.columns(3)
        with c1: metric_card("Total Doctors Meeting Criteria", f"{len(top_n_steady)}")
        with c2: metric_card("Selected Months", f"{len(selected_months)}")
        with c3: 
            if not top_n_steady.empty:
                metric_card("Revenue from these Docs", f"₹{top_n_steady['Total Amount'].sum():,.0f}")
            else:
                metric_card("Revenue from these Docs", "₹0")
        
        if not top_n_steady.empty:
            st.markdown("""<div class="chart-wrap"><div class="chart-title">Revenue from Top Steady Doctors</div>""", unsafe_allow_html=True)
            fig = px.bar(top_n_steady.head(15), x='Doctor Name', y='Total Amount', color_discrete_sequence=['#9400D3'])
            fig.update_layout(PLOT_LAYOUT)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)
            
            top_n_details = pd.merge(top_n_steady, monthly_doc_summary[['Doctor Name', 'Qualification', 'Mark_Exec']].drop_duplicates(subset=['Doctor Name']), on='Doctor Name', how='left')
            top_n_details['Mark_Exec'] = top_n_details['Mark_Exec'].fillna("Unassigned")
            top_n_details['Total Amount'] = top_n_details['Total Amount'].apply(lambda x: f"₹{x:,.2f}")
            render_table(top_n_details, key="t1")
        else:
            st.info("No doctors met the criteria in the selected time period.")

# --- Tab Walkin: Patient Source Analysis ---
with t_walkin:
    selected_months, top_n, df, test_df, self_df, monthly_doc_summary = render_filters("t_walkin")
    if selected_months:
        from patient_source_tab import render_patient_source_tab
        render_patient_source_tab(selected_months, top_n, df, test_df, self_df, monthly_doc_summary, month_order, metric_card, render_table)

# --- Tab 2: Unassigned Steady Docs (>25,000 Total in Period) ---
with t2:
    st.markdown("### Doctors without Marketing Executive (>25,000 Total Billed Amount)")
    st.markdown("*(This section analyzes the entire dataset year across all months)*")
    
    unassigned = df_full[df_full['Mark_Exec'].isna()]
    
    # Check for total bill amount exceeding 25000 in the entire period
    unassigned_totals = unassigned.groupby('Doctor Name')['Total Amount'].sum().reset_index()
    unassigned_totals = unassigned_totals[unassigned_totals['Total Amount'] > 25000]
    unassigned_totals = unassigned_totals.sort_values(by='Total Amount', ascending=False)
    
    c1, c2 = st.columns(2)
    with c1: metric_card("Unassigned Steady Doctors", f"{len(unassigned_totals)}")
    with c2:
        if not unassigned_totals.empty:
            metric_card("Potential Retained Revenue", f"₹{unassigned_totals['Total Amount'].sum():,.0f}")
        else:
            metric_card("Potential Retained Revenue", "₹0")
    
    if not unassigned_totals.empty:
        unassigned_details = pd.merge(unassigned_totals, df_full[['Doctor Name', 'Qualification']].drop_duplicates(subset=['Doctor Name']), on='Doctor Name', how='left')
        unassigned_details['Total Amount'] = unassigned_details['Total Amount'].apply(lambda x: f"₹{x:,.2f}")
        render_table(unassigned_details, key="t2")
    else:
        st.info("No unassigned doctors met the >₹25,000 criteria in the entire dataset.")

# --- Tab 3: Top N Tests ---
with t3:
    selected_months, top_n, df, test_df, self_df, monthly_doc_summary = render_filters("t3")
    if selected_months:
        st.markdown(f"### Top {top_n} Tests Sent by Top {top_n} Supporting Doctors")
        overall_top_n = monthly_doc_summary.groupby('Doctor Name')['Total Amount'].sum().nlargest(top_n).index
        
        top_docs_tests = test_df[test_df['Doctor Name'].isin(overall_top_n)]
        top_n_tests = top_docs_tests.groupby('Test Name')['Test Count'].sum().nlargest(top_n).sort_values(ascending=True).reset_index()
        
        c1, c2 = st.columns(2)
        with c1: metric_card(f"Total Tests by Top {top_n} Docs", f"{top_docs_tests['Test Count'].sum():,.0f}")
        
        if not top_n_tests.empty:
            st.markdown(f"""<div class="chart-wrap"><div class="chart-title">Top {top_n} Tests Breakdown (Ascending)</div>""", unsafe_allow_html=True)
            fig2 = px.bar(top_n_tests, x='Test Count', y='Test Name', orientation='h', height=max(400, top_n * 20), color_discrete_sequence=['#9400D3'])
            fig2.update_layout(PLOT_LAYOUT)
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("#### View Top 5 Doctors for a Specific Test")
            selected_test = st.selectbox("Select a test:", top_n_tests['Test Name'].sort_values().tolist())
            if selected_test:
                test_specific_df = top_docs_tests[top_docs_tests['Test Name'] == selected_test]
                top_5_docs_test = test_specific_df.groupby('Doctor Name')['Test Count'].sum().nlargest(5).reset_index()
                render_table(top_5_docs_test, key="t3")
        else:
            st.info("No test data available for the selected top doctors.")

# --- Tab 4: Growth Forecasting ---
with t4:
    selected_months, top_n, df, test_df, self_df, monthly_doc_summary = render_filters("t4")
    if selected_months:
        st.markdown(f"### 🔮 August 2027 Top {top_n} Projection")
        st.markdown("This model analyzes the **full year's historical pattern** for each doctor to predict their monthly performance 12 months into the future (August 2027). Doctors require at least 5 months of historical data to generate a stable forecast.")
        
        forecast_records = []
        # Use the full dataset to ensure a stable 12-month projection regardless of local tab filters
        full_monthly_summary = df_full.groupby(['Doctor Name', 'Month_Idx', 'Qualification', 'Mark_Exec'], dropna=False).agg({
            'Total Amount': 'sum',
            'Total Volume': 'sum'
        }).reset_index()
        
        valid_docs_full = full_monthly_summary.groupby('Doctor Name').size()
        valid_docs_full = valid_docs_full[valid_docs_full >= 5].index
        
        for doc in valid_docs_full:
            doc_data = full_monthly_summary[full_monthly_summary['Doctor Name'] == doc].sort_values('Month_Idx')
            X = doc_data['Month_Idx'].values.reshape(-1, 1)
            y_amt = doc_data['Total Amount'].values
            y_vol = doc_data['Total Volume'].values
            
            model_amt = LinearRegression().fit(X, y_amt)
            model_vol = LinearRegression().fit(X, y_vol)
            
            # Predict for August 2027 (Month Index = 24, since Aug 2025 is 0)
            proj_amt = max(0, model_amt.predict([[24]])[0])
            proj_vol = max(0, model_vol.predict([[24]])[0])
            
            if proj_amt > 0:
                growth_val = model_amt.coef_[0]
                if growth_val > 0:
                    remark = "🟢 ▲ Growth"
                elif growth_val < 0:
                    remark = "🔴 ▼ Drop"
                else:
                    remark = "⚪ — Stable"
                    
                forecast_records.append({
                    'Doctor Name': doc,
                    'Qualification': doc_data['Qualification'].iloc[0],
                    'Mark_Exec': doc_data['Mark_Exec'].iloc[0],
                    'Historical Avg (₹)': y_amt.mean(),
                    'Growth Trend (₹/mo)': growth_val,
                    'Performance Remark': remark,
                    'Projected Vol (Aug 2027)': int(proj_vol),
                    'Projected Amt (Aug 2027)': proj_amt
                })
                
        forecast_df = pd.DataFrame(forecast_records)
        if not forecast_df.empty:
            forecast_df = forecast_df.sort_values(by='Projected Amt (Aug 2027)', ascending=False).head(top_n)
            
            c1, c2 = st.columns(2)
            with c1: metric_card("Doctors Forecasted", f"{len(forecast_df)}")
            with c2: metric_card("Projected Revenue (Aug 2027)", f"₹{forecast_df['Projected Amt (Aug 2027)'].sum():,.0f}")
            
            st.markdown(f"""<div class="chart-wrap"><div class="chart-title">Top {top_n} Projected Doctors (August 2027)</div>""", unsafe_allow_html=True)
            fig3 = px.bar(forecast_df, x='Doctor Name', y='Projected Amt (Aug 2027)', color_discrete_sequence=['#ED80E9'])
            fig3.update_layout(PLOT_LAYOUT)
            st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)
            
            forecast_df['Mark_Exec'] = forecast_df['Mark_Exec'].fillna("Unassigned")
            forecast_df['Historical Avg (₹)'] = forecast_df['Historical Avg (₹)'].apply(lambda x: f"₹{x:,.2f}")
            forecast_df['Growth Trend (₹/mo)'] = forecast_df['Growth Trend (₹/mo)'].apply(lambda x: f"₹{x:,.2f}")
            forecast_df['Projected Amt (Aug 2027)'] = forecast_df['Projected Amt (Aug 2027)'].apply(lambda x: f"₹{x:,.2f}")
            
            forecast_df = forecast_df[['Doctor Name', 'Qualification', 'Mark_Exec', 'Historical Avg (₹)', 'Growth Trend (₹/mo)', 'Performance Remark', 'Projected Vol (Aug 2027)', 'Projected Amt (Aug 2027)']]
            
            st.markdown("""<div class="chart-wrap"><div class="chart-title">Forecast Data Table</div>""", unsafe_allow_html=True)
            render_table(forecast_df, key="t4")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Insufficient data to generate 2027 projections.")

# --- Tab 5: Churn & Drop Analysis ---
with t5:
    selected_months, top_n, df, test_df, self_df, monthly_doc_summary = render_filters("t5")
    if selected_months:
        st.markdown("### Support Pattern Drops & Sensitive Issues")
        st.markdown("Compares average support in the first half of the selected period vs the second half.")
        
        if len(selected_months) < 2:
            st.warning("Please select at least 2 months to calculate drop analysis.")
        else:
            half_idx = len(selected_months) // 2
            early_months = selected_months[:half_idx]
            late_months = selected_months[half_idx:]
            
            valid_docs = monthly_doc_summary.groupby('Doctor Name').size()
            valid_docs = valid_docs[valid_docs >= 3].index
            
            drop_records = []
            for doc in valid_docs:
                doc_data = monthly_doc_summary[monthly_doc_summary['Doctor Name'] == doc]
                early = doc_data[doc_data['Month'].isin(early_months)]['Total Amount'].mean()
                late = doc_data[doc_data['Month'].isin(late_months)]['Total Amount'].mean()
                
                if pd.isna(late): late = 0
                if pd.isna(early): continue
                
                if early > 3000 and (early - late) > 2000:
                    drop_records.append({
                        'Doctor Name': doc,
                        'Performance Remark': '🔴 ▼ Drop',
                        'Early Avg (₹)': early,
                        'Late Avg (₹)': late,
                        'Drop Amount (₹)': early - late
                    })
                    
            drop_df = pd.DataFrame(drop_records)
            if not drop_df.empty:
                drop_df = drop_df.sort_values(by='Drop Amount (₹)', ascending=False)
                
                c1, c2 = st.columns(2)
                with c1: metric_card("Doctors With Drops", f"{len(drop_df)}")
                
                st.markdown("#### Doctors with Significant Drops")
                selected_drop_doc = st.selectbox("Select a doctor to see test-level drop details:", drop_df['Doctor Name'].tolist())
                
                if selected_drop_doc:
                    doc_tests = test_df[test_df['Doctor Name'] == selected_drop_doc]
                    early_tests = doc_tests[doc_tests['Month'].isin(early_months)].groupby('Test Name')['Test Count'].mean()
                    late_tests = doc_tests[doc_tests['Month'].isin(late_months)].groupby('Test Name')['Test Count'].mean()
                    
                    test_diff = pd.DataFrame({
                        'Early Avg Count': early_tests,
                        'Late Avg Count': late_tests
                    }).fillna(0)
                    test_diff['Drop Count'] = test_diff['Early Avg Count'] - test_diff['Late Avg Count']
                    test_diff = test_diff[test_diff['Drop Count'] > 0].sort_values(by='Drop Count', ascending=False).reset_index()
                    
                    if not test_diff.empty:
                        st.markdown(f"**Sensitive Tests Drop for {selected_drop_doc}**")
                        render_table(test_diff.head(10), key="t5_1")
                    
                drop_df = pd.merge(drop_df, monthly_doc_summary[['Doctor Name', 'Qualification', 'Mark_Exec']].drop_duplicates(subset=['Doctor Name']), on='Doctor Name', how='left')
                drop_df['Mark_Exec'] = drop_df['Mark_Exec'].fillna("Unassigned")
                drop_df['Early Avg (₹)'] = drop_df['Early Avg (₹)'].apply(lambda x: f"₹{x:,.2f}")
                drop_df['Late Avg (₹)'] = drop_df['Late Avg (₹)'].apply(lambda x: f"₹{x:,.2f}")
                drop_df['Drop Amount (₹)'] = drop_df['Drop Amount (₹)'].apply(lambda x: f"₹{x:,.2f}")
                
                # Reorder columns for presentation
                drop_df = drop_df[['Doctor Name', 'Qualification', 'Mark_Exec', 'Performance Remark', 'Early Avg (₹)', 'Late Avg (₹)', 'Drop Amount (₹)']]
                
                render_table(drop_df, key="t5_2")
            else:
                st.info("No significant drops detected in the selected period.")

# --- Tab 6: Top N Tests & Strategies ---
with t6:
    selected_months, top_n, df, test_df, self_df, monthly_doc_summary = render_filters("t6")
    if selected_months:
        st.markdown(f"### Top {top_n} Tests & Growth Strategies")
        
        test_totals = test_df.groupby('Test Name').agg({'Test Count': 'sum', 'Test Amount': 'sum'}).reset_index()
        top_n_tests_overall = test_totals.nlargest(top_n, 'Test Amount').copy()
        
        c1, c2 = st.columns(2)
        with c1: metric_card(f"Total Tests Performed", f"{test_totals['Test Count'].sum():,.0f}")
        with c2: metric_card(f"Total Test Revenue", f"₹{test_totals['Test Amount'].sum():,.0f}")
        
        mid_idx = len(top_n_tests_overall) // 2
        top_performers = top_n_tests_overall.iloc[:mid_idx].copy()
        underperformers = top_n_tests_overall.iloc[mid_idx:].copy()
        
        def get_common_degrees(test_name):
            d_df = test_df[test_df['Test Name'] == test_name]
            degrees = d_df['Qualification'].replace('', np.nan).dropna().value_counts()
            if not degrees.empty:
                return ", ".join(degrees.head(3).index.tolist())
            return "N/A"
            
        top_performers['Qualification of Prescribers'] = top_performers['Test Name'].apply(get_common_degrees)
        underperformers['Qualification of Prescribers'] = underperformers['Test Name'].apply(get_common_degrees)
        
        top_performers['Test Amount'] = top_performers['Test Amount'].apply(lambda x: f"₹{x:,.2f}")
        underperformers['Test Amount'] = underperformers['Test Amount'].apply(lambda x: f"₹{x:,.2f}")
        
        st.markdown("#### 🌟 Top Performing Tests (High Volume/Amount)")
        st.markdown("**Strategy:** Create package bundles with these anchor tests, ensure high availability of reagents, and assign dedicated marketing execs to doctors prescribing these to ensure retention.")
        
        if not top_performers.empty:
            fig_top = px.bar(top_performers.sort_values(by='Test Amount', ascending=True), x='Test Amount', y='Test Name', orientation='h', color_discrete_sequence=['#9400D3'], height=max(300, len(top_performers)*35))
            fig_top.update_layout(PLOT_LAYOUT)
            st.markdown("""<div class="chart-wrap">""", unsafe_allow_html=True)
            st.plotly_chart(fig_top, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)
            render_table(top_performers, key="t6_1")
            
        st.markdown("---")
        
        st.markdown("#### 📈 High Potential Tests (Lower Volume, Strong Base)")
        st.markdown("**Strategy:** Offer temporary promotional discounts or run educational CMEs for doctors matching the 'Qualification of Prescribers' to raise awareness of clinical utility.")
        
        if not underperformers.empty:
            fig_under = px.bar(underperformers.sort_values(by='Test Amount', ascending=True), x='Test Amount', y='Test Name', orientation='h', color_discrete_sequence=['#ED80E9'], height=max(300, len(underperformers)*35))
            fig_under.update_layout(PLOT_LAYOUT)
            st.markdown("""<div class="chart-wrap">""", unsafe_allow_html=True)
            st.plotly_chart(fig_under, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)
            render_table(underperformers, key="t6_2")

# --- Tab 7: Outliers (Institutions) ---
with t7:
    st.markdown("### Outlier Institutions (MCH, BMH, KMCT, etc.)")
    st.markdown("These entries are institutions or labs (B2B Matrix) and were excluded from the main doctors analysis.")
    
    selected_months, top_n, df, test_df, self_df, monthly_doc_summary = render_filters("t7")
    if selected_months:
        f_outliers = outliers_df_full[outliers_df_full['Month'].isin(selected_months)]
        
        # We need to extract tests for the outliers for the requested test analysis table
        outlier_test_rows = []
        for _, row in f_outliers.iterrows():
            for t in row['Tests']:
                outlier_test_rows.append({
                    'Month': row['Month'],
                    'Institution': row['Doctor Clean'],
                    'Test Name': t['Test Name'],
                    'Test Count': t['Count'],
                    'Test Amount': t['Amount']
                })
        
        o_test_df = pd.DataFrame(outlier_test_rows) if outlier_test_rows else pd.DataFrame()
        
        # Institution summary
        outlier_summary = f_outliers.groupby('Doctor Clean').agg({'Total Amount': 'sum', 'Total Volume': 'sum'}).reset_index()
        outlier_totals = outlier_summary.sort_values(by='Total Amount', ascending=False).head(top_n)
        
        c1, c2 = st.columns(2)
        with c1: metric_card("Total Outlier Institutions", f"{len(outlier_summary)}")
        with c2: 
            if not outlier_summary.empty:
                metric_card("Total Outlier Revenue", f"₹{outlier_summary['Total Amount'].sum():,.0f}")
        
        st.markdown(f"#### Top {top_n} Institutions by Revenue")
        outlier_display = outlier_totals.copy()
        outlier_display['Total Amount'] = outlier_display['Total Amount'].apply(lambda x: f"₹{x:,.2f}")
        if not outlier_display.empty:
            render_table(outlier_display, key="t7_inst")
        else:
            st.info("No outliers found in the selected period.")
            
        st.markdown("---")
        st.markdown(f"### B2B Matrix: Range of Tests Billed by Top {top_n} Institutions")
        st.markdown("Detailed breakdown of tests referred by these institutions. Includes the total volume of individual tests, total amount billed, number of unique institutions prescribing it, and the months it was billed in.")
        
        if not o_test_df.empty:
            # Filter tests to only those from the Top N institutions
            top_inst_names = outlier_totals['Doctor Clean'].tolist()
            o_test_top = o_test_df[o_test_df['Institution'].isin(top_inst_names)]
            
            # Aggregate tests
            test_agg = o_test_top.groupby('Test Name').agg({
                'Test Count': 'sum',
                'Test Amount': 'sum'
            }).reset_index()
            test_agg = test_agg.sort_values('Test Amount', ascending=False)
            
            # Additional parameters: Number of unique institutions requesting this test
            test_inst_count = o_test_top.groupby('Test Name')['Institution'].nunique().reset_index().rename(columns={'Institution': 'Unique Insts Billed'})
            
            # Billed in each month
            test_months = o_test_top.groupby('Test Name')['Month'].unique().apply(lambda x: ", ".join(sorted(x))).reset_index().rename(columns={'Month': 'Months Billed'})
            
            test_agg = test_agg.merge(test_inst_count, on='Test Name', how='left')
            test_agg = test_agg.merge(test_months, on='Test Name', how='left')
            
            # Format
            test_agg['Test Amount'] = test_agg['Test Amount'].apply(lambda x: f"₹{x:,.0f}")
            test_agg.rename(columns={'Test Count': 'Total Volume Billed'}, inplace=True)
            
            # Add index positions
            test_agg.reset_index(drop=True, inplace=True)
            test_agg.index = test_agg.index + 1
            test_agg.index.name = 'Rank'
            
            render_table(test_agg.reset_index(), key="t7_tests")
        else:
            st.info("No test data found for the selected criteria.")

# --- Tab 8: Doctor Test Share ---
with t8:
    selected_months, top_n, df, test_df, self_df, monthly_doc_summary = render_filters("t8")
    if selected_months:
        st.markdown(f"### Doctor Test Share Analysis (Top {top_n} Doctors)")
        st.markdown("Analyze the specific tests prescribed by your top doctors to identify their clinical focus and cross-selling opportunities.")
        
        # Overall KPIs for all doctors in the selected period
        overall_vol = df['Total Volume'].sum()
        overall_amt = df['Total Amount'].sum()
        
        oc1, oc2 = st.columns(2)
        with oc1: metric_card("Overall Volume (All Doctors)", f"{overall_vol:,.0f}")
        with oc2: metric_card("Overall Revenue (All Doctors)", f"₹{overall_amt:,.0f}")
        
        st.markdown("<br/>", unsafe_allow_html=True)
        
        # Get Top N doctors by total amount in selected period
        overall_top_n_docs = monthly_doc_summary.groupby('Doctor Name')['Total Amount'].sum().nlargest(top_n).index.tolist()
        
        if overall_top_n_docs:
            c1, c2 = st.columns([1, 1])
            with c1:
                selected_doc = st.selectbox("Select a Doctor from Top N:", overall_top_n_docs, key="t8_doc_select")
            with c2:
                num_tests = st.number_input("Number of Top Tests to show:", min_value=5, max_value=100, value=20, step=5, key="t8_num_tests")
                
            if selected_doc:
                doc_tests = test_df[test_df['Doctor Name'] == selected_doc]
                
                # Group by test
                doc_test_summary = doc_tests.groupby('Test Name').agg({
                    'Test Count': 'sum',
                    'Test Amount': 'sum'
                }).reset_index()
                
                total_doc_vol = doc_test_summary['Test Count'].sum()
                total_doc_amt = doc_test_summary['Test Amount'].sum()
                
                # Sort and take top N
                top_doc_tests = doc_test_summary.nlargest(num_tests, 'Test Amount').copy()
                top_doc_tests = top_doc_tests.sort_values('Test Amount', ascending=True)
                
                st.markdown(f"#### {selected_doc} - Top {num_tests} Tests")
                
                metrics_col1, metrics_col2 = st.columns(2)
                with metrics_col1: metric_card("Total Volume (Selected Months)", f"{total_doc_vol:,.0f}")
                with metrics_col2: metric_card("Total Revenue (Selected Months)", f"₹{total_doc_amt:,.0f}")
                
                if not top_doc_tests.empty:
                    fig8 = px.bar(top_doc_tests, x='Test Amount', y='Test Name', orientation='h', color_discrete_sequence=['#9400D3'], height=max(300, len(top_doc_tests)*30))
                    fig8.update_layout(PLOT_LAYOUT)
                    st.markdown("""<div class="chart-wrap">""", unsafe_allow_html=True)
                    st.plotly_chart(fig8, use_container_width=True, config={"displayModeBar": False})
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Prepare table
                    table_df = top_doc_tests.sort_values('Test Amount', ascending=False).copy()
                    table_df['% of Revenue'] = (table_df['Test Amount'] / total_doc_amt * 100).apply(lambda x: f"{x:.1f}%")
                    table_df['% of Volume'] = (table_df['Test Count'] / total_doc_vol * 100).apply(lambda x: f"{x:.1f}%")
                    table_df['Test Amount'] = table_df['Test Amount'].apply(lambda x: f"₹{x:,.2f}")
                    
                    # Reorder
                    table_df = table_df[['Test Name', 'Test Count', '% of Volume', 'Test Amount', '% of Revenue']]
                    render_table(table_df, key="t8_table")
                else:
                    st.info("No test data available for this doctor in the selected period.")
        else:
            st.info("No top doctors found for the selected period.")
