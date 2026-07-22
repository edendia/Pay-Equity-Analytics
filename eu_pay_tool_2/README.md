# EU Pay Transparency Tool – README

## Project Overview
This Python project analyzes gender pay gaps in European organizations in line with the EU Pay Transparency Directive.  
It calculates unadjusted and adjusted pay gaps, visualizes the impact of key drivers (e.g., department, job level, tenure), and generates a full compliance report in Excel.

## Key Features
- **Descriptive metrics:** mean/median pay gaps, hourly pay gaps, bonus gaps, pay quartiles, workforce distribution.  
- **Regression analysis:** log-linear multivariate regression to compute adjusted gender pay gaps.  
- **Driver decomposition:** visual breakdown of how different factors contribute to the pay gap.  
- **Diagnostics:** variance inflation factor (VIF), heteroscedasticity tests (Breusch-Pagan), and model statistics.  
- **Reporting:** generates a full Excel report with all metrics and regression results.  
- **Data validation:** ensures dataset integrity (required columns, no negative pay).  

## Repository Structure

eu_pay_tool/
│
├─ src/
│   ├─ config.py          # Immutable project configuration (dataset path, reference date, required columns)
│   ├─ loader.py          # Loads and standardizes HR datasets
│   ├─ processor.py       # Prepares numeric/logged variables and encodes gender
│   ├─ descriptives.py    # Computes EU metrics and pay gap tables
│   ├─ regression.py      # Regression engine for adjusted pay gap and driver decomposition
│   ├─ diagnostics.py     # Regression diagnostic tests (VIF, Breusch-Pagan)
│   ├─ reporting.py       # Exports Excel report with metrics and results
│   └─ validator.py       # Checks required columns and negative pay
│
├─ main.py                # Entry point to run the pipeline from raw data to report
├─ app.py                 # Streamlit dashboard for interactive analysis
├─ data/                  # Place your Excel dataset here
└─ README.md              # Project overview and usage instructions

## Setup Instructions
1. **Install dependencies**  
```bash
pip install pandas numpy statsmodels openpyxl plotly streamlit

2.	Prepare dataset
Place the HR dataset (Excel) in the data/ folder. Ensure column names match the required fields in src/config.py.

3.	Run analysis via command line
python src/main.py

4.	Run interactive dashboard
streamlit run src/app.py

Usage
	•	The tool calculates unadjusted and adjusted gender pay gaps.
	•	Visualizes contributions of drivers to the gap in waterfall charts.
	•	Generates a full Excel report including descriptive metrics, regression results, and workforce distributions.

Notes
	•	Ensure gender column uses “Male” and “Female” labels.
	•	Adjust control variables in regression.py or main.py if your dataset has different column names.
	•	Logarithmic transformation is applied to pay variables before regression.
