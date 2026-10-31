import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mysql.connector
from PIL import Image, ImageTk

# MySQL Database Connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Ashish@123",
    database="blood_bank"
)

cursor = conn.cursor()

print("Database connected successfully!")
# Sample data structure to store blood bank data
blood_data = {
    'A+': 10,
    'A-': 5,
    'B+': 8,
    'B-': 3,
    'O+': 15,
    'O-': 2,
    'AB+': 6,
    'AB-': 1
}



# Add donor information
# Add donor information
def add_donor():

    name = name_entry.get().strip()
    blood_group = blood_group_combobox.get()
    age = age_entry.get().strip()
    contact = contact_entry.get().strip()

    # Check empty fields
    if not (name and blood_group and age and contact):
        messagebox.showerror(
            "Input Error",
            "Please fill all fields!"
        )
        return

    # Validate age
    try:
        age = int(age)

        if age <= 0:
            raise ValueError

    except ValueError:
        messagebox.showerror(
            "Input Error",
            "Please enter a valid age!"
        )
        return

    try:
        # Check duplicate using Name, Age and Phone Number
        cursor.execute(
            """
            SELECT donor_id FROM donors
            WHERE LOWER(TRIM(name)) = LOWER(TRIM(%s))
            AND age = %s
            AND contact = %s
            """,
            (name, age, contact)
        )

        existing_donor = cursor.fetchone()

        # If donor already exists
        if existing_donor:
            messagebox.showwarning(
                "Duplicate Donor",
                "Donor already registered!"
            )
            return

        # Save donor details in MySQL
        sql = """
        INSERT INTO donors (name, blood_group, age, contact)
        VALUES (%s, %s, %s, %s)
        """

        values = (name, blood_group, age, contact)

        cursor.execute(sql, values)
        conn.commit()

        # Update blood availability chart
        blood_data[blood_group] += 1
        update_chart()

        messagebox.showinfo(
            "Success",
            "Donor added successfully!"
        )

        # Clear input fields
        clear_fields()

    except mysql.connector.Error as error:
        messagebox.showerror(
            "Database Error",
            str(error)
        )
# Clear input fields
def clear_fields():
    name_entry.delete(0, tk.END)
    age_entry.delete(0, tk.END)
    contact_entry.delete(0, tk.END)
    blood_group_combobox.set('')

# Display donors
# Display, Edit and Delete Donors
def view_donors():

    donor_window = tk.Toplevel(root)
    donor_window.title("Donor Management")
    donor_window.geometry("900x500")
    donor_window.configure(bg="#F0F0F0")

    tk.Label(
        donor_window,
        text="DONOR MANAGEMENT",
        font=("Arial", 18, "bold"),
        fg="#B22222",
        bg="#F0F0F0"
    ).pack(pady=15)

    # Create donor table
    columns = ("Name", "Blood Group", "Age", "Contact")

    tree = ttk.Treeview(
        donor_window,
        columns=columns,
        show="headings",
        height=12
    )

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=180, anchor="center")

    tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    # Load donor records from MySQL
    def refresh_donors():
        for item in tree.get_children():
            tree.delete(item)

        try:
            cursor.execute(
                "SELECT donor_id, name, blood_group, age, contact FROM donors"
            )

            records = cursor.fetchall()

            for donor in records:
                donor_id, name, blood_group, age, contact = donor

                # Store donor_id as the Treeview item ID
                tree.insert(
                    "",
                    tk.END,
                    iid=str(donor_id),
                    values=(name, blood_group, age, contact)
                )

        except mysql.connector.Error as error:
            messagebox.showerror("Database Error", str(error))

    # Edit selected donor
    def edit_donor():

        selected = tree.selection()

        if not selected:
            messagebox.showwarning(
                "Selection Required",
                "Please select a donor to edit!"
            )
            return

        donor_id = selected[0]
        values = tree.item(donor_id, "values")

        edit_window = tk.Toplevel(donor_window)
        edit_window.title("Edit Donor")
        edit_window.geometry("400x400")
        edit_window.configure(bg="#F5F5F5")
        edit_window.resizable(False, False)

        tk.Label(
            edit_window,
            text="EDIT DONOR DETAILS",
            font=("Arial", 16, "bold"),
            fg="#B22222",
            bg="#F5F5F5"
        ).pack(pady=15)

        # Name
        tk.Label(edit_window, text="Name:", bg="#F5F5F5").pack()
        name_edit = tk.Entry(edit_window, width=30)
        name_edit.pack(pady=5)
        name_edit.insert(0, values[0])

        # Blood Group
        tk.Label(edit_window, text="Blood Group:", bg="#F5F5F5").pack()
        blood_edit = ttk.Combobox(
            edit_window,
            values=list(blood_data.keys()),
            width=27,
            state="readonly"
        )
        blood_edit.pack(pady=5)
        blood_edit.set(values[1])

        # Age
        tk.Label(edit_window, text="Age:", bg="#F5F5F5").pack()
        age_edit = tk.Entry(edit_window, width=30)
        age_edit.pack(pady=5)
        age_edit.insert(0, values[2])

        # Contact
        tk.Label(edit_window, text="Contact:", bg="#F5F5F5").pack()
        contact_edit = tk.Entry(edit_window, width=30)
        contact_edit.pack(pady=5)
        contact_edit.insert(0, values[3])

        # Save updated details
        def save_changes():

            name = name_edit.get().strip()
            blood_group = blood_edit.get()
            age = age_edit.get().strip()
            contact = contact_edit.get().strip()

            if not (name and blood_group and age and contact):
                messagebox.showerror(
                    "Input Error",
                    "Please fill all fields!",
                    parent=edit_window
                )
                return

            try:
                age = int(age)

                if age <= 0:
                    raise ValueError

            except ValueError:
                messagebox.showerror(
                    "Input Error",
                    "Please enter a valid age!",
                    parent=edit_window
                )
                return

            try:
                cursor.execute(
                    """
                    UPDATE donors
                    SET name=%s, blood_group=%s, age=%s, contact=%s
                    WHERE donor_id=%s
                    """,
                    (name, blood_group, age, contact, donor_id)
                )

                conn.commit()

                messagebox.showinfo(
                    "Success",
                    "Donor details updated successfully!",
                    parent=edit_window
                )

                edit_window.destroy()
                refresh_donors()

            except mysql.connector.Error as error:
                messagebox.showerror(
                    "Database Error",
                    str(error),
                    parent=edit_window
                )

        tk.Button(
            edit_window,
            text="SAVE CHANGES",
            command=save_changes,
            bg="#228B22",
            fg="white",
            font=("Arial", 11, "bold")
        ).pack(pady=20)

    # Delete selected donor
    def delete_donor():

        selected = tree.selection()

        if not selected:
            messagebox.showwarning(
                "Selection Required",
                "Please select a donor to delete!"
            )
            return

        donor_id = selected[0]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this donor?"
        )

        if confirm:
            try:
                cursor.execute(
                    "DELETE FROM donors WHERE donor_id=%s",
                    (donor_id,)
                )

                conn.commit()

                messagebox.showinfo(
                    "Success",
                    "Donor deleted successfully!"
                )

                refresh_donors()

            except mysql.connector.Error as error:
                messagebox.showerror("Database Error", str(error))

    # Buttons
    button_frame = tk.Frame(donor_window, bg="#F0F0F0")
    button_frame.pack(pady=15)

    tk.Button(
        button_frame,
        text="EDIT DONOR",
        command=edit_donor,
        bg="#228B22",
        fg="white",
        font=("Arial", 11, "bold"),
        width=15
    ).grid(row=0, column=0, padx=10)

    tk.Button(
        button_frame,
        text="DELETE DONOR",
        command=delete_donor,
        bg="#B22222",
        fg="white",
        font=("Arial", 11, "bold"),
        width=15
    ).grid(row=0, column=1, padx=10)

    tk.Button(
        button_frame,
        text="REFRESH",
        command=refresh_donors,
        bg="#4682B4",
        fg="white",
        font=("Arial", 11, "bold"),
        width=15
    ).grid(row=0, column=2, padx=10)

    # Show database records when window opens
    refresh_donors()
# Update chart
# Update chart with transparent background
def update_chart():

    blood_groups = list(blood_data.keys())
    quantities = list(blood_data.values())

    # Make chart and figure backgrounds transparent
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")

    ax.clear()

    # Keep axes background transparent after clearing
    ax.set_facecolor("none")

    bars = ax.bar(
        blood_groups,
        quantities,
        color=[
            '#FF9999', '#FFCC99', '#99CCFF', '#CCFF99',
            '#FF6666', '#6666FF', '#66FF66', '#FFFF66'
        ]
    )

    ax.set_title(
        "Blood Group Availability",
        fontsize=14,
        fontweight='bold',
        color="black"
    )

    ax.set_xlabel("Blood Groups", fontsize=12, fontweight='bold')
    ax.set_ylabel("Units Available", fontsize=12, fontweight='bold')

    ax.tick_params(axis='x', labelsize=10, colors="black")
    ax.tick_params(axis='y', labelsize=10, colors="black")

    # Make graph borders transparent
    for spine in ax.spines.values():
        spine.set_alpha(0)

    # Remove white graph box
    ax.patch.set_alpha(0)

    # Display values on bars
    for bar, qty in zip(bars, quantities):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            str(qty),
            ha='center',
            va='bottom',
            fontsize=10,
            color='black',
            fontweight='bold'
        )

    canvas.draw()
# Admin Login Function
def login():
    username = username_entry.get()
    password = password_entry.get()

    if not username or not password:
        messagebox.showerror("Error", "Please enter username and password!")
        return

    try:
        cursor.execute(
            """
            SELECT * FROM admin_users
            WHERE username = %s
            AND password_hash = SHA2(%s, 256)
            """,
            (username, password)
        )

        result = cursor.fetchone()

        if result:
            messagebox.showinfo("Success", "Login successful!")
            login_window.destroy()
            root.deiconify()
        else:
            messagebox.showerror(
                "Login Failed",
                "Invalid username or password!"
            )

    except mysql.connector.Error as error:
        messagebox.showerror("Database Error", str(error))
# Main application window
root = tk.Tk()
root.title("Blood Bank Management System")
root.state("zoomed")
root.withdraw()

# Load dashboard background image
root.update_idletasks()

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

dashboard_image = Image.open("image.jpg")
dashboard_image = dashboard_image.resize(
    (screen_width, screen_height),
    Image.Resampling.LANCZOS
)

dashboard_photo = ImageTk.PhotoImage(dashboard_image)

# Display image behind dashboard
dashboard_bg = tk.Label(root, image=dashboard_photo)
dashboard_bg.image = dashboard_photo
dashboard_bg.place(x=0, y=0, relwidth=1, relheight=1)
# Input fields
frame = tk.Frame(root, bg="#FFFFFF", bd=0)
frame.pack(pady=20)

tk.Label(frame, text="Name:", font=("Arial", 12, "bold"), bg="#FFFFFF").grid(row=0, column=0, padx=10, pady=10)
name_entry = tk.Entry(frame, font=("Arial", 12))
name_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(frame, text="Blood Group:", font=("Arial", 12, "bold"), bg="#FFFFFF").grid(row=1, column=0, padx=10, pady=10)
blood_group_combobox = ttk.Combobox(frame, values=list(blood_data.keys()), font=("Arial", 12))
blood_group_combobox.grid(row=1, column=1, padx=10, pady=10)

tk.Label(frame, text="Age:", font=("Arial", 12, "bold"), bg="#FFFFFF").grid(row=2, column=0, padx=10, pady=10)
age_entry = tk.Entry(frame, font=("Arial", 12))
age_entry.grid(row=2, column=1, padx=10, pady=10)

tk.Label(frame, text="Contact:", font=("Arial", 12, "bold"), bg="#FFFFFF").grid(row=3, column=0, padx=10, pady=10)
contact_entry = tk.Entry(frame, font=("Arial", 12))
contact_entry.grid(row=3, column=1, padx=10, pady=10)

# Buttons
tk.Button(frame, text="Add Donor", command=add_donor, font=("Arial", 12, "bold"), bg='#66CC66', fg='white').grid(row=4, column=0, padx=10, pady=20)
tk.Button(frame, text="View Donors", command=view_donors, font=("Arial", 12, "bold"), bg='#6699CC', fg='white').grid(row=4, column=1, padx=10, pady=20)

# Matplotlib chartp
# Create transparent blood availability chart
fig, ax = plt.subplots(figsize=(6, 5))

# Make graph and figure backgrounds transparent
fig.patch.set_alpha(0)
ax.patch.set_alpha(0)

# Keep graph labels visible
ax.set_facecolor("none")

canvas = FigureCanvasTkAgg(fig, root)

# Make the chart widget background match the main window
canvas.get_tk_widget().configure(bg="#F0F0F0", highlightthickness=0)

canvas.get_tk_widget().pack(pady=20)

update_chart()
# Login Window

# Login Window with Background Image

login_window = tk.Toplevel(root)
login_window.title("Blood Bank Management System")
login_window.state("zoomed")
login_window.resizable(False, False)

# Get screen dimensions
login_window.update_idletasks()
screen_width = login_window.winfo_screenwidth()
screen_height = login_window.winfo_screenheight()

# Load and resize background image
bg_image = Image.open("login_bg.jpg")
bg_image = bg_image.resize(
    (screen_width, screen_height),
    Image.Resampling.LANCZOS
)

background_photo = ImageTk.PhotoImage(bg_image)

# Display background image
background_label = tk.Label(
    login_window,
    image=background_photo
)
background_label.image = background_photo
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# Login heading
tk.Label(
    login_window,
    text="BLOOD BANK MANAGEMENT",
    font=("Arial", 30, "bold"),
    bg="#F4F4F4",
    fg="#B22222"
).place(relx=0.5, rely=0.17, anchor="center")

tk.Label(
    login_window,
    text="Admin Login",
    font=("Arial", 24, "bold"),
    bg="#F4F4F4",
    fg="#14212B"
).place(relx=0.5, rely=0.28, anchor="center")

# Username
tk.Label(
    login_window,
    text="Username",
    font=("Arial", 13),
    bg="#F4F4F4",
    fg="#333333"
).place(relx=0.5, rely=0.37, anchor="center")

username_entry = tk.Entry(
    login_window,
    font=("Arial", 16),
    width=30
)
username_entry.place(relx=0.5, rely=0.42, anchor="center", height=45)

# Password
tk.Label(
    login_window,
    text="Password",
    font=("Arial", 13),
    bg="#F4F4F4",
    fg="#333333"
).place(relx=0.5, rely=0.49, anchor="center")

password_entry = tk.Entry(
    login_window,
    font=("Arial", 16),
    width=30,
    show="*"
)
password_entry.place(relx=0.5, rely=0.54, anchor="center", height=45)

# Login button
tk.Button(
    login_window,
    text="LOGIN",
    command=login,
    font=("Arial", 16, "bold"),
    bg="#B22222",
    fg="white",
    activebackground="#8B0000",
    activeforeground="white",
    width=22,
    height=2,
    cursor="hand2"
).place(relx=0.5, rely=0.64, anchor="center")

tk.Label(
    login_window,
    text="Only Authorized Personnel",
    font=("Arial", 12),
    bg="white",
    fg="#555555"
).place(relx=0.5, rely=0.73, anchor="center")

# Start application
root.mainloop()


