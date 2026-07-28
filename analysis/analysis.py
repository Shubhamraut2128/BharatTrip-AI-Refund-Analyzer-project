import pandas as pd

# Excel Path
file_path = "data/BharatTrip_Refund_Data.xlsx"

# Load all sheets
excel = pd.ExcelFile(file_path)

print("Available Sheets:")
print(excel.sheet_names)

# Read Sheets
readme = pd.read_excel(file_path, sheet_name="Read_Me")
support = pd.read_excel(file_path, sheet_name="Support_Tracker")
finance = pd.read_excel(file_path, sheet_name="Finance_Tracker")
escalations = pd.read_excel(file_path, sheet_name="Escalations")

#Dataset Summary

print("\nSupport Shape:", support.shape)
print("Finance Shape:", finance.shape)
print("Escalation Shape:", escalations.shape)

print("\nSupport Columns")
print(support.columns)

print("\nFinance Columns")
print(finance.columns)

print("\nEscalation Columns")
print(escalations.columns)


#Missing Values

print("\nSupport Missing Values")
print(support.isnull().sum())

print("\nFinance Missing Values")
print(finance.isnull().sum())

print("\nEscalation Missing Values")
print(escalations.isnull().sum())


#Duplicate Records
print("\nSupport Duplicates:", support.duplicated().sum())

print("Finance Duplicates:", finance.duplicated().sum())

print("Escalation Duplicates:", escalations.duplicated().sum())


#Statistics

print("\nSupport Info")
print(support.describe(include="all"))

print("\nFinance Info")
print(finance.describe(include="all"))

print("\nEscalation Info")
print(escalations.describe(include="all"))

#Export Summary

summary = {
    "Support Records": len(support),
    "Finance Records": len(finance),
    "Escalation Records": len(escalations),
    "Support Missing": support.isnull().sum().sum(),
    "Finance Missing": finance.isnull().sum().sum(),
    "Escalation Missing": escalations.isnull().sum().sum(),
}

summary_df = pd.DataFrame(summary.items(), columns=["Metric", "Value"])

summary_df.to_csv("output/dataset_summary.csv", index=False)


#Support vs Finance Comparison 

print(support.columns.tolist())
print(finance.columns.tolist())  

#Rename Columns

# Rename ID columns

support.rename(
    columns={
        "Ticket ID": "Refund_ID"
    },
    inplace=True
)


finance.rename(
    columns={
        "Ref No": "Refund_ID"
    },
    inplace=True
)


# Verify rename

print("\nAfter Rename Support Columns:")
print(support.columns.tolist())


print("\nAfter Rename Finance Columns:")
print(finance.columns.tolist()) 



#Missing Refunds

missing_finance = support[
    ~support["Refund_ID"].isin(finance["Refund_ID"])
]

print("Missing in Finance:", len(missing_finance))

missing_finance.to_csv(
    "output/missing_in_finance.csv",
    index=False
)

#Missing in Support 

missing_support = finance[
    ~finance["Refund_ID"].isin(support["Refund_ID"])
]

print("Missing in Support:", len(missing_support))

missing_support.to_csv(
    "output/missing_in_support.csv",
    index=False
)

# Merge Sheets

merged = support.merge(
    finance,
    on="Refund_ID",
    how="outer",
    suffixes=("_Support", "_Finance")
)

print(merged.head())

#Status Mismatch
status_mismatch = merged[
    merged["Status"] != merged["Payout Status"]
]

print("Status Mismatch:", len(status_mismatch))

status_mismatch.to_csv(
    "output/status_mismatch.csv",
    index=False
)


# Amount Mismatch

amount_mismatch = merged[
    (merged["Refund Amount (INR)"].notna()) &
    (merged["Amount Paid (INR)"].notna()) &
    (merged["Refund Amount (INR)"] != merged["Amount Paid (INR)"])
]


print("Amount Mismatch:", len(amount_mismatch))


amount_mismatch.to_csv(
    "output/amount_mismatch.csv",
    index=False
)

#Duplicate Refund IDs
support_duplicates = support[
    support.duplicated(
        subset=["Refund_ID"],
        keep=False
    )
]
print(support_duplicates)


finance_duplicates = finance[
    finance.duplicated(
        subset=["Refund_ID"],
        keep=False
    )
]

print(finance_duplicates)


# Rename Escalation Reference Column

escalations.rename(
    columns={
        "Related Ticket / Ref": "Refund_ID"
    },
    inplace=True
)


print("\nEscalation Columns After Rename:")
print(escalations.columns.tolist())


# Step 9: Escalation Join

merged_all = merged.merge(
    escalations,
    on="Refund_ID",
    how="left",
    suffixes=("", "_Escalation")
)


print(merged_all.head())

#KPI Summary

print("="*40)

print("Support Records :", len(support))

print("Finance Records :", len(finance))

print("Escalations :", len(escalations))

print("Missing Finance :", len(missing_finance))

print("Missing Support :", len(missing_support))

print("Status Mismatch :", len(status_mismatch))

print("Amount Mismatch :", len(amount_mismatch))


#Exploratory Data Analysis (EDA)

# Step 1: Processing Time Analysis

# Convert dates
merged["Request Date"] = pd.to_datetime(
    merged["Request Date"],
    errors="coerce"
)

merged["Processed On"] = pd.to_datetime(
    merged["Processed On"],
    errors="coerce"
)


# Calculate Processing Days
merged["Processing_Days"] = (
    merged["Processed On"] -
    merged["Request Date"]
).dt.days


# Analysis
print("\nProcessing Days Statistics")
print(merged["Processing_Days"].describe())


print(support["Status"].value_counts()) 

print(finance["Payout Status"].value_counts())

print(support["Channel"].value_counts())

support.groupby("Channel")["Status"].value_counts()

merged_all.groupby("Channel")["Escalation ID"].count()

support["Handled By"].value_counts().head(10)

support["Refund Amount (INR)"].describe()

high_pending = support[
    (support["Status"] == "Pending") &
    (support["Refund Amount (INR)"] > 10000)
]

print(high_pending)


high_pending.to_csv(
    "output/high_pending_refunds.csv",
    index=False
)

print("High Pending Refunds Saved")

insights = pd.DataFrame({
    "Metric": [
        "Support Records",
        "Finance Records",
        "Escalations",
        "Pending Refunds",
        "Status Mismatches"
    ],
    "Value": [
        len(support),
        len(finance),
        len(escalations),
        len(support[support["Status"]=="Pending"]),
        len(status_mismatch)
    ]
})

insights.to_csv("output/kpi_summary.csv", index=False)


print("\nSummary Saved Successfully")


