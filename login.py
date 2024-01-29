import tkinter as tk
from datetime import datetime
from tkinter import messagebox
import time
import mysql.connector

# Initialize mysql
def connect_to_mysql():
    try:
        # Replace these with your MySQL server details
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="records"
        )
        return connection
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error: {err}")
        return None

def authenticate_user(student_id, password):
    connection = connect_to_mysql()
    if not connection:
        return False
    
    cursor = connection.cursor()

    query = "SELECT * FROM students WHERE studentid = %s AND password = %s"
    cursor.execute(query, (student_id, password))
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result is not None

def login():
    student_id = student_id_entry.get()
    password = password_entry.get()

    global current_session
    if authenticate_user(student_id, password):
        connection = connect_to_mysql()
        if connection:
            cursor = connection.cursor()

            login_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            insert_query = "INSERT INTO login_sessions (studentid, login_time) VALUES (%s, %s)"
            cursor.execute(insert_query, (student_id, login_time))

            connection.commit()

            # Store current session information
            current_session = {"student_id": student_id, "login_time": login_time}

            login_window.destroy()
            main_window(student_id, login_time)
    
    else:
        error_label.config(text="Invalid credentials", fg="red")

def on_logout(window, student_id, login_time):
    logout_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    connection = connect_to_mysql()
    if connection:
        cursor = connection.cursor()

        update_query = "UPDATE login_sessions SET logout_time = %s WHERE studentid = %s AND login_time = %s"
        cursor.execute(update_query, (logout_time, student_id, login_time))

        update_time = "UPDATE login_sessions SET consumed_time = TIMESTAMPDIFF(MINUTE, login_time, logout_time) WHERE studentid = %s AND login_time = %s"
        cursor.execute(update_time, (student_id, login_time))
        #time left
        update_timeleft = "UPDATE students SET time_left = time_left - (SELECT consumed_time FROM login_sessions WHERE students.studentid = login_sessions.studentid ORDER BY login_time DESC LIMIT 1) WHERE EXISTS (SELECT 1 FROM login_sessions WHERE students.studentid = login_sessions.studentid);"
        cursor.execute(update_timeleft)
        #consumed time
        # update_time = "UPDATE login_sessions SET consumed_time = TIMESTAMPDIFF(MINUTE, login_time, logout_time), time_left = time_left - TIMESTAMPDIFF(MINUTE, login_time, logout_time) WHERE studentid = %s AND login_time = %s"
        # cursor.execute(update_time, (student_id, login_time))

        connection.commit()
        cursor.close()
        connection.close()

        window.destroy()  # Corrected to use main_window window object 
        # login_window.deiconify()

def main_window(student_id, login_time):
    global start_time
    start_time = time.time()

    window = tk.Tk()  # Changed variable name to window
    window.title("Logged In")
    window.geometry("300x150")

    # Display current time at login
    current_time = datetime.now().strftime("%H:%M:%S %p")
    logged_in_label = tk.Label(window, text=f"Logged In: {current_time}")
    logged_in_label.pack()

    time_label = tk.Label(window, text="Running Time: 00:00:00")
    time_label.pack()

    def update_time():
        elapsed_time = time.time() - start_time
        running_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        time_label.config(text=f"Running Time: {running_time}")
        window.after(1000, update_time)  # Update every second

    update_time()

    logout_button = tk.Button(window, text="Logout", command=lambda: on_logout(window, student_id, login_time))
    logout_button.pack()

    window.mainloop()

# Login window
login_window = tk.Tk()
login_window.attributes("-fullscreen", True)

# WIDGETS
student_id_label = tk.Label(login_window, text="Student ID:")
student_id_label.pack(side=tk.TOP, pady=10)

student_id_entry = tk.Entry(login_window)
student_id_entry.pack(side=tk.TOP, pady=5)

password_label = tk.Label(login_window, text="Password:")
password_label.pack(side=tk.TOP, pady=10)

password_entry = tk.Entry(login_window, show="*")
password_entry.pack(side=tk.TOP, pady=5)

login_button = tk.Button(login_window, text="Login", command=login)
login_button.pack(side=tk.TOP, pady=20)

error_label = tk.Label(login_window, text="")
error_label.pack(side=tk.TOP, pady=10)

# Center the widgets in the window
for widget in login_window.winfo_children():
    widget.pack_configure(anchor='n')

# WIDGETS ^^
login_window.mainloop()
