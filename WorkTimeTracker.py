import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import sqlite3
import calendar

DATABASE_FILE = 'work_time.db'

class WorkTimeTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Work Time Tracker")

        self.conn = sqlite3.connect(DATABASE_FILE)
        self.create_table()

        self.label = tk.Label(root, text="Нажмите 'Пришел на работу' или 'Ушел с работы'")
        self.label.pack(pady=10)

        self.start_button = tk.Button(root, text="Пришел на работу", command=self.record_start_time)
        self.start_button.pack(pady=5)

        self.end_button = tk.Button(root, text="Ушел с работы", command=self.record_end_time)
        self.end_button.pack(pady=5)

        self.month_label = tk.Label(root, text="Выберите месяц:")
        self.month_label.pack(pady=10)

        self.month_var = tk.StringVar(root)
        self.month_var.set(calendar.month_name[datetime.now().month])
        self.month_menu = tk.OptionMenu(root, self.month_var, *calendar.month_name[1:])
        self.month_menu.pack(pady=5)

        self.view_stats_button = tk.Button(root, text="Просмотреть статистику", command=self.view_stats)
        self.view_stats_button.pack(pady=10)

        self.clear_db_button = tk.Button(root, text="Очистить базу данных", command=self.clear_database)
        self.clear_db_button.pack(pady=10)

    def create_table(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS work_log
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      event_type TEXT,
                      event_time DATETIME)''')
        self.conn.commit()

    def record_event(self, event_type):
        c = self.conn.cursor()
        event_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute("INSERT INTO work_log (event_type, event_time) VALUES (?, ?)", (event_type, event_time))
        self.conn.commit()

    def record_start_time(self):
        self.record_event('start')
        self.label.config(text=f"Вы пришли на работу в {datetime.now().strftime('%H:%M:%S')}")

    def record_end_time(self):
        self.record_event('end')
        self.label.config(text=f"Вы ушли с работы в {datetime.now().strftime('%H:%M:%S')}")

    def view_stats(self):
        month = list(calendar.month_name).index(self.month_var.get())
        year = datetime.now().year

        _, days_in_month = calendar.monthrange(year, month)

        avg_work_hours_per_day = 8

        total_work_hours_month = days_in_month * avg_work_hours_per_day

        c = self.conn.cursor()
        c.execute("SELECT event_type, event_time FROM work_log WHERE strftime('%m', event_time) = ? AND strftime('%Y', event_time) = ?",
                  (str(month).zfill(2), str(year)))
        records = c.fetchall()

        if not records:
            messagebox.showinfo("Статистика", "Нет записей за выбранный месяц.")
            return

        stats_window = tk.Toplevel(self.root)
        stats_window.title("Статистика за месяц")

        stats_label = tk.Label(stats_window, text=f"Статистика за {calendar.month_name[month]} {year}:")
        stats_label.pack(pady=10)

        total_work_time = 0
        stats_text = ""
        prev_event_time = None
        for record in records:
            event_type, event_time = record
            event_time = datetime.strptime(event_time, '%Y-%m-%d %H:%M:%S')

            if event_type == 'start':
                prev_event_time = event_time
            elif event_type == 'end' and prev_event_time:
                work_duration = event_time - prev_event_time
                total_work_time += work_duration.total_seconds() / 3600.0
                stats_text += f"{prev_event_time}: Работал {work_duration.total_seconds() / 3600.0:.2f} часов\n"
                prev_event_time = None

        stats_display = tk.Label(stats_window, text=stats_text)
        stats_display.pack(pady=10)

        remaining_work_hours = max(0, total_work_hours_month - total_work_time)
        remaining_work_hours_label = tk.Label(stats_window, text=f"Осталось отработать: {remaining_work_hours:.2f} часов")
        remaining_work_hours_label.pack(pady=10)

    def clear_database(self):
        c = self.conn.cursor()
        c.execute("DELETE FROM work_log")
        self.conn.commit()
        messagebox.showinfo("База данных", "База данных успешно очищена.")

if __name__ == "__main__":
    root = tk.Tk()
    app = WorkTimeTracker(root)
    root.mainloop()