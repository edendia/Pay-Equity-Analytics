
#Main Execution Script

#Coordinates the full EU Pay Transparency analysis pipeline:

#   1. Load raw HR data
#   2. Clean and process data
#   3. Compute EU Directive descriptive metrics
#   4. Run adjusted regression model
#   5. Export compliance-ready report

# This file acts as the orchestration layer of the application.


from pathlib import Path
from config import Config
from loader import DataLoader
from validator import EUValidator
from processor import DataProcessor
from regression import RegressionEngine
from diagnostics import Diagnostics
from descriptives import EUMetrics
from reporting import EUReportWriter


def main():
    # ==================================================
    # 1. Load & Process Data
    # ==================================================

    data_path = Config.DATA_PATH

    loader = DataLoader(data_path)
    df_raw = loader.load_and_clean()

    processor = DataProcessor(df_raw)
    df = processor.process()

    # ==================================================
    # 2. EU Descriptive Metrics (Directive Compliance)
    # ==================================================

    metrics_engine = EUMetrics(df)
    metrics = metrics_engine.full_summary()

    # ==================================================
    # 3. Adjusted Regression Model
    # ==================================================

    controls = [
        "tenure_years_",
        "job_level",
        "C(department)",
        "C(country)"
    ]

    reg_engine = RegressionEngine(
        df=df,
        dependent="log_total_pay",
        controls=controls
    )

    reg_engine.fit()

    adjusted_gap = reg_engine.adjusted_gender_gap()
    regression_table = reg_engine.regression_summary_df()
    model_stats = reg_engine.model_stats()

    # Add regression results to metrics dictionary
    metrics["summary"]["Adjusted Gender Pay Gap (%)"] = adjusted_gap
    metrics["regression_table"] = regression_table
    metrics["regression_stats"] = model_stats

    # Run diagnostics
    diagnostics = Diagnostics(reg_engine)

    print("\nModel Diagnostics:")
    print(diagnostics.summary_stats())
    print("\nBreusch-Pagan Test:")
    print(diagnostics.breusch_pagan_test())
    print("\nVariance Inflation Factors:")
    print(diagnostics.calculate_vif())

    # ==================================================
    # 4. Export Full Compliance Report
    # ==================================================

    output_path = Path("data/EU_Full_Compliance_Report_2024.xlsx")
    reporter = EUReportWriter(output_path)
    reporter.export_full_report(metrics)


if __name__ == "__main__":
    main()