
#EU Pay Transparency – MVP Dashboard

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.graph_objects as go

from src.loader import DataLoader
from src.processor import DataProcessor
from src.descriptives import EUMetrics
from src.regression import RegressionEngine
from src.reporting import EUReportWriter


# ------------------------------------------------------
# Page Configuration (Minimal Corporate Look)
# ------------------------------------------------------

st.set_page_config(
    page_title="EU Pay Transparency Tool",
    layout="wide"
)

st.markdown(
    """
    <style>
    .main {
        background-color: #FFFFFF;
    }
    h1, h2, h3 {
        color: #1F2933;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("EU Pay Transparency Analytics")


# ------------------------------------------------------
# File Upload
# ------------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload Pay Dataset (Excel format)",
    type=["xlsx"]
)


# ------------------------------------------------------
# Main App Logic
# ------------------------------------------------------

if uploaded_file:

    # -----------------------------
    # 1. Data Loading & Processing
    # -----------------------------

    loader = DataLoader(uploaded_file)
    df_raw = loader.load_and_clean()

    processor = DataProcessor(df_raw)
    df = processor.process()

    # -----------------------------
    # 2. Pay Component Selection
    # -----------------------------

    st.sidebar.header("Model Settings")

    pay_options = {
        "Total Pay": "total_actual_total_pay_2024",
        "Basic Wage": "total_actual_basic_wage_2024",
        "Complementary Pay": "total_actual_complementary_pay_2024"
    }

    selected_label = st.sidebar.selectbox(
        "Select Pay Component",
        list(pay_options.keys())
    )

    pay_component = pay_options[selected_label]

    # Defensive check (prevents crashes)
    if pay_component not in df.columns:
        st.error(f"Column '{pay_component}' not found in dataset.")
        st.stop()

    df["log_selected_pay"] = np.log(df[pay_component])

    # -----------------------------
    # 3. EU Descriptive Metrics
    # -----------------------------

    metrics_engine = EUMetrics(df)
    metrics = metrics_engine.full_summary()

    # -----------------------------
    # 4. Regression Model
    # -----------------------------

    controls = [
        "tenure_years_",
        "job_level",
        "C(department)",
        "C(country)"
    ]

    reg_engine = RegressionEngine(
        df=df,
        dependent="log_selected_pay",
        controls=controls
    )

    reg_engine.fit()
    adjusted_gap = reg_engine.adjusted_gender_gap()

    print("Dependent used:", reg_engine.dependent)
    print("Columns in df:", df.columns.tolist())

    # --------------------------------------------------
    # Key Results
    # --------------------------------------------------

    st.markdown("## Key Results")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Unadjusted Pay Gap (%)",
        metrics["summary"]["Mean Gender Pay Gap (%)"]
    )

    col2.metric(
        "Adjusted Pay Gap (%)",
        adjusted_gap
    )

    col3.metric(
        "Model R²",
        round(reg_engine.model.rsquared, 3)
    )

    st.divider()

    # --------------------------------------------------
    # Drivers of Pay Variation (Half Doughnut)
    # --------------------------------------------------

    driver_shares = reg_engine.driver_shares()  # now sums to 100%
    labels = list(driver_shares.keys())
    values = list(driver_shares.values())

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.5)])
    fig.update_layout(title="Drivers of Pay Variation (Normalized)")
    st.plotly_chart(fig, use_container_width=True)


    # --------------------------------------------------
    # Gap Evolution (Stepwise Reduction)
    # --------------------------------------------------
    
    st.markdown("## Evolution from Unadjusted to Adjusted Gap")

    # Get unadjusted and adjusted gap
    unadjusted_gap = metrics["summary"]["Mean Gender Pay Gap (%)"]
    adjusted_gap = reg_engine.adjusted_gender_gap()

    # Get driver shares (normalized to 100%)
    driver_weights = reg_engine.driver_shares()  # e.g., {'tenure':44,'job_level':33,'country':17,'department':5}

    # Stepwise reduction based on driver shares
    steps = ["Unadjusted"]
    values = [unadjusted_gap]

    current_gap = unadjusted_gap
    total_change = adjusted_gap - unadjusted_gap  # can be negative

    for driver, pct in driver_weights.items():
        change = total_change * (pct / 100)
        current_gap += change
        steps.append(driver)
        values.append(round(current_gap, 2))

    # Final adjusted gap (force exact value)
    steps.append("Adjusted")
    values.append(round(adjusted_gap, 2))

    # Convert to deltas for Waterfall
    deltas = [values[0]]  # first bar absolute
    for i in range(1, len(values)-1):
        deltas.append(values[i] - values[i-1])
    deltas.append(values[-1])  # total bar

    measure = ["absolute"] + ["relative"]*(len(deltas)-2) + ["total"]

    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=measure,
        x=steps,
        y=deltas,
        connector={"line":{"color":"rgb(63, 63, 63)"}},
        text=[f"{round(val,2)}%" for val in deltas],
        textposition="outside"
    ))

    fig.update_layout(
        title="How Controls Move the Gender Pay Gap",
        yaxis_title="Pay Gap (%)",
        xaxis_title="Step",
        showlegend=False,
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)


    # --------------------------------------------------
    # Report Download
    # --------------------------------------------------

    st.markdown("## Export Report")

    output_path = Path("temp_report.xlsx")
    reporter = EUReportWriter(output_path)

    # Add regression outputs to export dictionary
    metrics["summary"]["Adjusted Gender Pay Gap (%)"] = adjusted_gap
    metrics["regression_table"] = reg_engine.regression_summary_df()
    metrics["regression_stats"] = reg_engine.model_stats()

    reporter.export_full_report(metrics)

    with open(output_path, "rb") as f:
        st.download_button(
            label="Download EU Compliance Report",
            data=f,
            file_name="EU_Compliance_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


