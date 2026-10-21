import sqlite3
import datetime
import tkinter as tk
from tkinter import messagebox, ttk

DB_NAME = "smart_campus_box.db"
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("""CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT UNIQUE NOT NULL,password TEXT NOT NULL,role TEXT NOT NULL CHECK (role IN("Lecturer","Campus Administrator","System Operator")));""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS campuses (campus_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL, policy_type TEXT NOT NULL);""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS resources(resource_id TEXT PRIMARY KEY, campus_id INTEGER NOT NULL, name TEXT NOT NULL, type TEXT NOT NULL, FOREIGN KEY (campus_id) REFERENCES campuses (campus_id) ON DELETE CASCADE);""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS bookings(booking_id INTEGER PRIMARY KEY AUTOINCREMENT,resource_id TEXT NOT NULL, user_id INTEGER NOT NULL, DATE TEXT NOT NULL, start_time TEXT NOT NULL, duration INTEGER NOT NULL,FOREIGN KEY (resource_id) REFERENCES resources(resource_id) ON DELETE CASCADE,FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE);""")
        cursor.execute("SELECT COUNT(*) FROM campuses;")
        row = cursor.fetchone()
        if row and row [0] == 0:
            cursor.executemany("INSERT INTO campuses (name, policy_type) VALUES (?, ?);",[("Johannesburg","Max2Hours"),("Pretoria","BusinessHoursOnly"),("Durban","Standard")])
            cursor.executemany("INSERT INTO users (username, password, role) VALUES (?, ?, ?);",[("lecturer1","pass123","Lecturer"),("admin1","admin123","Campus Administrator"),("operator1","op123","System Operator")])
            cursor.executemany("INSERT INTO resources (resource_id, campus_id, name, type) VALUES (?,?,?,?);",[("JHB-LAB1", 1, "Computer Laboratory 1", "Laboratory"),("JHB-PROJ1", 1, "Multimedia Projector A","Equipment"),("PRY-SEM1", 2, "Seminar Room 101","Room"),("DBN-LAB2", 3, "Computer Laboratory 2", "Laboratory")])
        conn.commit()
class User:
    def __init__(self, user_id, username, role):
        self.__user_id = user_id
        self.__username = username
        self.role = role
    def get_id(self):
        return self.__user_id
    def get_username(self):
        return self.__username
class Lecturer(User):
    def __init__(self, user_id, username):
        super().__init__(user_id, username, "Lecturer")
class CampusAdministrator(User):
    def __init__(self, user_id, username):
        super().__init__(user_id, username, "Campus Administrator")
class SystemOperator(User):
    def __init__(self, user_id, username):
        super().__init__(user_id, username, "System Operator")
class BookingPolicyEngine:
    @staticmethod
    def validate(policy_type, start_time_str, duration):
        try:
            hour = int(start_time_str.split(":")[0])
        except (ValueError, IndexError):
            return False, "Invalid time format. Please apply standard HH:MM format parameters."
        if policy_type == "Max2Hours":
            if duration > 2:
                return False, "Johannesburg Rule Violation: Maximum allowed booking duration is 2 hours."
        elif policy_type == "BusinessHoursOnly":
            if hour < 8 or hour >=17:
                return False, "Pretoria Rule Violation: Bookings must stay within business hours (08:00 - 17:00)."
        return True, "Valid"
class SmartCampusApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Richfield Smart Campus Resource Booking System")
        self.root.geometry("950x650")
        self.current_user = None
        self.active_campus_id = None
        self.active_campus_name = ""
        self.active_policy = ""
        self.ent_username = None
        self.ent_password = None
        self.campus_combobox = None
        self.notebook = None
        self.tree_resources = None
        self.tree_history = None
        self.ent_date = None
        self.ent_time = None
        self.ent_duration = None
        self.ent_res_id = None
        self.ent_res_name = None
        self.cb_res_type = None
        self.tree_admin_resources = None
        self.tree_admin_bookings = None
        self.tree_operator_reports = None
        self.ent_admin_res_id = None
        self.ent_admin_res_name = None
        self.cb_admin_res_type = None
        self.show_login_frame()
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    def show_login_frame(self):
        self.clear_window()
        frame = ttk.Frame(self.root, padding = "30")
        frame.place(relx = 0.5, rely = 0.5, anchor = "center")
        ttk.Label(frame, text = "Richfield Campus Sign-In", font = ("Arial", 16, "bold")).grid(row = 0, column = 0, columnspan = 2, pady = 15)
        ttk.Label(frame, text = "Username:").grid(row = 1, column = 0, sticky = tk.W, pady = 5)
        self.ent_username = ttk.Entry(frame, width = 30)
        self.ent_username.grid(row = 1, column = 1, pady = 5)
        ttk.Label(frame, text="Password:").grid(row = 2, column = 0, sticky = tk.W, pady = 5)
        self.ent_password = ttk.Entry(frame, show = "*", width = 30)
        self.ent_password.grid(row = 2, column = 1, pady = 5)
        btn_login = ttk.Button(frame, text = "Login", command = self.handle_login)
        btn_login.grid(row = 3, column = 0, columnspan = 2, pady = 20, sticky = tk.EW)
    def handle_login(self):
        username = self.ent_username.get().strip()
        password = self.ent_password.get().strip()
        if not username or not password:
            messagebox.showerror("Validation Error","All field entries must be populated.")
            return
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, username, role FROM users WHERE username = ? AND password = ?", (username, password))
        row = cursor.fetchone()
        conn.close()
        if row:
            u_id, u_name, u_role = row
            if u_role == "Lecturer":
                self.current_user = Lecturer (u_id, u_name)
            elif u_role == "Campus Administrator":
                self.current_user = CampusAdministrator(u_id, u_name)
            else: self.current_user = SystemOperator(u_id, u_name)
            self.show_campus_selection()
        else:
            messagebox.showerror("Authentication Failed", "Invalid credentials provided.")
    def show_campus_selection(self):
        self.clear_window()
        frame = ttk.Frame(self.root, padding = "30")
        frame.place(relx = 0.5, rely = 0.5, anchor = "center")
        ttk.Label(frame, text = f"Welkom, {self.current_user.get_username()}!", font=("Arial", 14, "bold")).grid(row = 0, column = 0, pady = 10)
        ttk.Label(frame, text = "Select operational workspace campus context:").grid(row = 1, column = 0, pady = 5)
        self.campus_combobox = ttk.Combobox(frame, state = "readonly", width = 25)
        self.campus_combobox.grid(row = 2, column = 0, pady = 10)
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM campuses")
        campuses = [r[0] for r in cursor.fetchall()]
        conn.close()
        self.campus_combobox["values"] = campuses
        self.campus_combobox.current(0)
        btn_select = ttk.Button(frame, text="Initialize Workspace Dashboard",command = self.load_dashboard)
        btn_select.grid(row = 3, column = 0, pady = 15, sticky = tk.EW)
    def load_dashboard(self):
         selected_campus = self.campus_combobox.get()
         conn = sqlite3.connect(DB_NAME)
         cursor = conn.cursor()
         cursor.execute("SELECT campus_id, name, policy_type FROM campuses WHERE name=?", (selected_campus,))
         self.active_campus_id, self.active_campus_name, self.active_policy = cursor.fetchone()
         conn.close()
         self.show_main_dashboard()
    def show_main_dashboard(self):
        self.clear_window()
        status_frame = ttk.Frame(self.root, padding = "10", relief = "groove")
        status_frame.pack(fill = "x", side = "top")
        ttk.Label(status_frame, text = f"Identity: {self.current_user.get_username()}[{self.current_user.role}]", font = ("Arial", 10, "bold")).pack(side = "left",padx = 15)
        ttk.Label(status_frame, text = f"Campus Scope: {self.active_campus_name}", font = ("Arial",10)).pack(side = "left",padx = 15)
        ttk.Label(status_frame, text = f"Active Rule Constraints: {self.active_policy}",font = ("Arial", 10, "italic"), foreground = "crimson").pack(side = "left", padx = 15)
        btn_logout = ttk.Button(status_frame, text = "Sign Out", command = self.show_login_frame)
        btn_logout.pack(side = "right", padx = 15)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill = "both", expand = True, padx = 10, pady = 10)
        if self.current_user.role == "Lecturer":
            self.build_lecturer_tabs()
        elif self.current_user.role == "Campus Administrator":
            self.build_admin_tabs()
        elif self.current_user.role == "System Operator":
            self.build_operator_tabs()
    def build_lecturer_tabs(self):
        tab_booking = ttk.Frame(self.notebook)
        tab_history = ttk.Frame(self.notebook)
        self.notebook.add(tab_booking, text = "New Booking Request")
        self.notebook.add(tab_history, text = "Track My Bookings")
        left_pane = ttk.LabelFrame(tab_booking, text = "Live Resource Catalog Inventory", padding = "10")
        left_pane.pack(side = "left", fill = "both", expand = True, padx = 5, pady = 5)
        self.tree_resources = ttk.Treeview(left_pane,columns = ("ID", "Name","Type"), show = "headings")
        self.tree_resources.heading("ID", text = "Resource ID")
        self.tree_resources.heading("Name", text = "Resource Name")
        self.tree_resources.heading("Type", text = "Type")
        self.tree_resources.pack(fill = "both", expand = True)
        self.update_resource_tree()
        right_pane = ttk.LabelFrame(tab_booking, text = "Schedule Parameter Entry From", padding = "10")
        right_pane.pack(side = "right", fill = "y", padx = 5, pady = 5)
        ttk.Label(right_pane, text = "Date (YYYY-MM-DD):").pack(anchor = "w", pady = 2)
        self.ent_date = ttk.Entry(right_pane, width = 20)
        self.ent_date.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        self.ent_date.pack(fill = "x", pady = 2)
        ttk.Label(right_pane, text = "Start Time (HH:MM):").pack(anchor = "w", pady = 2)
        self.ent_time = ttk.Entry(right_pane, width = 20)
        self.ent_time.insert(0, "08:00")
        self.ent_time.pack(fill = "x", pady = 2)
        ttk.Label(right_pane, text = "Duration (Hours)").pack(anchor = "w", pady = 2)
        self.ent_duration = ttk.Entry(right_pane, width = 20)
        self.ent_duration.insert(0, "1")
        self.ent_duration.pack(fill = "x", pady = 2)
        btn_submit_booking = ttk.Button(right_pane, text = "commit Resource Booking", command = self.handle_create_booking)
        btn_submit_booking.pack(fill = "x", pady = 15)
        self.tree_history = ttk.Treeview(tab_history, columns = ("B_ID","R_ID","R_Name","Date","Time","Duration"), show = "headings")
        self.tree_history.heading("B_ID", text = "Booking ID")
        self.tree_history.heading("R_ID", text = "Resource ID")
        self.tree_history.heading("R_Name", text = "Resource ID")
        self.tree_history.heading("Date", text = "Date")
        self.tree_history.heading("Time", text = "Date")
        self.tree_history.heading("Duration", text = "Duration (Hrs)")
        self.tree_history.pack(fill = "both", expand = True, padx = 10, pady = 10)
        btn_cancel_booking = ttk.Button(tab_history, text = "Cancel Selected Reservation", command = self.handle_cancel_booking)
        btn_cancel_booking.pack(pady = 5)
        self.update_history_tree()
    def update_resource_tree(self):
        for item in self.tree_resources.get_children():
            self.tree_resources.delete(item)
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT resource_id, name, type FROM resources WHERE campus_id = ?", (self.active_campus_id,))
        for row in cursor.fetchall():
            self.tree_resources.insert("", "end", values = row)
        conn.close()
    def update_history_tree(self):
        for item in self.tree_history.get_children():
            self.tree_history.delete(item)
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT b.booking_id, b.resource_id, r.name, b.date, b.start_time, b.duration FROM bookings b JOIN resources r ON b.resource_id = r.resource_id Where b.user_id = ? AND r.campus_id = ?""", (self.current_user.get_id(), self.active_campus_id))
        for row in cursor.fetchall():
            self.tree_history.insert("", "end", values = row)
    def handle_create_booking(self):
        selected = self.tree_resources.selection()
        if not selected:
            messagebox.showerror("Selection Error", "Please select a target resource asset from the catalog list.")
            return
        res_values = self.tree_resources.item(selected)["values"]
        res_id = res_values[0]
        date_str = self.ent_date.get().strip()
        time_str = self.ent_time.get().strip()
        duration_str = self.ent_duration.get().strip()
        if not date_str or not time_str or not duration_str:
            messagebox.showerror("Input Error", "All scheduling configurations must be filled out.")
            return
        try:
            duration = int(duration_str)
            if duration <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Type Error","Duration matrix values must evaluate to a value positive integer.")
            return
        is_valid, policy_msg = BookingPolicyEngine.validate(self.active_policy, time_str, duration)
        if not is_valid:
            messagebox.showerror("Policy Infringement Violation", policy_msg)
            return
        try:
            start_hour = int(time_str.split(":")[0])
            start_min = int(time_str.split(":")[1])
            new_start = start_hour + (start_min / 60.0)
            new_end = new_start + duration
        except (ValueError, AttributeError, IndexError):
            messagebox.showerror("Format Error","Time conversion metrics failed. Use structured HH:MM format.")
            return
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT start_time, duration FROM bookings WHERE resource_id = ? And date = ?", (res_id, date_str))
            existing_booking = cursor.fetchall()
            for ex_time, ex_dur in existing_booking:
                try:
                    ex_h, ex_m = map(int, ex_time.split(":"))
                    ex_start = ex_h + (ex_m / 60.0)
                    ex_end = ex_start + ex_dur
                    if not (new_end <= ex_start or new_start >= ex_end):
                        messagebox.showerror("Double booking Collision Detected","Resources Conflict: The chosen asset is already locked during this time.")
                        return
                except Exception:
                    continue
            cursor.execute("INSERT INTO bookings (resource_id, user_id, date, start_time, duration) VALUES (?,?,?,?,?)",
                       (res_id, self.current_user.get_id(), date_str, time_str, duration))
            conn.commit()
        messagebox.showinfo("Success","Campus resource scheduling transaction confirmed.")
        self.update_history_tree()
    def handle_cancel_booking(self):
        selected = self.tree_history.selection()
        if not selected:
            messagebox.showerror("Selection Error", "Please highlight the targeting reservation slot first.")
            return
        booking_values = self.tree_history.item(selected)["values"]
        booking_id = booking_values[0]
        if messagebox.askyesno("Confirm Action", "Do you wish to drop and revoke this booing allocation?"):
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM bookings WHERE booking_id = ?", (booking_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Transaction complete","the reserved calendar allocation has been completely dropped")
            self.update_history_tree()
    def build_admin_tabs(self):
        tab_manage = ttk.Frame(self.notebook)
        self.notebook.add(tab_manage, text = "Manage Campus Resources")
        left_pane = ttk.LabelFrame(tab_manage, text = "Manage Campus Resources")
        left_pane.pack(side = "left", fill = "both", expand = True, padx = 5, pady = 5)
        self.tree_admin_resources = ttk.Treeview(left_pane, columns = ("ID", "Name","Type"), show = "headings")
        self.tree_admin_resources.heading("ID", text = "Resources ID")
        self.tree_admin_resources.heading("Name", text = "Resource Name")
        self.tree_admin_resources.heading("Type", text = "Type")
        self.tree_admin_resources.pack(fill = "both", expand = True)
        self.tree_admin_resources.bind("<<TreeviewSelect>>", self.populate_admin_fields)
        right_pane = ttk.LabelFrame(tab_manage, text = "Asset Parameters Management From", padding = "10")
        right_pane.pack(side = "right", fill = "y", padx = 5, pady = 5)
        ttk.Label(right_pane, text = "Resource ID (Unique):").pack(anchor = "w", pady = 2)
        self.ent_admin_res_id = ttk.Entry(right_pane, width = 25)
        self.ent_admin_res_id.pack(fill = "x", pady = 2)
        self.ent_admin_res_id.pack(fill = "x", pady = 2)
        ttk.Label(right_pane, text = "Resource Name:").pack(anchor = "w", pady = 2)
        self.ent_admin_res_name = ttk.Entry(right_pane, width = 25)
        self.ent_admin_res_name.pack(fill = "x", pady = 2)
        ttk.Label(right_pane, text = "Resource Type:").pack(anchor = "w", pady = 2)
        self.cb_admin_res_type = ttk.Combobox(right_pane, values = ["Laboratory", "Equipment", "Room"], state = "readonly")
        self.cb_admin_res_type.pack(fill = "x", pady = 2)
        self.cb_admin_res_type.current(0)
        btn_add = ttk.Button(right_pane, text = "Add New Resource Asset", command = self.handle_admin_add)
        btn_add.pack(fill = "x", pady = 5)
        btn_update = ttk.Button(right_pane, text="Update Existing Resource", command=self.handle_admin_update)
        btn_update.pack(fill = "x", pady = 5)
        btn_delete = ttk.Button(right_pane, text = "Remove Selected Asset", command = self.handle_admin_delete)
        btn_delete.pack(fill = "x", pady = 5)
        self.update_admin_resource_tree()
    def update_admin_resource_tree(self):
        for item in self.tree_admin_resources.get_children():
            self.tree_admin_resources.delete(item)
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT resource_id, name, type FROM resources WHERE campus_id = ?", (self.active_campus_id,))
            for row in cursor.fetchall():
                self.tree_admin_resources.insert("","end", values = row)
    def populate_admin_fields(self, event):
        selected = self.tree_admin_resources.selection()
        if not selected:
            return
        values = self.tree_admin_resources.item(selected)["values"]
        self.ent_admin_res_id.delete(0, tk.END)
        self.ent_admin_res_id.insert(0, values[0])
        self.ent_admin_res_name.delete(0, tk.END)
        self.ent_admin_res_name.insert(0, values[1])
        self.cb_admin_res_type.set(values[2])
    def handle_admin_add(self):
        r_id = self.ent_admin_res_id.get().strip()
        r_name = self.ent_admin_res_name.get().strip()
        r_type = self.cb_admin_res_type.get()
        if not r_id or not r_name:
            messagebox.showerror("Input Error","All field must be populated to save a new resource")
            return
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO resources (resource_id, name, type) VALUES (?, ?,?, ?)", (r_id, self.active_campus_id, r_name, r_type))
                conn.commit()
            messagebox.showinfo("Success", "Resource registered successfully")
            self.update_admin_resource_tree()
        except sqlite3.IntegrityError:
            messagebox.showerror("Duplicate Error", "This Resource ID is already allocated within the system.")
    def handle_admin_update(self):
        selected = self.tree_admin_resources.selection()
        if not selected:
            messagebox.showerror("Selection Error","Please select a resource item from the list to modify.")
            return
        r_id = self.ent_admin_res_id.get().strip()
        r_name = self.ent_admin_res_name.get().strip()
        r_type = self.cb_admin_res_type.get()
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("Update resources SET name = ?, type = ? WHERE resource_id = ? AND campus_id = ?",(r_name, r_type, r_id, self.active_campus_id))
            conn.commit()
        messagebox.showinfo("Success", "Resource information altered successfully.")
        self.update_admin_resource_tree()
    def handle_admin_delete(self):
        selected = self.tree_admin_resources.selected()
        if not selected:
            messagebox.showerror("Selection Error", "Please highlight the target asset you wish to remove.")
            return
        r_id = self.tree_admin_resources.item(selected)["values"][0]
        if messagebox.askyesno("Confirm Drop", "Permanently clear this asset and all its linked reservations?"):
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM resources WHERE resource_id = ? AND campus_id = ?", (r_id, self.active_campus_id))
                conn.commit()
            messagebox.showinfo("Asset Revoked", "The resource data table entry has been deleted.")
            self.update_admin_resource_tree()
    def build_operator_tabs(self):
        tab_reports = ttk.Frame(self.notebook)
        self.notebook.add(tab_reports, text = "Cross-Campus Metrics Analytics View")
        top_pane = ttk.Frame(tab_reports, padding = "10")
        top_pane.pack(side = "top", fill = "x")
        ttk.Label(top_pane, text = "Comparative System Usage Summary Reports Engine", font = ("Arial", 12,"bold")).pack(side = "left")
        btn_refresh = ttk.Button(top_pane, text = "Compute System Reporting Indicators", command = self.calculate_operator_metrics)
        btn_refresh.pack(side = "right")
        self.tree_operator_reports = ttk.Treeview(tab_reports, columns =("Campus", "TotalBookings", "AvgDuration"),show = "headings")
        self.tree_operator_reports.heading("Campus", text = "Campus Site Location")
        self.tree_operator_reports.heading("TotalBookings", text = "Accumulated Booking Index Count")
        self.tree_operator_reports.heading("AvgDuration", text = "Average Allocation Window Length (Hours)")
        self.tree_operator_reports.pack(fill = "both", expand = True, padx = 10, pady = 10)
    def calculate_operator_metrics(self):
        for item in self.tree_operator_reports.get_children():
            self.tree_operator_reports.delete(item)
            self.calculate_operator_metrics()
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT c.name, COUNT(b.booking_id), IFNULL(AVG(b.duration), 0.0)FROM campuses c LEFT JOIN resources r ON c.campus_id = r.campus_id LEFT JOIN bookings b ON r.resource_id = b.resource_id GROUP BY c.campus_id""")
            for row in cursor.fetchall():
                formatted_row = (row[0], row[1], f"{row[2]:.2f} Hours")
                self.tree_operator_reports.insert("", "end", values = formatted_row)
if __name__ == "__main__":
    init_db()
    main_window = tk.Tk()
    app = SmartCampusApp(main_window)
    main_window.mainloop()