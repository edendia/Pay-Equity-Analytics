#Validation module

from functools import wraps

def validation_logger(func):
    
    #Decorator to log validation steps.
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Running validation: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper


class BaseValidator:
    
    #Base class for dataset validation.
    def __init__(self, dataframe):
        self.df = dataframe


class EUValidator(BaseValidator):
    
    #EU Pay Transparency specific validations.

    @validation_logger
    def check_required_columns(self, required_columns):
        #Ensures all required columns are present in the dataset.
        #   - Converts required column names to lowercase and replaces spaces with underscores.
        #   - Raises ValueError if any are missing.

        missing = [col for col in required_columns if col.lower().replace(" ", "_") not in self.df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        return True

    @validation_logger
    def check_no_negative_pay(self):
        #Ensures there are no negative pay values in the dataset.
        #   - Checks 'total_actual_total_pay_2024' column.
        #   - Raises ValueError if any negative values are detected.

        if (self.df["total_actual_total_pay_2024"] < 0).any():
            raise ValueError("Negative pay detected.")
        return True
    

