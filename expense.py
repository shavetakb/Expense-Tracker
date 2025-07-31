import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime, timedelta
from tkcalendar import DateEntry  

# Create Database for expenses
def init_db():
    conn = sqlite3.connect("expenses.db")
    c = conn.cursor()
    
    # Create the table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            amount REAL,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Add expense to database
def add_expense():
    category = category_entry.get().strip()
    amount = amount_entry.get().strip()
    date = date_entry.get().strip()

    if not category or not amount:
        messagebox.showerror("Error", "Category and Amount are required!")
        return

    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror("Error", "Amount must be a valid number!")
        return

    if not date:
        date = datetime.today().strftime('%Y-%m-%d')  # Default to today's date

    try:
        # Validate date format
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        messagebox.showerror("Error", "Date must be in YYYY-MM-DD format!")
        return

    conn = sqlite3.connect("expenses.db")
    c = conn.cursor()
    c.execute('''
        INSERT INTO expenses (category, amount, date)
        VALUES (?, ?, ?)
    ''', (category, amount, date))
    conn.commit()
    conn.close()

    category_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    date_entry.delete(0, tk.END)

    messagebox.showinfo("Success", "Expense added successfully!")
    show_all_expenses()

# Filter expenses for the given period
def filter_expenses(period="week"):
    try:
        if period == "week":
            end_date = datetime.today()
            start_date = end_date - timedelta(days=end_date.weekday())  # Start of week (Monday)
        elif period == "month":
            end_date = datetime.today()
            start_date = end_date.replace(day=1)  # Start of month

        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()
        c.execute('''SELECT * FROM expenses WHERE date BETWEEN ? AND ?''', (start_date_str, end_date_str))
        records = c.fetchall()
        conn.close()

        total_expense = sum([row[2] for row in records])
        total_expense_label.config(text=f"Total Expense ({period.capitalize()}): ₹{total_expense:.2f}")

        expenses_tree.delete(*expenses_tree.get_children())
        for row in records:
            expenses_tree.insert("", "end", values=row)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# GUI Setup
app = tk.Tk()
app.title("Expense Tracker")
app.geometry("700x500")

def delete_expense():
    selected_item = expenses_tree.selection()
    if not selected_item:
        messagebox.showwarning("Warning", "Please select an entry to delete.")
        return

    # Get the selected record's ID
    item = expenses_tree.item(selected_item)
    expense_id = item['values'][0]

    # Confirm delete
    confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this expense?")
    if not confirm:
        return

    try:
        conn = sqlite3.connect("expenses.db")
        c = conn.cursor()
        c.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()
        conn.close()

        # Remove from Treeview
        # Refresh the full list and update total
        show_all_expenses()


    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while deleting: {e}")

def show_all_expenses():
    try:
        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()
        c.execute("SELECT * FROM expenses")
        records = c.fetchall()
        conn.close()

        # Clear the Treeview
        expenses_tree.delete(*expenses_tree.get_children())

        # Insert all records into Treeview
        for row in records:
            expenses_tree.insert("", "end", values=row)

        # Update total expense
        total = sum([row[2] for row in records])
        total_expense_label.config(text=f"Total Expense (All): ₹{total:.2f}")

    except Exception as e:
        messagebox.showerror("Error", f"Error loading records: {e}")

# Initialize the database
init_db()

tk.Label(app, text="Expense Tracker", font=("Arial", 20)).pack(pady=10)

frame = tk.Frame(app)
frame.pack(pady=10)

tk.Label(frame, text="Category:", font=("Arial", 12)).grid(row=0, column=0, padx=10)
category_entry = tk.Entry(frame, font=("Arial", 12))
category_entry.grid(row=0, column=1, padx=10)

tk.Label(frame, text="Amount:", font=("Arial", 12)).grid(row=1, column=0, padx=10)
amount_entry = tk.Entry(frame, font=("Arial", 12))
amount_entry.grid(row=1, column=1, padx=10)

tk.Label(frame, text="Date:", font=("Arial", 12)).grid(row=2, column=0, padx=10)
date_entry = DateEntry(frame, font=("Arial", 12), width=17, date_pattern='yyyy-mm-dd', maxdate=datetime.today())
date_entry.grid(row=2, column=1, padx=10)

add_button = tk.Button(app, text="Add Expense", font=("Arial", 12), command=add_expense)
add_button.pack(pady=5)

total_expense_label = tk.Label(app, text="Total Expense (Week): ₹0.00", font=("Arial", 14))
total_expense_label.pack(pady=10)

week_button = tk.Button(app, text="Show Weekly Expenses", font=("Arial", 12), command=lambda: filter_expenses("week"))
week_button.pack(pady=5)

month_button = tk.Button(app, text="Show Monthly Expenses", font=("Arial", 12), command=lambda: filter_expenses("month"))
month_button.pack(pady=5)

delete_button = tk.Button(app, text="Delete Selected Expense", font=("Arial", 12), command=delete_expense)
delete_button.pack(pady=5)

columns = ("ID", "Category", "Amount", "Date")
expenses_tree = ttk.Treeview(app, columns=columns, show="headings")
for col in columns:
    expenses_tree.heading(col, text=col)
    expenses_tree.column(col, width=150)
expenses_tree.pack(pady=10, fill='x')

app.mainloop()