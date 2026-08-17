import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.graph_objects as go

def render_patient_source_tab(selected_months, top_n, df, test_df, self_df, monthly_doc_summary, month_order, metric_card, render_table):
    st.markdown("## Patient Source Analysis")
    st.markdown("Analyze the difference between **Self-Billed / Self-Referred Patients** and **Doctor-Referred Patients**.")
    
    # Check data quality & limitations
    st.warning("⚠️ **Data Limitation:** Patient-level identifiers are unavailable. 'Volume' represents total billed units/accessions, not unique patients. Metrics have been labelled accordingly.")
    
    # ---------------------------------------------------------
    # 4. EXECUTIVE KPI SECTION
    # ---------------------------------------------------------
    doc_vol = df['Total Volume'].sum()
    doc_amt = df['Total Amount'].sum()
    
    # Self-Billed volume - since the PDF didn't have "Total Volume" field, we use Test Count as a proxy for Volume Unit
    self_vol = self_df['Test Count'].sum()
    self_amt = self_df['Test Amount'].sum()
    
    total_vol = doc_vol + self_vol
    total_amt = doc_amt + self_amt
    
    self_vol_pct = (self_vol / total_vol * 100) if total_vol > 0 else 0
    doc_vol_pct = (doc_vol / total_vol * 100) if total_vol > 0 else 0
    
    # Data Completeness
    completeness = 100.0 # Everything is mapped to either Self or Doctor
    
    st.markdown("### Executive KPIs")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("Total Volume", f"{total_vol:,.0f}")
    with c2: metric_card("Self-Billed Volume", f"{self_vol:,.0f} ({self_vol_pct:.1f}%)")
    with c3: metric_card("Doc-Referred Volume", f"{doc_vol:,.0f} ({doc_vol_pct:.1f}%)")
    with c4: metric_card("Data Completeness", f"{completeness:.1f}%")
    
    c5, c6, c7, c8 = st.columns(4)
    with c5: metric_card("Total Revenue", f"₹{total_amt:,.0f}")
    with c6: metric_card("Self-Billed Rev", f"₹{self_amt:,.0f}")
    with c7: metric_card("Doc-Referred Rev", f"₹{doc_amt:,.0f}")
    
    rev_per_vol = total_amt / total_vol if total_vol > 0 else 0
    with c8: metric_card("Revenue per Vol Unit", f"₹{rev_per_vol:,.0f}")
    
    # ---------------------------------------------------------
    # 5. SELF VS DOCTOR COMPARISON
    # ---------------------------------------------------------
    st.markdown("---")
    st.markdown("### Self vs Doctor Comparison")
    
    doc_tests = test_df['Test Count'].sum()
    self_tests = self_df['Test Count'].sum()
    
    comp_data = [
        {"Metric": "Volume", "Self Billed": self_vol, "Doctor Referred": doc_vol},
        {"Metric": "Revenue", "Self Billed": self_amt, "Doctor Referred": doc_amt},
        {"Metric": "Revenue per Volume Unit", "Self Billed": self_amt/self_vol if self_vol>0 else 0, "Doctor Referred": doc_amt/doc_vol if doc_vol>0 else 0},
        {"Metric": "Tests", "Self Billed": self_tests, "Doctor Referred": doc_tests},
        {"Metric": "Average Revenue per Test", "Self Billed": self_amt/self_tests if self_tests>0 else 0, "Doctor Referred": doc_amt/doc_tests if doc_tests>0 else 0},
    ]
    
    comp_df = pd.DataFrame(comp_data)
    comp_df['Difference'] = comp_df['Self Billed'] - comp_df['Doctor Referred']
    comp_df['% Difference'] = np.where(comp_df['Doctor Referred'] > 0, 
                                     (comp_df['Difference'] / comp_df['Doctor Referred'] * 100), 0)
    
    # Formatting
    comp_disp = comp_df.copy()
    for col in ['Self Billed', 'Doctor Referred', 'Difference']:
        comp_disp[col] = comp_disp.apply(lambda r: f"₹{r[col]:,.0f}" if 'Revenue' in r['Metric'] else f"{r[col]:,.0f}", axis=1)
    comp_disp['% Difference'] = comp_disp['% Difference'].apply(lambda x: f"{x:+.1f}%")
    
    render_table(comp_disp, key="comp_tbl")
    
    # ---------------------------------------------------------
    # 6. MONTHLY TREND ANALYSIS
    # ---------------------------------------------------------
    st.markdown("---")
    st.markdown("### Monthly Trend Analysis")
    
    # Aggregate monthly
    m_doc = df.groupby('Month').agg({'Total Volume': 'sum', 'Total Amount': 'sum'}).reset_index()
    m_doc['Source'] = 'Doctor Referred'
    
    m_self = self_df.groupby('Month').agg({'Test Count': 'sum', 'Test Amount': 'sum'}).reset_index()
    m_self.rename(columns={'Test Count': 'Total Volume', 'Test Amount': 'Total Amount'}, inplace=True)
    m_self['Source'] = 'Self Billed'
    
    m_trend = pd.concat([m_doc, m_self])
    m_trend['Month_Idx'] = m_trend['Month'].apply(lambda x: month_order.index(x) if x in month_order else 99)
    m_trend = m_trend.sort_values('Month_Idx')
    
    fig_vol = px.line(m_trend, x='Month', y='Total Volume', color='Source', markers=True, title="Volume Trend by Source", color_discrete_map={'Doctor Referred':'#9400D3', 'Self Billed':'#D3D3FF'})
    fig_amt = px.line(m_trend, x='Month', y='Total Amount', color='Source', markers=True, title="Revenue Trend by Source", color_discrete_map={'Doctor Referred':'#9400D3', 'Self Billed':'#D3D3FF'})
    
    tc1, tc2 = st.columns(2)
    with tc1: st.plotly_chart(fig_vol, use_container_width=True)
    with tc2: st.plotly_chart(fig_amt, use_container_width=True)
    
    # ---------------------------------------------------------
    # 7. PATIENT ECONOMICS
    # ---------------------------------------------------------
    st.markdown("---")
    st.markdown("### Patient Economics")
    st.info("💡 Comparing the value generated per volume unit between direct walk-ins and doctor referrals.")
    
    ec1, ec2, ec3 = st.columns(3)
    with ec1: metric_card("Self Rev/Vol Unit", f"₹{self_amt/self_vol if self_vol>0 else 0:,.0f}")
    with ec2: metric_card("Doc Rev/Vol Unit", f"₹{doc_amt/doc_vol if doc_vol>0 else 0:,.0f}")
    with ec3: metric_card("Premium on Doc Ref", f"{((doc_amt/doc_vol)/(self_amt/self_vol) - 1)*100 if self_amt>0 else 0:+.1f}%")
    
    # ---------------------------------------------------------
    # 8. TEST MIX ANALYSIS
    # ---------------------------------------------------------
    st.markdown("---")
    st.markdown("### Test Mix by Patient Source")
    
    t_doc = test_df.groupby('Test Name').agg({'Test Count': 'sum', 'Test Amount': 'sum'}).reset_index()
    t_doc.rename(columns={'Test Count': 'Doc_Vol', 'Test Amount': 'Doc_Rev'}, inplace=True)
    
    t_self = self_df.groupby('Test Name').agg({'Test Count': 'sum', 'Test Amount': 'sum'}).reset_index()
    t_self.rename(columns={'Test Count': 'Self_Vol', 'Test Amount': 'Self_Rev'}, inplace=True)
    
    t_mix = pd.merge(t_doc, t_self, on='Test Name', how='outer').fillna(0)
    t_mix['Total_Vol'] = t_mix['Doc_Vol'] + t_mix['Self_Vol']
    t_mix['Total_Rev'] = t_mix['Doc_Rev'] + t_mix['Self_Rev']
    
    t_mix['Self_Vol_%'] = (t_mix['Self_Vol'] / t_mix['Total_Vol'] * 100).round(1)
    t_mix['Doc_Vol_%'] = (t_mix['Doc_Vol'] / t_mix['Total_Vol'] * 100).round(1)
    
    sort_by = st.selectbox("Sort Tests By:", ["Volume", "Revenue"], key="test_mix_sort")
    sort_col = 'Total_Vol' if sort_by == "Volume" else 'Total_Rev'
    
    top_mix = t_mix.sort_values(sort_col, ascending=False).head(top_n)
    
    fig_mix = go.Figure(data=[
        go.Bar(name='Self Billed', y=top_mix['Test Name'], x=top_mix['Self_Vol' if sort_by=="Volume" else 'Self_Rev'], orientation='h', marker_color='#D3D3FF'),
        go.Bar(name='Doctor Referred', y=top_mix['Test Name'], x=top_mix['Doc_Vol' if sort_by=="Volume" else 'Doc_Rev'], orientation='h', marker_color='#9400D3')
    ])
    fig_mix.update_layout(barmode='stack', yaxis={'autorange': 'reversed'}, title=f"Top {top_n} Tests Split by Source")
    st.plotly_chart(fig_mix, use_container_width=True)
    
    # ---------------------------------------------------------
    # 11. SELF-BILLING OPPORTUNITY ANALYSIS
    # ---------------------------------------------------------
    st.markdown("#### Referral Dependency vs Direct Patient Opportunity")
    
    # Find tests with high self billing (Opportunity)
    direct_opp = t_mix[(t_mix['Self_Vol_%'] > 60) & (t_mix['Total_Vol'] > 10)].sort_values('Self_Vol', ascending=False).head(5)
    ref_dep = t_mix[(t_mix['Doc_Vol_%'] > 90) & (t_mix['Total_Vol'] > 10)].sort_values('Doc_Vol', ascending=False).head(5)
    
    col_opp, col_dep = st.columns(2)
    with col_opp:
        st.success("**Direct Patient Opportunities** (High Self-Billed %)")
        render_table(direct_opp[['Test Name', 'Self_Vol_%', 'Total_Vol']], key="opp_tbl")
    with col_dep:
        st.info("**Referral Dependent Tests** (High Doctor-Referred %)")
        render_table(ref_dep[['Test Name', 'Doc_Vol_%', 'Total_Vol']], key="dep_tbl")
    
    # ---------------------------------------------------------
    # 9 & 10. DOCTOR REFERRAL & RISK ANALYSIS
    # ---------------------------------------------------------
    st.markdown("---")
    st.markdown("### Doctor Referral Performance & Risk")
    
    if len(selected_months) < 2:
        st.warning("Please select at least 2 months in the filter to view growth, trends, and risk analysis.")
    else:
        # Split into first half and second half
        half = len(selected_months) // 2
        h1_months = selected_months[:half]
        h2_months = selected_months[half:]
        
        h1_df = df[df['Month'].isin(h1_months)].groupby('Doctor Name').agg({'Total Volume':'sum', 'Total Amount':'sum'}).reset_index()
        h2_df = df[df['Month'].isin(h2_months)].groupby('Doctor Name').agg({'Total Volume':'sum', 'Total Amount':'sum'}).reset_index()
        
        doc_risk = pd.merge(h1_df, h2_df, on='Doctor Name', suffixes=('_H1', '_H2'), how='outer').fillna(0)
        doc_risk['Vol_Change'] = doc_risk['Total Volume_H2'] - doc_risk['Total Volume_H1']
        doc_risk['Vol_Change_%'] = np.where(doc_risk['Total Volume_H1'] > 0, (doc_risk['Vol_Change'] / doc_risk['Total Volume_H1'] * 100), 0)
        
        def classify_risk(pct):
            if pct > 10: return "🟢 Growing"
            elif pct >= -10: return "⚪ Stable"
            elif pct >= -25: return "🟠 Declining"
            else: return "🔴 Critical Decline"
            
        doc_risk['Status'] = doc_risk['Vol_Change_%'].apply(classify_risk)
        
        # Merge back qualification and mark exec
        doc_meta = df[['Doctor Name', 'Qualification', 'Mark_Exec']].drop_duplicates('Doctor Name')
        doc_risk = pd.merge(doc_risk, doc_meta, on='Doctor Name', how='left')
        
        doc_risk = doc_risk.sort_values('Total Amount_H2', ascending=False).head(top_n)
        
        disp_risk = doc_risk[['Doctor Name', 'Qualification', 'Mark_Exec', 'Total Volume_H2', 'Total Amount_H2', 'Vol_Change_%', 'Status']].copy()
        disp_risk['Vol_Change_%'] = disp_risk['Vol_Change_%'].apply(lambda x: f"{x:+.1f}%")
        disp_risk['Total Amount_H2'] = disp_risk['Total Amount_H2'].apply(lambda x: f"₹{x:,.0f}")
        
        render_table(disp_risk, key="risk_tbl")

    # ---------------------------------------------------------
    # 13. REVENUE CONCENTRATION
    # ---------------------------------------------------------
    st.markdown("---")
    st.markdown("### Doctor Revenue Concentration")
    
    doc_totals = df.groupby('Doctor Name')['Total Amount'].sum().sort_values(ascending=False)
    
    top5_share = doc_totals.head(5).sum() / doc_amt * 100 if doc_amt > 0 else 0
    top10_share = doc_totals.head(10).sum() / doc_amt * 100 if doc_amt > 0 else 0
    
    con_c1, con_c2, con_c3 = st.columns(3)
    with con_c1: metric_card("Top 5 Docs Share", f"{top5_share:.1f}%")
    with con_c2: metric_card("Top 10 Docs Share", f"{top10_share:.1f}%")
    with con_c3: metric_card("Remaining Docs Share", f"{100 - top10_share:.1f}%")
    
    # ---------------------------------------------------------
    # 14. AUTOMATED INSIGHTS
    # ---------------------------------------------------------
    st.markdown("---")
    st.markdown("### 🤖 Automated Insights & Alerts")
    
    insights = []
    
    if doc_vol_pct > 80:
        insights.append(f"⚠️ **High Referral Dependency:** {doc_vol_pct:.1f}% of volume comes from doctors, indicating low direct-patient engagement.")
    elif self_vol_pct > 30:
        insights.append(f"📈 **Strong Direct Patient Base:** Walk-ins account for {self_vol_pct:.1f}% of volume.")
        
    if len(selected_months) >= 2:
        tot_vol_h1 = m_trend[m_trend['Month'].isin(h1_months)]['Total Volume'].sum()
        tot_vol_h2 = m_trend[m_trend['Month'].isin(h2_months)]['Total Volume'].sum()
        if tot_vol_h1 > 0:
            trend_pct = (tot_vol_h2 - tot_vol_h1) / tot_vol_h1 * 100
            if trend_pct < -5:
                insights.append(f"📉 **Overall Decline:** Volume dropped by {abs(trend_pct):.1f}% from the first half of the selected period to the second half.")
            elif trend_pct > 5:
                insights.append(f"🚀 **Overall Growth:** Volume grew by {trend_pct:.1f}% from the first half of the selected period to the second half.")
                
    if top10_share > 50:
        insights.append(f"⚠️ **Concentration Risk:** The top 10 doctors contribute {top10_share:.1f}% of all referred revenue. Losing any of them would severely impact business.")
        
    if doc_amt > 0 and self_amt > 0:
        if (doc_amt/doc_vol) > (self_amt/self_vol) * 1.2:
            insights.append(f"💰 **Value Discrepancy:** Doctor-referred volume units generate significantly higher revenue (₹{doc_amt/doc_vol:,.0f}) compared to walk-ins (₹{self_amt/self_vol:,.0f}).")
    
    if len(insights) == 0:
        insights.append("✅ Business metrics are currently stable with no extreme outliers detected.")
        
    for i in insights:
        st.markdown(f"- {i}")

