print(
    "################################################################################"
)
print("Use standard python libraries to do the transformations")
print(
    "################################################################################"
)

# Question: How do you read data from a CSV file at ./data/sample_data.csv into a list of dictionaries?
import csv
data =[]
with open("./data/sample_data.csv", "r" , encoding = 'utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        data.append(row)

print(data)

# Question: How do you remove duplicate rows based on customer ID?
unique_data = []
customer_ids_seen = set()
for row in data:
    customer_id = row["Customer_ID"]
    if customer_id not in customer_ids_seen:
        unique_data.append(row)
        customer_ids_seen.add(customer_id)
    else:
        print(f"Duplicate row found: {row}")


# Question: How do you handle missing values by replacing them with 0?
for row in unique_data:
    if row['Age'] == '':
        row['Age'] = 0
    if row['Purchase_Amount'] == '':
        row['Purchase_Amount'] = 0

# Question: How do you remove outliers such as age > 100 or purchase amount > 1000?
data_cleaned = [
    row
    for row in unique_data
    if int(row['Age'])<=100 and float(row['Purchase_Amount'])<=1000
]

# Question: How do you convert the Gender column to a binary format (0 for Female, 1 for Male)?
for row in data_cleaned:
    if row['Gender'] == 'Female':
        row['Gender'] = 0
    elif row['Gender'] == 'Male':
        row['Gender'] = 1
    

# Question: How do you split the Customer_Name column into separate First_Name and Last_Name columns?
for row in data_cleaned:
    first_name, last_name = row['Customer_Name'].split(' ', 1)
    row['First_Name'] = first_name
    row['Last_Name'] = last_name
# Question: How do you calculate the total purchase amount by Gender?
total_purchase_by_gender = {}

for row in data_cleaned:
    gender = row['Gender']
    amount = float(row['Purchase_Amount'])

    if gender not in total_purchase_by_gender:
        total_purchase_by_gender[gender] = 0.0

    total_purchase_by_gender[gender] += amount

# Question: How do you calculate the average purchase amount by Age group?
# assume age_groups is the grouping we want
# hint: Why do we convert to float?
age_groups = {"18-30": [], "31-40": [], "41-50": [], "51-60": [], "61-70": []}
for row in data_cleaned:
    age = int(row["Age"])
    if age <= 30:
        age_groups["18-30"].append(float(row["Purchase_Amount"]))
    elif age <= 40:
        age_groups["31-40"].append(float(row["Purchase_Amount"]))
    elif age <= 50:
        age_groups["41-50"].append(float(row["Purchase_Amount"]))
    elif age <= 60:
        age_groups["51-60"].append(float(row["Purchase_Amount"]))
    else:
        age_groups["61-70"].append(float(row["Purchase_Amount"]))

average_purchase_by_age_group = {
    group: sum(amounts) / len(amounts) for group, amounts in age_groups.items()
}

# Question: How do you print the results for total purchase amount by Gender and average purchase amount by Age group?

print(f"Total purchase amount by Gender: {total_purchase_by_gender}")
print(f"Average purchase amount by Age group: {average_purchase_by_age_group}")

print(
    "################################################################################"
)
print("Use DuckDB to do the transformations")
print(
    "################################################################################"
)

import duckdb

# Question: How do you connect to DuckDB and load data from a CSV file into a DuckDB table?
duckdb_conn = duckdb.connect(database=':memory:', read_only=False)
# Connect to DuckDB and load data
duckdb_conn.execute(
    "CREATE TABLE data (Customer_ID INTEGER, Customer_Name VARCHAR, Age INTEGER, Gender VARCHAR, Purchase_Amount FLOAT, Purchase_Date DATE)"
)

# Read data from CSV file into DuckDB table
duckdb_conn.execute("COPY data FROM './data/sample_data.csv' WITH HEADER CSV")
# Question: How do you remove duplicate rows based on customer ID in DuckDB?
duckdb_conn.execute(
    "CREATE TABLE unique_data AS SELECT DISTINCT * FROM data"
)
# Question: How do you handle missing values by replacing them with 0 in DuckDB?
duckdb_conn.execute(
    "CREATE TABLE data_cleaned_missing AS SELECT \
             Customer_ID, Customer_Name, \
             COALESCE(Age, 0) AS Age, \
             Gender, \
             COALESCE(Purchase_Amount, 0.0) AS Purchase_Amount, \
             Purchase_Date \
             FROM data_unique"
)
# Question: How do you remove outliers (e.g., age > 100 or purchase amount > 1000) in DuckDB?
duckdb_conn.execute(
    "CREATE TABLE data_cleaned AS SELECT * FROM data_cleaned_missing \
             WHERE Age <= 100 AND Purchase_Amount <= 1000"
)
# Question: How do you convert the Gender column to a binary format (0 for Female, 1 for Male) in DuckDB?
duckdb_conn.execute(
     "CREATE TABLE data_cleaned_gender AS SELECT *, \
             CASE WHEN Gender = 'Female' THEN 0 ELSE 1 END AS Gender_Binary \
             FROM data_cleaned_outliers"
)
# Question: How do you split the Customer_Name column into separate First_Name and Last_Name columns in DuckDB?
duckdb_conn.execute(
    "CREATE TABLE data_cleaned AS SELECT \
             Customer_ID, \
             SPLIT_PART(Customer_Name, ' ', 1) AS First_Name, \
             SPLIT_PART(Customer_Name, ' ', 2) AS Last_Name, \
             Age, Gender_Binary, Purchase_Amount, Purchase_Date \
             FROM data_cleaned_gender"
)

# Question: How do you calculate the total purchase amount by Gender in DuckDB?
total_purchase_by_gender = duckdb_conn.execute(
    "SELECT Gender_Binary, SUM(Purchase_Amount) AS Total_Purchase_Amount \
                                        FROM data_cleaned_gender \
                                        GROUP BY Gender_Binary"
).fetchall()
# Question: How do you calculate the average purchase amount by Age group in DuckDB?
average_purchase_by_age_group = duckdb_conn.execute(
    "SELECT CASE \
                                             WHEN Age BETWEEN 18 AND 30 THEN '18-30' \
                                             WHEN Age BETWEEN 31 AND 40 THEN '31-40' \
                                             WHEN Age BETWEEN 41 AND 50 THEN '41-50' \
                                             WHEN Age BETWEEN 51 AND 60 THEN '51-60' \
                                             ELSE '61-70' END AS Age_Group, \
                                             AVG(Purchase_Amount) AS Average_Purchase_Amount \
                                             FROM data_cleaned \
                                             GROUP BY Age_Group"
).fetchall()

# Question: How do you print the results for total purchase amount by Gender and average purchase amount by Age group in DuckDB?
print("====================== Results ======================")
print("Total purchase amount by Gender:", total_purchase_by_gender)
print("Average purchase amount by Age group:", average_purchase_by_age_group)
