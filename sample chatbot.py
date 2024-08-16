import re
import random
import json
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext, messagebox
from colorama import init, Fore
import os
import sqlite3
from googletrans import Translator  # For multi-language support

# Initialize colorama
init(autoreset=True)

class ChatBot:
    def __init__(self, responses_file='C:\\Users\\User\\Desktop\\AI,ML Projects\\AI (Python)\\responses.json'):
        print(Fore.CYAN + f"Current working directory: {os.getcwd()}")
        print(Fore.CYAN + f"Expected file path: {os.path.abspath(responses_file)}")
        self.load_responses(responses_file)
        self.greetings = {
            "morning": "Good morning! How can I assist you today?",
            "afternoon": "Good afternoon! How can I assist you today?",
            "evening": "Good evening! How can I assist you today?",
            "night": "Hello! How can I assist you today?"
        }
        self.translator = Translator()  # Initialize the translator for multi-language support
        self.db = sqlite3.connect('chatbot_users.db')  # SQLite database for user profiles
        self.create_user_table()

    def create_user_table(self):
        with self.db:
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT,
                    preferences TEXT
                )
            """)

    def load_responses(self, file_path):
        try:
            with open(file_path, 'r') as file:
                self.responses = json.load(file)
            print(Fore.GREEN + "Responses loaded successfully.")
        except FileNotFoundError:
            print(Fore.RED + f"Error: The file '{file_path}' was not found.")
            self.responses = {}
        except json.JSONDecodeError:
            print(Fore.RED + "Error: The file is not a valid JSON.")
            self.responses = {}

    def get_greeting(self):
        current_hour = datetime.now().hour
        if 5 <= current_hour < 12:
            return self.greetings["morning"]
        elif 12 <= current_hour < 17:
            return self.greetings["afternoon"]
        elif 17 <= current_hour < 21:
            return self.greetings["evening"]
        else:
            return self.greetings["night"]

    def get_response(self, user_input):
        user_input = user_input.lower()
        for pattern, responses in self.responses.items():
            if re.search(pattern, user_input):
                return random.choice(responses)
        return "I'm sorry, I don't understand that. Can you please rephrase?"

    def translate_text(self, text, dest_language='en'):
        try:
            translation = self.translator.translate(text, dest=dest_language)
            return translation.text
        except Exception as e:
            print(Fore.RED + f"Translation error: {e}")
            return text

    def run(self):
        self.root = tk.Tk()
        self.root.title("Chatbot Login")
        self.root.configure(bg='#2c3e50')

        self.login_frame = tk.Frame(self.root, bg='#2c3e50')
        self.login_frame.pack(padx=20, pady=20)

        self.username_label = tk.Label(self.login_frame, text="Username:", bg='#2c3e50', fg='white', font=('Arial', 12))
        self.username_label.pack(pady=5)

        self.username_entry = tk.Entry(self.login_frame, font=('Arial', 12))
        self.username_entry.pack(pady=5)

        self.password_label = tk.Label(self.login_frame, text="Password:", bg='#2c3e50', fg='white', font=('Arial', 12))
        self.password_label.pack(pady=5)

        self.password_entry = tk.Entry(self.login_frame, show='*', font=('Arial', 12))
        self.password_entry.pack(pady=5)

        self.login_button = tk.Button(self.login_frame, text="Login", command=self.authenticate, bg='#3498db', fg='white', font=('Arial', 12), relief='flat')
        self.login_button.pack(pady=10)

        self.signup_button = tk.Button(self.login_frame, text="Sign Up", command=self.show_signup_window, bg='#3498db', fg='white', font=('Arial', 12), relief='flat')
        self.signup_button.pack(pady=10)

        self.root.mainloop()

    def show_signup_window(self):
        self.signup_window = tk.Toplevel(self.root)
        self.signup_window.title("Sign Up")
        self.signup_window.configure(bg='#2c3e50')

        self.signup_frame = tk.Frame(self.signup_window, bg='#2c3e50')
        self.signup_frame.pack(padx=20, pady=20)

        self.signup_username_label = tk.Label(self.signup_frame, text="Username:", bg='#2c3e50', fg='white', font=('Arial', 12))
        self.signup_username_label.pack(pady=5)

        self.signup_username_entry = tk.Entry(self.signup_frame, font=('Arial', 12))
        self.signup_username_entry.pack(pady=5)

        self.signup_password_label = tk.Label(self.signup_frame, text="Password:", bg='#2c3e50', fg='white', font=('Arial', 12))
        self.signup_password_label.pack(pady=5)

        self.signup_password_entry = tk.Entry(self.signup_frame, show='*', font=('Arial', 12))
        self.signup_password_entry.pack(pady=5)

        self.signup_button = tk.Button(self.signup_frame, text="Register", command=self.register_user, bg='#3498db', fg='white', font=('Arial', 12), relief='flat')
        self.signup_button.pack(pady=10)

    def register_user(self):
        username = self.signup_username_entry.get()
        password = self.signup_password_entry.get()
        if username and password:
            with self.db:
                self.db.execute("INSERT OR REPLACE INTO users (username, password, preferences) VALUES (?, ?, ?)",
                                (username, password, ''))
            messagebox.showinfo("Success", "Registration successful. You can now log in.")
            self.signup_window.destroy()
        else:
            messagebox.showerror("Error", "Please provide both username and password.")

    def authenticate(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if self.check_user_credentials(username, password):
            self.login_frame.destroy()
            self.create_chat_interface(username)
        else:
            messagebox.showerror("Error", "Incorrect username or password. Access denied.")

    def check_user_credentials(self, username, password):
        with self.db:
            cursor = self.db.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            return cursor.fetchone() is not None

    def create_chat_interface(self, username):
        self.chat_window = tk.Toplevel(self.root)
        self.chat_window.title("Chatbot")
        self.chat_window.configure(bg='#2c3e50')

        self.chat_display = scrolledtext.ScrolledText(self.chat_window, state='disabled', width=50, height=20, wrap='word', font=('Arial', 12), bg='#34495e', fg='white', relief='flat')
        self.chat_display.pack(padx=10, pady=10)

        self.entry_frame = tk.Frame(self.chat_window, bg='#2c3e50')
        self.entry_frame.pack(padx=10, pady=10)

        self.user_entry = tk.Entry(self.entry_frame, width=40, font=('Arial', 12), bg='#ecf0f1', relief='flat')
        self.user_entry.pack(side=tk.LEFT, padx=(0, 5))

        self.send_button = tk.Button(self.entry_frame, text="Send", command=self.process_user_input, bg='#3498db', fg='white', font=('Arial', 12), relief='flat')
        self.send_button.pack(side=tk.LEFT)

        self.chat_display.configure(state='normal')
        self.chat_display.insert(tk.END, f"Chatbot: {self.get_greeting()} Type 'bye' to exit.\n")
        self.chat_display.configure(state='disabled')

    def process_user_input(self):
        user_input = self.user_entry.get().strip()
        if user_input:
            self.chat_display.configure(state='normal')
            self.chat_display.insert(tk.END, f"You: {user_input}\n", 'user')
            self.user_entry.delete(0, tk.END)

            if user_input.lower() in ["bye", "goodbye"]:
                self.chat_display.insert(tk.END, "Chatbot: Goodbye! Have a nice day!\n", 'chatbot')
                self.chat_display.configure(state='disabled')
                self.chat_window.after(2000, self.chat_window.destroy)
                return

            response = self.get_response(user_input)
            translated_response = self.translate_text(response, dest_language='en')  # Translate response if needed
            self.chat_display.insert(tk.END, f"Chatbot: {translated_response}\n", 'chatbot')
            self.chat_display.configure(state='disabled')
            self.chat_display.yview(tk.END)

if __name__ == "__main__":
    bot = ChatBot()
    bot.run()
