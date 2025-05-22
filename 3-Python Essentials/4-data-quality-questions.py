import polars as pl
from cuallee import Check, CheckLevel
import sys
sys.stdout.reconfigure(encoding='utf-8')


# Read CSV file into Polars DataFrame
df = pl.read_csv("./data/sample_data.csv")

# Question: Check for Nulls on column Id and that Customer_ID column is unique

# check docs at https://canimus.github.io/cuallee/polars/ on how to define a check and run it.
# you will end up with a dataframe of results, check that the `status` column does not have any "FAIL" in it

check = Check(CheckLevel.ERROR, "Completeness")
validation_results_df = (
    check.is_complete("Customer_ID").is_unique("Customer_ID").validate(df)
)
print(validation_results_df)
results = validation_results_df["status"].to_list()
assert "FAIL" not in results == True
