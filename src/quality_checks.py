import pandas as pd


# =========================================
# File paths
# =========================================

DATA_DIR = "data/large"


# =========================================
# Load datasets
# =========================================

print("Loading datasets...")

customers = pd.read_csv(f"{DATA_DIR}/customers.csv")
products = pd.read_csv(f"{DATA_DIR}/products.csv")
orders = pd.read_csv(f"{DATA_DIR}/orders.csv")
order_items = pd.read_csv(f"{DATA_DIR}/order_items.csv")


print("Datasets loaded successfully!")

print("\nDataset sizes")
print("-------------------------")
print(f"Customers   : {len(customers)}")
print(f"Products    : {len(products)}")
print(f"Orders      : {len(orders)}")
print(f"Order Items : {len(order_items)}")
# =========================================
# Duplicate ID Checks
# =========================================

print("\nDuplicate ID Checks")
print("-------------------------")

customer_duplicates = customers["customer_id"].duplicated().sum()
product_duplicates = products["product_id"].duplicated().sum()
order_duplicates = orders["order_id"].duplicated().sum()
order_item_duplicates = order_items["order_item_id"].duplicated().sum()


print(f"Customer ID duplicates     : {customer_duplicates}")
print(f"Product ID duplicates     : {product_duplicates}")
print(f"Order ID duplicates       : {order_duplicates}")
print(f"Order Item ID duplicates  : {order_item_duplicates}")
# =========================================
# Missing Value Checks
# =========================================

print("\nMissing Value Checks")
print("-------------------------")

print("\nCustomers:")
print(f"Missing customer_id   : {customers['customer_id'].isna().sum()}")
print(f"Missing customer_name  : {customers['customer_name'].isna().sum()}")
print(f"Missing city           : {customers['city'].isna().sum()}")
print(f"Missing state          : {customers['state'].isna().sum()}")

print("\nProducts:")
print(f"Missing product_id     : {products['product_id'].isna().sum()}")
print(f"Missing product_name   : {products['product_name'].isna().sum()}")
print(f"Missing category       : {products['category'].isna().sum()}")
print(f"Missing price          : {products['price'].isna().sum()}")

print("\nOrders:")
print(f"Missing order_id       : {orders['order_id'].isna().sum()}")
print(f"Missing customer_id    : {orders['customer_id'].isna().sum()}")
print(f"Missing order_date     : {orders['order_date'].isna().sum()}")

print("\nOrder Items:")
print(f"Missing order_item_id  : {order_items['order_item_id'].isna().sum()}")
print(f"Missing order_id       : {order_items['order_id'].isna().sum()}")
print(f"Missing product_id     : {order_items['product_id'].isna().sum()}")
print(f"Missing quantity       : {order_items['quantity'].isna().sum()}")
# =========================================
# Referential Integrity Checks
# =========================================

print("\nReferential Integrity Checks")
print("-------------------------")


# Check 1: Orders → Customers

invalid_order_customers = orders[
    ~orders["customer_id"].isin(customers["customer_id"])
]

print(
    f"Orders with invalid customer IDs : "
    f"{len(invalid_order_customers)}"
)


# Check 2: Order Items → Orders

invalid_order_items_orders = order_items[
    ~order_items["order_id"].isin(orders["order_id"])
]

print(
    f"Order items with invalid order IDs : "
    f"{len(invalid_order_items_orders)}"
)


# Check 3: Order Items → Products

invalid_order_items_products = order_items[
    ~order_items["product_id"].isin(products["product_id"])
]

print(
    f"Order items with invalid product IDs : "
    f"{len(invalid_order_items_products)}"
)
# =========================================
# Business Rule Checks
# =========================================

print("\nBusiness Rule Checks")
print("-------------------------")

# Quantity must be greater than 0
invalid_quantities = order_items[
    order_items["quantity"] <= 0
]

# Product price must be greater than 0
invalid_prices = products[
    products["price"] <= 0
]

# Order date must not be in the future
orders["order_date"] = pd.to_datetime(orders["order_date"])

today = pd.Timestamp("2026-09-16")

future_orders = orders[
    orders["order_date"] > today
]


print(f"Invalid quantities : {len(invalid_quantities)}")
print(f"Invalid prices     : {len(invalid_prices)}")
print(f"Future orders      : {len(future_orders)}")


# =========================================
# Final Data Quality Result
# =========================================

total_errors = (
    customer_duplicates
    + product_duplicates
    + order_duplicates
    + order_item_duplicates
    + len(invalid_order_customers)
    + len(invalid_order_items_orders)
    + len(invalid_order_items_products)
    + len(invalid_quantities)
    + len(invalid_prices)
    + len(future_orders)
)


print("\n========================================")
print("        DATA QUALITY RESULT")
print("========================================")

if total_errors == 0:
    print("STATUS : PASSED")
    print("All data quality checks passed!")
else:
    print("STATUS : FAILED")
    print(f"Total errors detected : {total_errors}")

print("========================================")