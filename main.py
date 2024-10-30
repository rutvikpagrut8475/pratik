import sqlite3
from tabulate import tabulate

# Create or connect to the database
conn = sqlite3.connect('glossary.db')
cursor = conn.cursor()

# Create table for storing products
cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL
    )
''')
conn.commit()

def view_items():
    cursor.execute('SELECT * FROM products')
    items = cursor.fetchall()
    if items:
        print(tabulate(items, headers=["ID", "Name", "Price", "Quantity"], tablefmt="grid"))
    else:
        print("No items available in the glossary.")

def add_item():
    name = input("Enter product name: ")
    price = float(input("Enter product price: "))
    quantity = int(input("Enter product quantity: "))
    
    cursor.execute('''
        INSERT INTO products (name, price, quantity)
        VALUES (?, ?, ?)
    ''', (name, price, quantity))
    conn.commit()
    print(f"{name} added successfully!")

def generate_bill():
    bill_items = []
    total_amount = 0

    while True:
        item_id = input("Enter product ID to add to the bill (or 'done' to finish): ")
        if item_id.lower() == 'done':
            break

        cursor.execute('SELECT * FROM products WHERE id = ?', (item_id,))
        item = cursor.fetchone()
        if item:
            quantity = int(input(f"Enter quantity for {item[1]}: "))
            if quantity > item[3]:
                print(f"Not enough stock! Available: {item[3]}")
                continue

            # Add item to bill
            bill_items.append([item[1], item[2], quantity, item[2] * quantity])
            total_amount += item[2] * quantity

            # Update stock quantity in the database
            cursor.execute('''
                UPDATE products
                SET quantity = quantity - ?
                WHERE id = ?
            ''', (quantity, item_id))
            conn.commit()
        else:
            print("Invalid product ID. Please try again.")

    # Display the final bill
    print("\n--- Bill Summary ---")
    print(tabulate(bill_items, headers=["Name", "Price", "Quantity", "Total"], tablefmt="grid"))
    print(f"\nTotal Amount: ₹{total_amount:.2f}")

def main():
    while True:
        print("\n--- Glossary Management ---")
        print("1. View Items")
        print("2. Add Item")
        print("3. Generate Bill")
        print("4. Exit")

        choice = input("Enter your choice: ")
        if choice == '1':
            view_items()
        elif choice == '2':
            add_item()
        elif choice == '3':
            generate_bill()
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

# Close the database connection when the program ends
conn.close()
