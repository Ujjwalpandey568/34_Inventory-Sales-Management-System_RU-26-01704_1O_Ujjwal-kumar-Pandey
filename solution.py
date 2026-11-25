import os
import pandas as pd

INV_FILE = "inventory.csv"
SALES_FILE = "sales.csv"


def setup_files():
    if not os.path.exists(INV_FILE):
        df_inv = pd.DataFrame(columns=["ID", "Name", "Stock", "Price"])
        df_inv.to_csv(INV_FILE, index=False)
    if not os.path.exists(SALES_FILE):
        df_sales = pd.DataFrame(columns=["ID", "Quantity", "Amount"])
        df_sales.to_csv(SALES_FILE, index=False)


def format_num(val):
    if float(val).is_integer():
        return int(val)
    return round(float(val), 2)


def load_inventory():
    df = pd.read_csv(INV_FILE, dtype={"ID": str})
    inventory = {}
    for _, row in df.iterrows():
        item_id = str(row["ID"]).strip()
        inventory[item_id] = {
            "Name": str(row["Name"]).strip(),
            "Stock": int(row["Stock"]),
            "Price": format_num(row["Price"])
        }
    return inventory


def save_inventory(inventory):
    rows = []
    for item_id, details in inventory.items():
        rows.append({
            "ID": item_id,
            "Name": details["Name"],
            "Stock": details["Stock"],
            "Price": details["Price"]
        })
    df = pd.DataFrame(rows, columns=["ID", "Name", "Stock", "Price"])
    df.to_csv(INV_FILE, index=False)


def get_next_id(inventory):
    if not inventory:
        return "I101"
    nums = []
    for item_id in inventory:
        if item_id.startswith("I") and item_id[1:].isdigit():
            nums.append(int(item_id[1:]))
    if not nums:
        return "I101"
    return "I" + str(max(nums) + 1)


def clean_id(raw_id, inventory):
    item_id = raw_id.strip().upper()
    if item_id not in inventory and item_id.isdigit() and item_id.startswith("1"):
        alt_id = "I" + item_id[1:]
        if alt_id in inventory:
            return alt_id
    return item_id


def add_item():
    inventory = load_inventory()
    name = input("Name: ").strip()
    try:
        stock = int(input("Stock: ").strip())
        price = format_num(float(input("Price: ").strip()))
    except ValueError:
        print("Invalid stock or price.")
        return

    if stock < 0 or price < 0:
        print("Stock and price cannot be negative.")
        return

    item_id = get_next_id(inventory)
    inventory[item_id] = {
        "Name": name,
        "Stock": stock,
        "Price": price
    }
    save_inventory(inventory)

    print("Item added.")
    print(f"ID: {item_id} | {name} | Stock: {stock} | Price: {price}")


def sell_item():
    inventory = load_inventory()
    item_id = clean_id(input("ID: "), inventory)

    if item_id not in inventory:
        print(f"Item ID {item_id} not found.")
        return

    try:
        qty = int(input("Quantity: ").strip())
    except ValueError:
        print("Invalid quantity.")
        return

    if qty <= 0:
        print("Quantity must be greater than 0.")
        return

    available = inventory[item_id]["Stock"]
    if qty > available:
        print(f"Not enough stock. Available: {available}")
        return

    name = inventory[item_id]["Name"]
    price = inventory[item_id]["Price"]
    amount = format_num(qty * price)

    inventory[item_id]["Stock"] = available - qty
    save_inventory(inventory)

    sales_df = pd.read_csv(SALES_FILE, dtype={"ID": str})
    new_sale = pd.DataFrame([{"ID": item_id, "Quantity": qty, "Amount": amount}])
    sales_df = pd.concat([sales_df, new_sale], ignore_index=True)
    sales_df.to_csv(SALES_FILE, index=False)

    print(f"Sale recorded: {name} x{qty} = {amount}")
    stock_left = inventory[item_id]["Stock"]
    if stock_left == 0:
        print("Stock left: 0 | Item is now out of stock.")
    else:
        print(f"Stock left: {stock_left}")


def update_item():
    inventory = load_inventory()
    item_id = clean_id(input("ID: "), inventory)

    if item_id not in inventory:
        print(f"Item ID {item_id} not found.")
        return

    current = inventory[item_id]
    print(f"Current: {current['Name']} | Stock: {current['Stock']} | Price: {current['Price']}")

    new_name = input("New Name (leave blank to keep same): ").strip()
    new_stock = input("New Stock (leave blank to keep same): ").strip()
    new_price = input("New Price (leave blank to keep same): ").strip()

    if new_name != "":
        current["Name"] = new_name

    try:
        if new_stock != "":
            stock_val = int(new_stock)
            if stock_val < 0:
                print("Stock cannot be negative.")
                return
            current["Stock"] = stock_val
        if new_price != "":
            price_val = format_num(float(new_price))
            if price_val < 0:
                print("Price cannot be negative.")
                return
            current["Price"] = price_val
    except ValueError:
        print("Invalid input.")
        return

    inventory[item_id] = current
    save_inventory(inventory)
    print("Item updated.")
    print(f"ID: {item_id} | {current['Name']} | Stock: {current['Stock']} | Price: {current['Price']}")


def delete_item():
    inventory = load_inventory()
    item_id = clean_id(input("ID: "), inventory)

    if item_id not in inventory:
        print(f"Item ID {item_id} not found.")
        return

    del inventory[item_id]
    save_inventory(inventory)
    print("Item deleted.")


def sales_report():
    inventory = load_inventory()
    sales_df = pd.read_csv(SALES_FILE, dtype={"ID": str})

    if sales_df.empty:
        print("No sales recorded yet.")
        return

    grouped = sales_df.groupby("ID", sort=False).agg({
        "Quantity": "sum",
        "Amount": "sum"
    }).reset_index()

    total_revenue = 0
    best_seller_name = ""
    best_seller_units = -1

    for _, row in grouped.iterrows():
        item_id = str(row["ID"]).strip()
        units = int(row["Quantity"])
        revenue = format_num(row["Amount"])

        if item_id in inventory:
            name = inventory[item_id]["Name"]
        else:
            name = item_id

        print(f"{name}: {units} units | Revenue: {revenue}")

        total_revenue = format_num(total_revenue + revenue)
        if units > best_seller_units:
            best_seller_units = units
            best_seller_name = name

    print(f"Total revenue: {total_revenue}")
    print(f"Best seller: {best_seller_name} ({best_seller_units} units)")


def main():
    setup_files()
    while True:
        print("1. Add item")
        print("2. Sell")
        print("3. Update")
        print("4. Delete")
        print("5. Sales report")
        print("6. Exit")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            add_item()
        elif choice == "2":
            sell_item()
        elif choice == "3":
            update_item()
        elif choice == "4":
            delete_item()
        elif choice == "5":
            sales_report()
        elif choice == "6":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
