import sqlite3
from tabulate import tabulate

# Create or connect to the database
conn = sqlite3.connect('glossary.db')
cursor = conn.cursor()

# Create table for storing products
cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,  -- Ensure product names are unique
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
    name = input("Enter product name: ").strip()
    price = float(input("Enter product price: "))
    quantity = int(input("Enter product quantity: "))

    # Check if the product already exists
    cursor.execute('SELECT * FROM products WHERE name = ?', (name,))
    existing_item = cursor.fetchone()

    if existing_item:
        # Update the product's price and quantity
        cursor.execute('''
            UPDATE products
            SET price = ?, quantity = quantity + ?
            WHERE name = ?
        ''', (price, quantity, name))
        conn.commit()
        print(f"{name} updated successfully! New Quantity: {existing_item[3] + quantity}, Price: {price}")
    else:
        # Insert the new product if it doesn't exist
        cursor.execute('''
            INSERT INTO products (name, price, quantity)
            VALUES (?, ?, ?)
        ''', (name, price, quantity))
        conn.commit()
        print(f"{name} added successfully!")

def delete_item():
    view_items()
    item_id = input("\nEnter the ID of the product to delete: ")

    # Check if the item exists
    cursor.execute('SELECT * FROM products WHERE id = ?', (item_id,))
    item = cursor.fetchone()

    if item:
        cursor.execute('DELETE FROM products WHERE id = ?', (item_id,))
        conn.commit()
        print(f"{item[1]} deleted successfully!")
        rearrange_ids()  # Call to rearrange IDs after deletion
    else:
        print("Invalid product ID. Please try again.")

def rearrange_ids():
    # Get all the current data
    cursor.execute('SELECT name, price, quantity FROM products')
    items = cursor.fetchall()

    # Drop the original table
    cursor.execute('DROP TABLE IF EXISTS products')

    # Recreate the table
    cursor.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL
        )
    ''')

    # Reinsert data with sequential IDs
    cursor.executemany('''
        INSERT INTO products (name, price, quantity)
        VALUES (?, ?, ?)
    ''', items)
    
    conn.commit()

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
        print("4. Delete Item")
        print("5. Exit")

        choice = input("Enter your choice: ")
        if choice == '1':
            view_items()
        elif choice == '2':
            add_item()
        elif choice == '3':
            view_items()
            generate_bill()
        elif choice == '4':
            delete_item()
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

# Close the database connection when the program ends
conn.close()
