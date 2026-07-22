
import pandas as pd
from pathlib import Path

class EUReportWriter:

    def __init__(self, output_path: Path):
        self.output_path = output_path

    def export_full_report(self, metrics: dict):

        with pd.ExcelWriter(self.output_path, engine="openpyxl") as writer:

            # Summary
            pd.DataFrame(
                metrics["summary"].items(),
                columns=["Metric", "Value"]
            ).to_excel(writer, sheet_name="Summary", index=False)

            # Annual Pay
            metrics["annual_pay_table"].to_excel(writer, sheet_name="Annual Pay Stats")

            # Hourly Pay
            metrics["hourly_pay_table"].to_excel(writer, sheet_name="Hourly Pay Stats")

            # Bonus
            metrics["bonus_table"].to_excel(writer, sheet_name="Bonus Stats")

            metrics["bonus_participation"].to_frame(
                "Bonus Participation (%)"
            ).to_excel(writer, sheet_name="Bonus Participation")

            # Quartiles
            metrics["quartiles"].to_excel(writer, sheet_name="Pay Quartiles")

            # Workforce
            metrics["workforce_distribution"].to_frame(
                "Workforce Distribution (%)"
            ).to_excel(writer, sheet_name="Workforce Distribution")

            # Regression Results
            if "regression_table" in metrics:
                metrics["regression_table"].to_excel(
                writer,
                sheet_name="Regression Results"
                )
            
            # Regression Model Stats
            if "regression_stats" in metrics:
                pd.DataFrame(
                metrics["regression_stats"].items(),
                columns=["Metric", "Value"]
                ).to_excel(writer, sheet_name="Regression Model Stats", index=False)

        print(f"\nFull EU Report exported to: {self.output_path}")