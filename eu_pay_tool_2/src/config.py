##Configuration module for Pay Gap Tool
#This module centralizes immutable application settings:
#   - Default data paths
#   - Reference reporting date
#   - Required dataset structure

# Used a dataclass to ensure settings are structured, typed, and protected from modification.

from pathlib import Path
from dataclasses import dataclass

#The `frozen=True` parameter prevents runtime modification.

@dataclass(frozen=True)

#Immutable configuration settings.
class Config:
    
    # Default dataset location (used if no upload is provided)
    DATA_PATH: Path = Path("data/EU_Pay_Transparency_Synthetic_Dataset_2024.xlsx")
    
    # Official reporting reference date (EU directive requirement)
    REFERENCE_DATE: str = "2024-12-31"
    
    # Mandatory columns required for compliance calculations.
    # The loader should validate the dataset against these fields.
    REQUIRED_COLUMNS: tuple = (
        "Anonymised Employee ID",
        "Gender",
        "Country",
        "Job Level",
        "FTE Contractual Base Salary (31 Dec 2024)",
        "TOTAL ACTUAL Total Pay 2024"
    )

    