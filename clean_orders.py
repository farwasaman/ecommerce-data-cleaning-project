"""
Data Cleaning Project: E-Commerce Orders
------------------------------------------
Goal: Take a messy raw orders dataset and clean it into something
analysis-ready, using pandas.

This script is written step-by-step with comments explaining WHY each
step is needed -- not just what the code does. That's the part worth
understanding, not just copying.
"""

import pandas as pd

# -----------------------------------------------------------------
# STEP 1: Load the data and take a first look
# -----------------------------------------------------------------
df = pd.read_csv("messy_orders.csv")

print("Original shape (rows, columns):", df.shape)
print("\nColumn names:", list(df.columns))
print("\nFirst 5 rows:\n", df.head())
print("\nData types:\n", df.dtypes)
print("\nMissing values per column:\n", df.isnull().sum())

# -----------------------------------------------------------------
# STEP 2: Fix column names
# -----------------------------------------------------------------
# Notice "  email" has extra whitespace in the header -- this kind of
# thing breaks code later if you try to reference df["email"] and it
# doesn't exist. Always strip and standardize column names first.
df.columns = df.columns.str.strip()
print("\nCleaned column names:", list(df.columns))

# -----------------------------------------------------------------
# STEP 3: Remove exact duplicate rows
# -----------------------------------------------------------------
# Rows 1001/1005 and 1003/1013 are exact duplicates (same customer,
# same order, submitted twice). In a real system this could be a
# double-click on a checkout button, or a failed retry that logged
# twice. We drop duplicates based on all columns except order_id
# (since order_id itself is always unique).
duplicate_check_cols = [c for c in df.columns if c != "order_id"]
duplicates = df[df.duplicated(subset=duplicate_check_cols, keep="first")]
print(f"\nFound {len(duplicates)} duplicate order(s):\n", duplicates[["order_id", "customer_name"]])

df = df.drop_duplicates(subset=duplicate_check_cols, keep="first")
print("Shape after removing duplicates:", df.shape)

# -----------------------------------------------------------------
# STEP 4: Standardize text formatting
# -----------------------------------------------------------------
# "electronics", "Electronics", and "ELECTRONICS" are the same category
# but pandas treats them as three different values unless we normalize
# casing. Same problem with city names ("rawalpindi" vs "Rawalpindi").
df["product_category"] = df["product_category"].str.strip().str.title()
df["city"] = df["city"].str.strip().str.title()
# .str.replace collapses any double/triple internal spaces (e.g. "Usman  Tariq")
# down to single spaces, then .str.title() fixes casing (e.g. "sara khan" -> "Sara Khan")
df["customer_name"] = df["customer_name"].str.strip().str.replace(r"\s+", " ", regex=True).str.title()

print("\nUnique categories after cleaning:", df["product_category"].unique())
print("Unique cities after cleaning:", df["city"].unique())

# -----------------------------------------------------------------
# STEP 5: Fix inconsistent date formats
# -----------------------------------------------------------------
# The order_date column has at least 4 different formats mixed together:
# 2024-01-05, 01/06/2024, 2024/01/09, 13-01-2024
#
# IMPORTANT LESSON: pd.to_datetime(..., format="mixed", dayfirst=True)
# looks like the obvious fix, but it's actually a trap -- dayfirst=True
# can silently swap day/month even on unambiguous ISO dates like
# "2024-01-05", turning Jan 5th into May 1st with NO error or warning.
# Always verify a few known values after parsing dates, don't trust it blindly.
#
# The safer approach: try each known format explicitly, in order, and
# only fall back to inference if none match.
# Note on 01/06/2024: this is genuinely ambiguous (Jan 6 or June 1?).
# Format alone can't resolve it -- you have to use context. Since this
# row's order_id (1002) falls between order 1001 (Jan 5) and order 1003
# (Jan 7), it's almost certainly Jan 6 in MM/DD/YYYY format. This is a
# realistic example of why date cleaning sometimes needs judgment, not
# just code -- always sanity-check against neighboring data when a
# format is ambiguous.
def parse_date(value):
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d", "%d-%m-%Y"):
        try:
            return pd.to_datetime(value, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.NaT  # couldn't match any known format

df["order_date"] = df["order_date"].apply(parse_date)
print("\nRows where date couldn't be parsed:\n", df[df["order_date"].isnull()][["order_id", "order_date"]])

# -----------------------------------------------------------------
# STEP 6: Handle missing values
# -----------------------------------------------------------------
# Different columns need different strategies -- there's no single
# "fill everything with 0" answer:
# - Missing customer_name: can't guess a name, so we flag it instead
# - Missing email: same, flag rather than invent
# - Missing quantity: fill with 1 (most common single-item order) is
#   a reasonable assumption here, but in real work you'd confirm this
#   with whoever owns the data
# - Missing unit_price: fill with the median price for that category,
#   since prices vary a lot by category (electronics vs books)

df["customer_name"] = df["customer_name"].fillna("Unknown")
df["email"] = df["email"].fillna("Not Provided")

df["quantity"] = df["quantity"].fillna(1)

category_median_price = df.groupby("product_category")["unit_price"].transform("median")
df["unit_price"] = df["unit_price"].fillna(category_median_price)

print("\nMissing values after cleaning:\n", df.isnull().sum())

# -----------------------------------------------------------------
# STEP 7: Fix invalid / suspicious values
# -----------------------------------------------------------------
# Quantity of -1 doesn't make sense for an order -- likely a data entry
# error or a return that got logged incorrectly. We flag these rather
# than silently deleting, since that decision usually needs a human.
invalid_quantity = df[df["quantity"] < 0]
print("\nRows with invalid (negative) quantity:\n", invalid_quantity[["order_id", "quantity"]])
df.loc[df["quantity"] < 0, "quantity"] = df["quantity"].abs()

# unit_price of 999999 is an obvious outlier/typo compared to similar
# electronics items (~15,000-45,000 range). We flag it for review
# instead of guessing the "correct" value.
price_outliers = df[df["unit_price"] > 100000]
print("\nPossible price outliers (needs manual review):\n", price_outliers[["order_id", "product_category", "unit_price"]])

# -----------------------------------------------------------------
# STEP 8: Create a useful derived column
# -----------------------------------------------------------------
# This is a common step in real analysis -- adding calculated fields
# that make the dataset more useful downstream (e.g. for a Power BI
# dashboard or a summary report).
df["total_amount"] = df["quantity"] * df["unit_price"]

# -----------------------------------------------------------------
# STEP 9: Final check and export
# -----------------------------------------------------------------
print("\nFinal cleaned data:\n", df)
print("\nFinal shape:", df.shape)

df.to_csv("cleaned_orders.csv", index=False)
print("\nSaved cleaned dataset to cleaned_orders.csv")

# -----------------------------------------------------------------
# STEP 10: Quick summary (this is the kind of insight you'd put in
# your LinkedIn post or portfolio write-up)
# -----------------------------------------------------------------
summary = df.groupby("product_category")["total_amount"].sum().sort_values(ascending=False)
print("\nRevenue by category:\n", summary)
