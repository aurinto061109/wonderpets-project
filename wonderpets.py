import flet as ft
import sqlite3
import csv

class DigitalFormsApp:
    def __init__(self):
        self.db_connection = sqlite3.connect("attendance.db", check_same_thread=False)
        self.create_table()

    def create_table(self):
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                form_name TEXT NOT NULL
            )
        """
        self.execute_sql(create_table_sql)

    def execute_sql(self, sql, params=()):
        """Execute a given SQL command with optional parameters."""
        with self.db_connection:
            self.db_connection.execute(sql, params)

    def main(self, page: ft.Page):
        page.title = "Digital Forms Management - WONDERPETS"
        page.window.width = 720
        page.window.height = 640

        self.form_name_input = ft.TextField(label="Enter Name:", width=300)
        self.tracking_listbox = ft.ListView(width=300, height=200)

        # Create a Text control for feedback messages
        self.feedback_text = ft.Text("", color="green", size=16)

        # Add a key event listener to the TextField
        self.form_name_input.on_submit = self.submit_form  # This will call submit_form when Enter is pressed

        self.create_ui(page)

    def create_ui(self, page):
        page.add(
            ft.Column(
                controls=[
                    ft.Text("Employer Attendance", size=20, weight="bold"),
                    self.form_name_input,
                    ft.ElevatedButton("Submit", on_click=self.submit_form),
                    ft.Text("Attendance List", size=20, weight="bold"),
                    self.tracking_listbox,
                    ft.ElevatedButton("Export Data", on_click=self.export_data),
                    self.feedback_text  # Add feedback text to the UI
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=10
            )
        )
        self.load_forms()

    def submit_form(self, e):
        form_name = self.form_name_input.value.strip()
        if form_name:
            self.save_form_to_db(form_name)
            self.add_to_tracking_list(form_name)  # No count needed
            self.update_feedback("Form submitted successfully.")
        else:
            self.update_feedback("Please enter a name.")
        
        # Clear the input field after processing the submission
        self.form_name_input.value = ""
        self.form_name_input.update()  # Ensure the input field is updated

    def save_form_to_db(self, form_name):
        insert_sql = "INSERT INTO attendance (form_name) VALUES (?)"
        self.execute_sql(insert_sql, (form_name,))

    def load_forms(self):
        cursor = self.db_connection.cursor()
        cursor.execute("""
            SELECT form_name, COUNT(*) as total_forms
            FROM attendance
            GROUP BY form_name
            ORDER BY total_forms DESC
        """)
        forms = cursor.fetchall()
        for form in forms:
            self.add_to_tracking_list(form[0])  # No count needed

    def add_to_tracking_list(self, form_name):
        delete_button = ft.IconButton(icon=ft.Icons.DELETE, on_click=lambda e: self.remove_form_ui(form_name))
        list_tile = ft.ListTile(title=ft.Text(form_name), trailing=delete_button)  # Only show the form name
        self.tracking_listbox.controls.append(list_tile)
        self.tracking_listbox.update()  # Update the ListView to reflect the new item

    def remove_form_ui(self, form_name):
        delete_sql = "DELETE FROM attendance WHERE form_name = ?"
        self.execute_sql(delete_sql, (form_name,))
        self.update_tracking_list()
        self.update_feedback("Form deleted successfully.")

    def update_tracking_list(self):
        self.tracking_listbox.controls.clear()
        self.load_forms()  # Reload forms from the database
        self.tracking_listbox.update()  # Ensure the ListView is updated

    def export_data(self, e):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT form_name FROM attendance")
        forms = cursor.fetchall()

        if not forms:
            self.update_feedback("No data to export.")
            return

        with open("Attendance_List.csv", "w", newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Form Names"])  # Write header
            for form in forms:
                writer.writerow([form[0]])  # Write only the form name

        self.update_feedback("Data exported to Attendance_List.csv.")

    def update_feedback(self, message):
        self.feedback_text.value = message  # Update the feedback text
        self.feedback_text.update() 
        # Ensure the feedback text is updated

if __name__ == "__main__":
    app = DigitalFormsApp()
    ft.app(target=app.main)