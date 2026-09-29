import tkinter as tk
from tkinter import messagebox
import sqlite3

# =========================
# DATABASE
# =========================
conn = sqlite3.connect("netflix.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    genre TEXT,
    year INTEGER,
    rating REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS watchlist (
    username TEXT,
    movie_id INTEGER
)
""")

conn.commit()

# =========================
# SAMPLE MOVIES
# =========================
cursor.execute("SELECT COUNT(*) FROM movies")
if cursor.fetchone()[0] == 0:
    movies = [
        ("Stranger Things", "Sci-Fi", 2016, 8.7),
        ("Wednesday", "Comedy", 2022, 8.0),
        ("Money Heist", "Crime", 2017, 8.2),
        ("Dark", "Sci-Fi", 2017, 8.7),
        ("The Witcher", "Fantasy", 2019, 8.0),
        ("Lucifer", "Fantasy", 2016, 8.0),
        ("Squid Game", "Thriller", 2021, 8.0),
        ("The Night Agent", "Action", 2023, 7.5),
        ("Extraction", "Action", 2020, 6.8),
        ("Interstellar", "Sci-Fi", 2014, 8.7)
    ]
    cursor.executemany(
        "INSERT INTO movies(title, genre, year, rating) VALUES (?, ?, ?, ?)",
        movies
    )
    conn.commit()

# =========================
# MAIN WINDOW
# =========================
root = tk.Tk()
root.title("Netflix Python Project")
root.geometry("900x650")
root.configure(bg="#141414")

current_user = None

def clear_screen():
    for widget in root.winfo_children():
        widget.destroy()

def signup():
    username = username_entry.get().strip()
    password = password_entry.get()

    if not username or not password:
        messagebox.showwarning("Warning", "Enter username and password.")
        return

    try:
        cursor.execute(
            "INSERT INTO users(username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        messagebox.showinfo("Success", "Account created successfully!")
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Username already exists.")

def login():
    global current_user

    username = username_entry.get().strip()
    password = password_entry.get()

    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password)
    )
    user = cursor.fetchone()

    if user:
        current_user = username
        home_screen()
    else:
        messagebox.showerror("Error", "Invalid username or password.")

def add_to_watchlist(movie_id):
    cursor.execute(
        "SELECT * FROM watchlist WHERE username = ? AND movie_id = ?",
        (current_user, movie_id)
    )
    if cursor.fetchone():
        messagebox.showinfo("My List", "Movie is already in your list!")
        return

    cursor.execute(
        "INSERT INTO watchlist(username, movie_id) VALUES (?, ?)",
        (current_user, movie_id)
    )
    conn.commit()
    messagebox.showinfo("My List", "Movie added to your list!")

def show_movies(movie_list):
    clear_screen()

    header = tk.Frame(root, bg="#141414")
    header.pack(fill="x")

    tk.Label(
        header, text="NETFLIX",
        font=("Arial", 25, "bold"),
        fg="red", bg="#141414"
    ).pack(side="left", padx=20, pady=15)

    tk.Button(header, text="HOME", command=home_screen).pack(side="right", padx=10)
    tk.Button(header, text="MY LIST", command=watchlist_screen).pack(side="right")

    content = tk.Frame(root, bg="#141414")
    content.pack(fill="both", expand=True, pady=10)

    if not movie_list:
        tk.Label(
            content, text="No movies found.",
            font=("Arial", 18), fg="white", bg="#141414"
        ).pack(pady=30)
        return

    for movie in movie_list:
        movie_id, title, genre, year, rating = movie

        card = tk.Frame(content, bg="#222222", padx=15, pady=10)
        card.pack(fill="x", padx=100, pady=6)

        tk.Label(
            card,
            text=f"{title}   |   {genre}   |   {year}   |   ⭐ {rating}",
            font=("Arial", 13),
            fg="white", bg="#222222"
        ).pack(side="left")

        tk.Button(
            card, text="ADD TO MY LIST",
            command=lambda x=movie_id: add_to_watchlist(x)
        ).pack(side="right")

def home_screen():
    clear_screen()

    header = tk.Frame(root, bg="#141414")
    header.pack(fill="x")

    tk.Label(
        header, text="NETFLIX",
        font=("Arial", 28, "bold"),
        fg="red", bg="#141414"
    ).pack(side="left", padx=20, pady=15)

    tk.Button(header, text="LOGOUT", command=login_screen).pack(
        side="right", padx=20
    )
    tk.Button(header, text="MY LIST", command=watchlist_screen).pack(side="right")

    tk.Label(
        root,
        text=f"Welcome, {current_user}!",
        font=("Arial", 22, "bold"),
        fg="white", bg="#141414"
    ).pack(pady=15)

    search_frame = tk.Frame(root, bg="#141414")
    search_frame.pack(pady=5)

    search_entry = tk.Entry(search_frame, width=30, font=("Arial", 14))
    search_entry.pack(side="left")

    def search():
        text = search_entry.get().strip()
        cursor.execute(
            "SELECT * FROM movies WHERE title LIKE ? OR genre LIKE ?",
            (f"%{text}%", f"%{text}%")
        )
        show_movies(cursor.fetchall())

    tk.Button(search_frame, text="SEARCH", command=search).pack(side="left", padx=5)
    tk.Button(search_frame, text="SHOW ALL", command=lambda: show_movies(
        get_all_movies()
    )).pack(side="left")

    tk.Label(
        root,
        text="MOVIES & SERIES",
        font=("Arial", 20, "bold"),
        fg="white", bg="#141414"
    ).pack(pady=15)

    list_frame = tk.Frame(root, bg="#141414")
    list_frame.pack(fill="both", expand=True)

    for movie in get_all_movies():
        movie_id, title, genre, year, rating = movie
        tk.Button(
            list_frame,
            text=f"{title}  |  {genre}  |  {year}  |  ⭐ {rating}",
            width=65,
            command=lambda x=movie_id: add_to_watchlist(x)
        ).pack(pady=3)

def get_all_movies():
    cursor.execute("SELECT * FROM movies ORDER BY rating DESC")
    return cursor.fetchall()

def watchlist_screen():
    clear_screen()

    tk.Label(
        root, text="MY LIST",
        font=("Arial", 30, "bold"),
        fg="red", bg="#141414"
    ).pack(pady=30)

    cursor.execute("""
        SELECT movies.title, movies.genre, movies.year, movies.rating
        FROM movies
        JOIN watchlist ON movies.id = watchlist.movie_id
        WHERE watchlist.username = ?
    """, (current_user,))

    movies = cursor.fetchall()

    if not movies:
        tk.Label(
            root, text="Your list is empty.",
            font=("Arial", 18), fg="white", bg="#141414"
        ).pack(pady=20)
    else:
        for title, genre, year, rating in movies:
            tk.Label(
                root,
                text=f"{title}  |  {genre}  |  {year}  |  ⭐ {rating}",
                font=("Arial", 14),
                fg="white", bg="#222222",
                width=60, pady=6
            ).pack(pady=5)

    tk.Button(root, text="BACK TO HOME", command=home_screen).pack(pady=30)

def login_screen():
    clear_screen()

    tk.Label(
        root, text="NETFLIX",
        font=("Arial", 40, "bold"),
        fg="red", bg="#141414"
    ).pack(pady=60)

    global username_entry, password_entry

    username_entry = tk.Entry(root, font=("Arial", 16), width=25)
    username_entry.pack(pady=10)

    password_entry = tk.Entry(root, font=("Arial", 16), width=25, show="*")
    password_entry.pack(pady=10)

    tk.Button(
        root, text="LOGIN",
        font=("Arial", 14, "bold"),
        bg="red", fg="white",
        width=20, command=login
    ).pack(pady=15)

    tk.Button(
        root, text="CREATE ACCOUNT",
        font=("Arial", 12),
        width=20, command=signup
    ).pack()

    tk.Label(
        root,
        text="Python + Tkinter + SQLite",
        font=("Arial", 10),
        fg="gray", bg="#141414"
    ).pack(pady=30)

def on_close():
    conn.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
login_screen()
root.mainloop()
