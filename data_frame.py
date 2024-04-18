from tkinter import ttk, messagebox
from customtkinter import *
from PIL import Image
from datetime import datetime, timedelta
from tkcalendar import Calendar
from database import Database
from openpyxl import Workbook
from toggle_button import ToggleButton
from utility import *


class DataFrame(CTkFrame):
    def __init__(self, parent, db: Database, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.db = db
        self.date_picker_opened = False
        self.download_logo = CTkImage(
            Image.open(resource_path("assets/download.png")), size=(30, 30)
        )
        self.configure(border_width=4, border_color="#5665EF", corner_radius=0)
        self.create_filter_frame()
        self.show_table()

    def create_filter_frame(self):
        # Frame for filter options
        self.filter_frame = CTkFrame(self, fg_color="#B188A8", corner_radius=3)
        self.filter_frame.pack(
            side="top", fill="x", padx=6, pady=(6, 1), ipadx=10, ipady=10
        )

        self.filter_course_label = CTkLabel(
            self.filter_frame, text="Course:", bg_color="#B188A8", text_color="black"
        )
        self.filter_course_label.pack(side="left", padx=10)
        self.filter_course_entry = CTkComboBox(
            self.filter_frame,
            command=self.show_table,
            values=["ALL", "BSC", "BCA", "BBA"],
            bg_color="#B188A8",
            state="readonly",
            width=100
        )
        self.filter_course_entry.set("ALL")
        self.filter_course_entry.pack(side="left")

        self.filter_sem_label = CTkLabel(
            self.filter_frame, text="Sem:", bg_color="#B188A8", text_color="black"
        )
        self.filter_sem_label.pack(side="left", padx=10)
        self.filter_sem_entry = CTkComboBox(
            self.filter_frame,
            command=self.show_table,
            values=["ALL", "1", "2", "3", "4", "5", "6"],
            bg_color="#B188A8",
            state="readonly",
            width=100
        )
        self.filter_sem_entry.set("ALL")
        self.filter_sem_entry.pack(side="left")

        self.toggle_button = ToggleButton(
            self.filter_frame,
            texts=("Switch to Staff", "Switch to Students"),
            font=("Arial", 15, "bold"),
            width = 200,
            callbacks=(self.show_table, self.show_table),
        )
        self.toggle_button.place(rely=0.5, relx=0.5, anchor="center")
        
        self.max_date = StringVar()
        self.max_date_entry = CTkEntry(self.filter_frame, textvariable=self.max_date, width=100)
        self.max_date_entry.pack(side="right", padx=10)
        self.max_date_entry.bind(
            "<Button-1>", lambda event: self.open_date_picker(event, self.max_date)
        )
        self.max_date_entry.configure(state=DISABLED)

        self.max_date_label = CTkLabel(
            self.filter_frame, text="To:", bg_color="#B188A8", text_color="black"
        )
        self.max_date_label.pack(side="right")

        self.min_date = StringVar()
        self.min_date_entry = CTkEntry(self.filter_frame, textvariable=self.min_date, width=100)
        self.min_date_entry.pack(side="right", padx=10)
        self.min_date_entry.bind(
            "<Button-1>", lambda event: self.open_date_picker(event, self.min_date)
        )
        self.min_date_entry.configure(state=DISABLED)

        self.min_date_label = CTkLabel(
            self.filter_frame, text="From:", bg_color="#B188A8", text_color="black"
        )
        self.min_date_label.pack(side="right")
        self.set_default_date()
        self.set_date_list()

    def show_table(self, *args):
        try:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
            self.tree.destroy()
        except:
            pass

        if self.dates:
            style = ttk.Style()
            style.theme_use("clam")
            style.configure(
                "Treeview",
                background="#363636",
                fieldbackground="#363636",
                foreground="white",
                font=("Arial", 10),
            )
            style.map("Treeview", background=[("selected", "#4a4a4a")])

            # Create the Treeview
            self.tree = ttk.Treeview(self, selectmode="extended")
            self.tree.pack(side="left", fill="both", expand=True, padx=8, pady=(1, 8))

            # Scrollbar for the Treeview
            yscroll = tk.Scrollbar(
                self.tree, orient="vertical", command=self.tree.yview, width=15
            )
            yscroll.pack(side=tk.RIGHT, fill=tk.Y)

            xscroll = tk.Scrollbar(
                self.tree, orient="horizontal", command=self.tree.xview, width=15
            )
            xscroll.pack(side=tk.BOTTOM, fill=tk.X)

            self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)

            dates = [datetime.strptime(date, "%Y-%m-%d").strftime("%d/%m/%Y") for date in self.dates]
            self.tree["columns"] = ["ID", "Name"] + dates
            self.tree.column("#0", width=0, stretch=tk.NO)
            self.tree.column("ID", anchor=tk.W, width=100)
            self.tree.heading("ID", text="ID", anchor=tk.W)
            self.tree.column("Name", anchor=tk.W, width=150)
            self.tree.heading("Name", text="Name", anchor=tk.W)
            for i in dates:
                self.tree.column(i, anchor=tk.W, width=10)
                self.tree.heading(
                    i,
                    text=i,
                    anchor=tk.W,
                )
            
            data = self.db.fetch_data(self.generate_query())
            for row in data:
                self.tree.insert("", "end", values=row)

            self.download_button = CTkButton(
                self.tree,
                command= lambda:self.save_tree(self.tree),
                image=self.download_logo,
                text="",
                width=30,
                height=30,
                bg_color="#363636",
                fg_color="#1B1B1B",
                hover_color="#4C4C4C",
            )
            self.download_button.place(rely=0.96, relx=0.98, anchor="se")

    def save_tree(self, tree: ttk.Treeview):
        try:
            if not os.path.exists("./Saved files"):
                os.makedirs("./Saved_Files")
            wb = Workbook()
            ws = wb.active
            headers = tree["columns"]
            ws.append(headers)
            
            for item in tree.get_children():
                row = tree.item(item)['values']
                ws.append(row)
            course = self.filter_course_entry.get()
            sem = self.filter_sem_entry.get()
            dt1 = datetime.strptime(self.min_date.get(), "%Y-%m-%d").strftime("%d-%m-%y")
            dt2 = datetime.strptime(self.max_date.get(), "%Y-%m-%d").strftime("%d-%m-%y")
            if not self.toggle_button.state:
                file_name = f"./Saved_Files/{course} {sem} {dt1}_{dt2}.xlsx"
            else:
                file_name = f"./Saved_Files/Staff {dt1}_{dt2}.xlsx"
            wb.save(file_name)
            messagebox.showinfo("Info", "File saved.")
        except Exception as e:
            print(e)
            messagebox.showerror("Error", "File couldn't be saved.")

    def generate_query(self):
        sem = self.filter_sem_entry.get()
        course = self.filter_course_entry.get()
        clicked = self.toggle_button.state
        date_cases = ",\n    ".join(
            [
                f"""
                MAX(
                    CASE
                        WHEN 
                            a.Date = '{date}' 
                        THEN 
                            {
                                "CONCAT_WS(' - ',COALESCE(DATE_FORMAT(a.CheckIn, '%l:%i %p'), 'No CheckIn'),COALESCE(DATE_FORMAT(a.CheckOut, '%l:%i %p'), 'No CheckOut')) ELSE '-'"
                                if clicked else "'P' ELSE 'A'"
                            }  
                        END
                ) AS `{date}`
                """
                for date in self.dates
            ]
        )
        if not clicked:
            query = f"""
SELECT
    s.ID,
    s.Name,
    {date_cases}
FROM
    student_face s
LEFT JOIN
    student_attendance a ON s.ID = a.ID
WHERE
    1=1
    AND s.Sem like '{'%' if sem == "ALL" else sem}' AND s.Course like '{'%' if course == "ALL" else course}'
GROUP BY
    s.ID,
    s.Name
"""
        else:
            query = f"""
SELECT
    s.ID,
    s.Name,
    {date_cases}
FROM
    staff_face s
LEFT JOIN
    staff_attendance a ON s.ID = a.ID
GROUP BY
    s.ID,
    s.Name
"""
        
        return query

    def open_date_picker(self, event, input_field_text: StringVar):

        if self.date_picker_opened:
            return
        self.date_picker_opened = True

        def on_date_select(event):
            selected_date = cal.selection_get()
            input_field_text.set(selected_date)
            cal.destroy()
            self.date_picker_opened = False
            self.set_date_list()
            self.show_table()

        cal = Calendar(
            self.parent, selectmode="day", mindate=self.oldest_date, maxdate=self.recent_date
        )
        cal.place(rely=0.5, relx=0.5, anchor="center")
        cal.bind("<<CalendarSelected>>", on_date_select)

    def set_date_range(self):
        self.recent_date = datetime.date(datetime.now())
        self.oldest_date = self.db.fetch_data("SELECT MIN(Date) from attendance")[0][0]
        if not self.oldest_date:
            self.oldest_date = self.recent_date

    def set_default_date(self):
        self.set_date_range()
        now = datetime.date(datetime.now())
        first_day_of_month = now.replace(day=1)
        self.min_date.set(
            max(first_day_of_month, self.oldest_date).strftime("%Y-%m-%d")
        )
        self.max_date.set(self.recent_date.strftime("%Y-%m-%d"))

    def set_date_list(self):
        min_date = self.min_date.get()
        max_date = self.max_date.get()

        start = datetime.strptime(min_date, "%Y-%m-%d")
        end = datetime.strptime(max_date, "%Y-%m-%d")
        date_generated = [
            start + timedelta(days=x) for x in range(0, (end - start).days + 1)
        ]
        self.dates = [date.strftime("%Y-%m-%d") for date in date_generated]
