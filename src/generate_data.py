import csv
import random
from datetime import datetime, timedelta
from pathlib import Path


# =========================================
# Configuration
# =========================================

NUM_CUSTOMERS = 10_000
NUM_PRODUCTS = 1_000
NUM_ORDERS = 100_000

OUTPUT_DIR = Path("data/large")


# =========================================
# Sample data
# =========================================

first_names = [
    "Anu", "Rahul", "Meera", "Arjun", "Sneha",
    "Vishnu", "Diya", "Adithya", "Priya", "Nikhil",
    "Akhil", "Neha", "Kiran", "Asha", "Rohan"
]

cities_states = [
    ("Kochi", "Kerala"),
    ("Thiruvananthapuram", "Kerala"),
    ("Kozhikode", "Kerala"),
    ("Kollam", "Kerala"),
    ("Chennai", "Tamil Nadu"),
    ("Coimbatore", "Tamil Nadu"),
    ("Bangalore", "Karnataka"),
    ("Mysore", "Karnataka"),
    ("Hyderabad", "Telangana"),
    ("Pune", "Maharashtra"),
    ("Mumbai", "Maharashtra"),
    ("Delhi", "Delhi")
]

products = [
    ("Laptop", "Electronics", 65000),
    ("Wireless Mouse", "Electronics", 800),
    ("Keyboard", "Electronics", 1500),
    ("Office Chair", "Furniture", 8500),
    ("Desk", "Furniture", 12000),
    ("Headphones", "Electronics", 2500),
    ("Backpack", "Accessories", 1800),
    ("Smart Watch", "Electronics", 5500),
    ("Water Bottle", "Accessories", 700),
    ("Monitor", "Electronics", 15000),
    ("Webcam", "Electronics", 3500),
    ("Desk Lamp", "Furniture", 2200),
    ("USB Cable", "Electronics", 500),
    ("Power Bank", "Electronics", 1800),
    ("Notebook", "Stationery", 250)
]


# =========================================
# Create output directory
# =========================================

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =========================================
# 1. Generate Customers
# =========================================

print("Generating customers...")

customers = []

with open(OUTPUT_DIR / "customers.csv", "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "customer_id",
        "customer_name",
        "city",
        "state"
    ])

    for i in range(1, NUM_CUSTOMERS + 1):

        customer_id = f"C{i:05d}"

        customer_name = random.choice(first_names)

        city, state = random.choice(cities_states)

        customers.append(customer_id)

        writer.writerow([
            customer_id,
            customer_name,
            city,
            state
        ])


print(f"Customers generated: {NUM_CUSTOMERS}")


# =========================================
# 2. Generate Products
# =========================================

print("Generating products...")

product_records = []

with open(OUTPUT_DIR / "products.csv", "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "product_id",
        "product_name",
        "category",
        "price"
    ])

    for i in range(1, NUM_PRODUCTS + 1):

        product_id = f"P{i:04d}"

        product_name, category, base_price = random.choice(products)

        price = round(
            base_price * random.uniform(0.8, 1.2),
            2
        )

        product_records.append(
            (product_id, price)
        )

        writer.writerow([
            product_id,
            f"{product_name} {i}",
            category,
            price
        ])


print(f"Products generated: {NUM_PRODUCTS}")


# =========================================
# 3. Generate Orders
# =========================================

print("Generating orders...")

order_records = []

# Start and end dates for historical orders
start_date = datetime(2026, 1, 1)
end_date = datetime(2026, 9, 16)

# Number of days between start and end date
date_range = (end_date - start_date).days

with open(OUTPUT_DIR / "orders.csv", "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "order_id",
        "customer_id",
        "order_date"
    ])

    for i in range(1, NUM_ORDERS + 1):

        order_id = f"O{i:06d}"

        customer_id = random.choice(customers)

        # Generate a random date between
        # January 1, 2026 and September 16, 2026
        random_days = random.randint(0, date_range)

        order_date = start_date + timedelta(
            days=random_days
        )

        order_records.append(order_id)

        writer.writerow([
            order_id,
            customer_id,
            order_date.strftime("%Y-%m-%d")
        ])


print(f"Orders generated: {NUM_ORDERS}")


# =========================================
# 4. Generate Order Items
# =========================================

print("Generating order items...")

order_item_id = 1

with open(
    OUTPUT_DIR / "order_items.csv",
    "w",
    newline=""
) as file:

    writer = csv.writer(file)

    writer.writerow([
        "order_item_id",
        "order_id",
        "product_id",
        "quantity"
    ])

    for order_id in order_records:

        # Each order contains between 1 and 4 products
        number_of_items = random.randint(1, 4)

        selected_products = random.sample(
            product_records,
            number_of_items
        )

        for product_id, _ in selected_products:

            quantity = random.randint(1, 5)

            writer.writerow([
                order_item_id,
                order_id,
                product_id,
                quantity
            ])

            order_item_id += 1


print("Order items generated successfully!")


# =========================================
# Completed
# =========================================

print("\nLarge dataset generation completed.")