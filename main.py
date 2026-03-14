import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3, json, os
import matplotlib.pyplot as plt

class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🏆 Award-Worthy Library System")
        self.root.configure(bg="#f0f8ff")

        self.conn = sqlite3.connect("library.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS books (
                                isbn TEXT PRIMARY KEY,
                                title TEXT,
                                author TEXT,
                                year TEXT,
                                publisher TEXT)""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS borrowers (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT,
                                isbn TEXT,
                                borrow_date TEXT,
                                return_date TEXT,
                                FOREIGN KEY(isbn) REFERENCES books(isbn))""")
        self.conn.commit()

        input_frame = tk.LabelFrame(root, text="Book Details", bg="#e6f7ff", fg="black")
        input_frame.pack(fill="x", padx=10, pady=10)

        labels = ["ISBN", "Title", "Author", "Year", "Publisher"]
        self.entries = {}

        for i, label in enumerate(labels):
            tk.Label(input_frame, text=label, bg="#e6f7ff").grid(row=i, column=0, padx=5, pady=5)
            entry = tk.Entry(input_frame, bg="#ffffff", fg="black")
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries[label.lower()] = entry

        tk.Button(root, text="Insert Book", bg="#4CAF50", fg="white", command=self.insert_book).pack(pady=5)
        tk.Button(root, text="Update Book", bg="#FF9800", fg="white", command=self.update_book).pack(pady=5)
        tk.Button(root, text="Delete Book", bg="#f44336", fg="white", command=self.delete_book).pack(pady=5)
        tk.Button(root, text="Search Book", bg="#2196F3", fg="white", command=self.search_book).pack(pady=5)
        tk.Button(root, text="Show All Books", bg="#9C27B0", fg="white", command=self.show_books).pack(pady=5)
        tk.Button(root, text="Borrow Book", bg="#607D8B", fg="white", command=self.borrow_book).pack(pady=5)
        tk.Button(root, text="Return Book", bg="#795548", fg="white", command=self.return_book).pack(pady=5)
        tk.Button(root, text="Export Book", bg="#3F51B5", fg="white", command=self.export_book).pack(pady=5)
        tk.Button(root, text="Analytics Dashboard", bg="#009688", fg="white", command=self.show_dashboard).pack(pady=5)
        tk.Button(root, text="Exit", bg="#000000", fg="white", command=root.quit).pack(pady=5)

        self.tree = ttk.Treeview(root, columns=("ISBN", "Title", "Author", "Year", "Publisher"), show="headings")
        for col in ("ISBN", "Title", "Author", "Year", "Publisher"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.status = tk.Label(root, text="Welcome to Award-Worthy Library System", bd=1, relief="sunken", anchor="w", bg="#333", fg="white")
        self.status.pack(side="bottom", fill="x")

        self.show_books()

    def insert_book(self):
        data = {k: e.get() for k, e in self.entries.items()}
        if not all(data.values()):
            messagebox.showwarning("Input Error", "All fields must be filled!")
            return
        try:
            self.cursor.execute("INSERT INTO books VALUES (?, ?, ?, ?, ?)", tuple(data.values()))
            self.conn.commit()
            self.status.config(text=f"Book '{data['title']}' inserted")
            self.show_books()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Book with this ISBN already exists!")

    def update_book(self):
        data = {k: e.get() for k, e in self.entries.items()}
        self.cursor.execute("""UPDATE books SET title=?, author=?, year=?, publisher=? WHERE isbn=?""",
                            (data["title"], data["author"], data["year"], data["publisher"], data["isbn"]))
        self.conn.commit()
        self.status.config(text=f"Book '{data['isbn']}' updated")
        self.show_books()

    def delete_book(self):
        isbn = self.entries["isbn"].get()
        self.cursor.execute("DELETE FROM books WHERE isbn=?", (isbn,))
        self.conn.commit()
        self.status.config(text=f"Book {isbn} deleted")
        self.show_books()

    def search_book(self):
        isbn = self.entries["isbn"].get()
        title = self.entries["title"].get()

        if isbn:
            self.cursor.execute("SELECT * FROM books WHERE isbn=?", (isbn,))
        elif title:
            self.cursor.execute("SELECT * FROM books WHERE title LIKE ?", ('%' + title + '%',))
        else:
            messagebox.showwarning("Input Error", "Enter ISBN or Title to search!")
            return

        rows = self.cursor.fetchall()
        self.update_tree(rows)
        self.status.config(text=f"Search returned {len(rows)} result(s)")

    def show_books(self):
        self.cursor.execute("SELECT * FROM books")
        rows = self.cursor.fetchall()
        self.update_tree(rows)
        self.status.config(text=f"{len(rows)} book(s) in library")

    def update_tree(self, rows):
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def borrow_book(self):
        name = self.entries["author"].get()
        isbn = self.entries["isbn"].get()

        self.cursor.execute("SELECT * FROM books WHERE isbn=?", (isbn,))
        book = self.cursor.fetchone()

        if book:
            self.cursor.execute("INSERT INTO borrowers (name, isbn, borrow_date) VALUES (?, ?, DATE('now'))", (name, isbn))
            self.conn.commit()
            self.status.config(text=f"{name} borrowed {book[1]}")
        else:
            messagebox.showerror("Error", "Book not found!")

    def return_book(self):
        isbn = self.entries["isbn"].get()
        self.cursor.execute("UPDATE borrowers SET return_date=DATE('now') WHERE isbn=? AND return_date IS NULL", (isbn,))
        self.conn.commit()
        self.status.config(text=f"Book {isbn} returned")

    def export_book(self):
        isbn = self.entries["isbn"].get()
        self.cursor.execute("SELECT * FROM books WHERE isbn=?", (isbn,))
        row = self.cursor.fetchone()

        if row:
            book_data = {"isbn": row[0], "title": row[1], "author": row[2], "year": row[3], "publisher": row[4]}
            folder = f"exports/{row[2]}"
            os.makedirs(folder, exist_ok=True)
            filename = os.path.join(folder, f"{isbn}.json")

            with open(filename, "w") as f:
                json.dump(book_data, f, indent=4)

            self.status.config(text=f"Book exported to {filename}")
        else:
            messagebox.showerror("Error", "Book not found!")

    def show_dashboard(self):
        self.cursor.execute("SELECT COUNT(*) FROM books")
        total_books = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM borrowers WHERE return_date IS NULL")
        borrowed_books = self.cursor.fetchone()[0]

        labels = ["Total Books", "Borrowed Books"]
        values = [total_books, borrowed_books]

        plt.bar(labels, values, color=["#4CAF50", "#f44336"])
        plt.title("Library Dashboard")
        plt.show()


if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()