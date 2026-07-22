## Data Loading Module
# Responsible for:
#   - Loading raw HR data from Excel files
#   - Standardising column names
#   - Providing a clean, consistent dataset for downstream processing

#This module ensures consistent naming conventions across datasets before analysis.

import pandas as pd
from pathlib import Path
import re

class DataLoader:
    
    #Loads and standardises HR datasets.

    def __init__(self, path: Path):
        self.path = path
        self._data = None  # Internal storage for loaded DataFrame

    # Data Access
    @property
    def data(self):
        #Returns the currently loaded dataset.
        return self._data

    # Load Raw Data
    def load(self):
        
        #Load dataset from Excel file.
        self._data = pd.read_excel(self.path)
        return self._data

    # Column Standardisation
    def standardise_columns(self):
        
        #Standardise column names using regex.
        #   - Converting to lowercase
        #   - Removing leading/trailing whitespace
        #   - Replacing non-alphanumeric characters with underscores
        
        clean_columns = []
        for col in self._data.columns:
            col = col.strip().lower()
            col = re.sub(r"[^\w]+", "_", col)
            clean_columns.append(col)

        self._data.columns = clean_columns
        return self._data
    
    # Convenience Method
    def load_and_clean(self):
        
        #One-line convenience method.
        self.load()
        self.standardise_columns()
        return self._data
    
    