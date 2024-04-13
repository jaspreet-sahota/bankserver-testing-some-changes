import server
import tkinter as tk
from tkinter import messagebox
import datetime


def deposit(username, amount, log_text):
    try:
        amount = float(amount)
        if amount <= 0:
            messagebox.showerror("Error", "Please enter a positive amount.")
        else:
            server.accounts[username]['balance'] += amount
            messagebox.showinfo("Deposit",
                                f"Successfully deposited ${amount}. New balance: ${server.accounts[username]['balance']}")
            log_text.insert(tk.END,
                            f"User {username} deposited ${amount}. New balance: ${server.accounts[username]['balance']}. {get_current_datetime()}\n")
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid amount.")


def withdraw(username, amount, log_text):
    try:
        amount = float(amount)
        if amount <= 0:
            messagebox.showerror("Error", "Please enter a positive amount.")
        else:
            if username in server.accounts:
                if server.accounts[username]['balance'] >= amount:
                    server.accounts[username]['balance'] -= amount
                    messagebox.showinfo("Withdraw",
                                        f"Successfully withdrew ${amount}. New balance: ${server.accounts[username]['balance']}")
                    log_text.insert(tk.END,
                                    f"User {username} withdrew ${amount}. New balance: ${server.accounts[username]['balance']}. {get_current_datetime()}\n")
                else:
                    messagebox.showerror("Error", "Insufficient balance.")
            else:
                messagebox.showerror("Error", "User not found.")
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid amount.")


def check_balance(username, log_text):
    if username in server.accounts:
        balance = server.accounts[username]['balance']
        messagebox.showinfo("Balance", f"Your balance: {balance}")
        log_text.insert(tk.END,
                        f"User {username} checked their balance. Balance: ${balance}. {get_current_datetime()}\n")
    else:
        messagebox.showerror("Error", "User not found.")


def get_current_datetime():
    return datetime.now().strftime("%m/%d/%y @ %H:%M:%S")
