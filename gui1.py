import tkinter as tk
from tkinter import ttk, messagebox
from db import execute

# =====================================================
# LOAD DATA (maps: label -> id)
# =====================================================
def load_students():
    rows = execute("SELECT id, name FROM t_students ORDER BY name")
    return {name: sid for sid, name in rows}

def load_sessions():
    rows = execute("""
        SELECT cs.id,
               c.name || ' - ' || cs.session_date || ' ' || cs.start_time
        FROM t_class_sessions cs
        JOIN t_classes c ON cs.class_id = c.id
        ORDER BY cs.session_date DESC, cs.start_time
    """)
    return {label: sid for sid, label in rows}

# =====================================================
# ACTIONS
# =====================================================
def register_attendance():
    try:
        student_id = students_map[att_student_var.get()]
        session_id = sessions_map[att_session_var.get()]

        execute("""
            INSERT INTO t_attendance (session_id, student_id, status, checkin_source)
            VALUES (%s,%s,%s,%s)
            ON CONFLICT DO NOTHING
        """, (
            session_id,
            student_id,
            att_status.get(),
            att_source.get()
        ))

        messagebox.showinfo("OK", "Attendance registered")

    except KeyError:
        messagebox.showerror("Error", "Select student and session")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def register_student():
    try:
        execute("""
            INSERT INTO t_students (name, email, belt, phone, country)
            VALUES (%s,%s,%s,%s,%s)
        """, (
            st_name.get(),
            st_email.get(),
            st_belt.get(),
            st_phone.get(),
            st_country.get()
        ))
        refresh_students()
        messagebox.showinfo("OK", "Student registered")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def register_coach():
    try:
        execute("""
            INSERT INTO t_coaches (name, email, belt, phone, hire_date)
            VALUES (%s,%s,%s,%s,CURRENT_DATE)
        """, (
            co_name.get(),
            co_email.get(),
            co_belt.get(),
            co_phone.get()
        ))
        messagebox.showinfo("OK", "Coach registered")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def refresh_students():
    global students_map
    students_map = load_students()
    cmb_students["values"] = list(students_map.keys())


# =====================================================
# UI
# =====================================================
root = tk.Tk()
root.title("BJJ Academy Management")
root.geometry("750x520")

notebook = ttk.Notebook(root)
notebook.grid(row=0, column=0, sticky="nsew")

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# =====================================================
# TAB 1 - ATTENDANCE
# =====================================================
tab_att = ttk.Frame(notebook, padding=10)
notebook.add(tab_att, text="Attendance")

students_map = load_students()
sessions_map = load_sessions()

att_student_var = tk.StringVar()
att_session_var = tk.StringVar()
att_status = tk.StringVar(value="present")
att_source = tk.StringVar(value="coach")

ttk.Label(tab_att, text="Student").grid(row=0, column=0, sticky="w")
cmb_students = ttk.Combobox(
    tab_att,
    textvariable=att_student_var,
    values=list(students_map.keys()),
    state="readonly",
    width=45
)
cmb_students.grid(row=0, column=1, pady=3)

ttk.Label(tab_att, text="Session").grid(row=1, column=0, sticky="w")
cmb_sessions = ttk.Combobox(
    tab_att,
    textvariable=att_session_var,
    values=list(sessions_map.keys()),
    state="readonly",
    width=45
)
cmb_sessions.grid(row=1, column=1, pady=3)

ttk.Label(tab_att, text="Status").grid(row=2, column=0, sticky="w")
ttk.Combobox(
    tab_att,
    textvariable=att_status,
    values=["present","late","absent","no_show"],
    state="readonly"
).grid(row=2, column=1, sticky="w")

ttk.Label(tab_att, text="Source").grid(row=3, column=0, sticky="w")
ttk.Combobox(
    tab_att,
    textvariable=att_source,
    values=["coach","qr","kiosk","admin"],
    state="readonly"
).grid(row=3, column=1, sticky="w")

ttk.Button(
    tab_att,
    text="Register Attendance",
    command=register_attendance
).grid(row=4, column=0, columnspan=2, pady=10)

# =====================================================
# TAB 2 - STUDENTS
# =====================================================
tab_students = ttk.Frame(notebook, padding=10)
notebook.add(tab_students, text="Students")

st_name = tk.StringVar()
st_email = tk.StringVar()
st_belt = tk.StringVar()
st_phone = tk.StringVar()
st_country = tk.StringVar(value="Austria")

ttk.Label(tab_students, text="Name").grid(row=0, column=0, sticky="w")
ttk.Entry(tab_students, textvariable=st_name, width=40).grid(row=0, column=1)

ttk.Label(tab_students, text="Email").grid(row=1, column=0, sticky="w")
ttk.Entry(tab_students, textvariable=st_email, width=40).grid(row=1, column=1)

ttk.Label(tab_students, text="Belt").grid(row=2, column=0, sticky="w")
ttk.Combobox(
    tab_students,
    textvariable=st_belt,
    values=["White","Blue","Purple","Brown","Black"],
    state="readonly"
).grid(row=2, column=1, sticky="w")

ttk.Label(tab_students, text="Phone").grid(row=3, column=0, sticky="w")
ttk.Entry(tab_students, textvariable=st_phone, width=40).grid(row=3, column=1)

ttk.Label(tab_students, text="Country").grid(row=4, column=0, sticky="w")
ttk.Entry(tab_students, textvariable=st_country, width=40).grid(row=4, column=1)

ttk.Button(
    tab_students,
    text="Register Student",
    command=register_student
).grid(row=5, column=0, columnspan=2, pady=10)

# =====================================================
# TAB 3 - COACHES
# =====================================================
tab_coaches = ttk.Frame(notebook, padding=10)
notebook.add(tab_coaches, text="Coaches")

co_name = tk.StringVar()
co_email = tk.StringVar()
co_belt = tk.StringVar()
co_phone = tk.StringVar()

ttk.Label(tab_coaches, text="Name").grid(row=0, column=0, sticky="w")
ttk.Entry(tab_coaches, textvariable=co_name, width=40).grid(row=0, column=1)

ttk.Label(tab_coaches, text="Email").grid(row=1, column=0, sticky="w")
ttk.Entry(tab_coaches, textvariable=co_email, width=40).grid(row=1, column=1)

ttk.Label(tab_coaches, text="Belt").grid(row=2, column=0, sticky="w")
ttk.Combobox(
    tab_coaches,
    textvariable=co_belt,
    values=["Brown","Black"],
    state="readonly"
).grid(row=2, column=1, sticky="w")

ttk.Label(tab_coaches, text="Phone").grid(row=3, column=0, sticky="w")
ttk.Entry(tab_coaches, textvariable=co_phone, width=40).grid(row=3, column=1)

ttk.Button(
    tab_coaches,
    text="Register Coach",
    command=register_coach
).grid(row=4, column=0, columnspan=2, pady=10)

root.mainloop()
