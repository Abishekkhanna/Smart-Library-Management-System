import tkinter as tk
from tkinter import messagebox, ttk
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import sqlite3

class LibraryManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Library Management System")
        self.root.geometry("600x600")
        self.root.configure(bg="#f9f9f9")

        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Arial", 12), background="#f9f9f9")
        self.style.configure("TButton", font=("Arial", 12))

        self.header = tk.Label(root, text="Smart Library Management System", font=("Arial", 18, "bold"), bg="#f9f9f9", fg="#333333")
        self.header.pack(pady=20)

        self.label = ttk.Label(root, text="Enter the current rack number:", background="#f9f9f9")
        self.label.pack(pady=10)

        self.rack_entry = ttk.Entry(root, width=20, font=("Arial", 12))
        self.rack_entry.pack(pady=10)

        self.scan_button = ttk.Button(root, text="Scan Barcode", command=self.start_scanning, style="Custom.TButton")
        self.scan_button.pack(pady=20)

        self.result_label = tk.Label(root, text="", font=("Arial", 12), bg="#f9f9f9", fg="#333333")
        self.result_label.pack(pady=10)

        # Additional buttons
        self.view_total_books_button = ttk.Button(root, text="View Total Books", command=self.view_total_books)
        self.view_total_books_button.pack(pady=10)

        self.list_books_button = ttk.Button(root, text="List Books", command=self.list_books)
        self.list_books_button.pack(pady=10)

        self.add_book_button = ttk.Button(root, text="Add Book", command=self.add_book)
        self.add_book_button.pack(pady=10)

        self.close_button = ttk.Button(root, text="Close", command=root.quit)
        self.close_button.pack(pady=10)

    def start_scanning(self):
        current_rack = self.rack_entry.get()
        if not current_rack:
            messagebox.showerror("Input Error", "Please enter a rack number.")
            return

        self.result_label.config(text="Scanning for barcode...")

        # Initialize camera
        cap = cv2.VideoCapture(0)
        output_shown = False

        while not output_shown:
            # Read frame from camera
            ret, frame = cap.read()

            # Decode barcodes
            barcodes = decode(frame)

            # Loop over detected barcodes
            for barcode in barcodes:
                # Extract barcode data
                barcode_data = barcode.data.decode('utf-8')

                # Check if the book is placed in the correct rack
                book_title, correct_rack, genre = self.check_book_placement(barcode_data)

                if book_title:
                    if current_rack == correct_rack:
                        result_text = f"The book '{book_title}' is placed in the correct rack."
                        recommendations = self.recommend_books(genre, book_title)
                        if recommendations:
                            result_text += "\nYou might also like these books from the same genre:"
                            for rec in recommendations:
                                result_text += f"\n- {rec[0]} (Rack {rec[1]})"
                        else:
                            result_text += "\nNo other recommendations available in the same genre."
                    else:
                        result_text = f"The book '{book_title}' is placed in the wrong rack. Please place it in {correct_rack}."

                    self.result_label.config(text=result_text)
                    output_shown = True
                    break

            # Exit loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release camera and close OpenCV windows
        cap.release()
        cv2.destroyAllWindows()

    def check_book_placement(self, barcode_data):
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # Query the database for the book with the given barcode
        cursor.execute('SELECT title, rack_no, genre FROM books WHERE barcode = ?', (barcode_data,))
        book = cursor.fetchone()
        
        conn.close()
        
        if book:
            return book[0], book[1], book[2]
        else:
            return None, None, None

    def recommend_books(self, genre, current_book_title):
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # Query the database for books of the same genre, excluding the current book
        cursor.execute('SELECT title, rack_no FROM books WHERE genre = ? AND title != ? LIMIT 3', (genre, current_book_title))
        recommendations = cursor.fetchall()
        
        conn.close()
        
        return recommendations

    def view_total_books(self):
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM books')
        total_books = cursor.fetchone()[0]
        conn.close()
        messagebox.showinfo("Total Books", f"Total number of books: {total_books}")

    def list_books(self):
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        cursor.execute('SELECT title FROM books')
        books = cursor.fetchall()
        conn.close()
        book_list = "\n".join([book[0] for book in books])
        messagebox.showinfo("List of Books", f"Books:\n{book_list}")

    def add_book(self):
        add_book_window = tk.Toplevel(self.root)
        add_book_window.title("Add Book")
        add_book_window.geometry("300x300")
        add_book_window.configure(bg="#f9f9f9")

        tk.Label(add_book_window, text="Book Title:", bg="#f9f9f9").pack(pady=5)
        title_entry = tk.Entry(add_book_window, width=30)
        title_entry.pack(pady=5)

        tk.Label(add_book_window, text="Barcode:", bg="#f9f9f9").pack(pady=5)
        barcode_entry = tk.Entry(add_book_window, width=30)
        barcode_entry.pack(pady=5)

        tk.Label(add_book_window, text="Rack Number:", bg="#f9f9f9").pack(pady=5)
        rack_entry = tk.Entry(add_book_window, width=30)
        rack_entry.pack(pady=5)

        tk.Label(add_book_window, text="Genre:", bg="#f9f9f9").pack(pady=5)
        genre_entry = tk.Entry(add_book_window, width=30)
        genre_entry.pack(pady=5)

        def save_book():
            title = title_entry.get()
            barcode = barcode_entry.get()
            rack = rack_entry.get()
            genre = genre_entry.get()

            if not title or not barcode or not rack or not genre:
                messagebox.showerror("Input Error", "All fields are required.")
                return

            conn = sqlite3.connect('library.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO books (title, barcode, rack_no, genre) VALUES (?, ?, ?, ?)', (title, barcode, rack, genre))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Book added successfully.")
            add_book_window.destroy()

        ttk.Button(add_book_window, text="Add Book", command=save_book).pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryManagementApp(root)

    # Customizing button style
    root.style = ttk.Style()
    root.style.theme_use('clam')
    root.style.configure('Custom.TButton', background='#007bff', foreground='#ffffff', font=('Arial', 12, 'bold'))

    root.mainloop()
