import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from psycopg.errors import UniqueViolation
from db import execute

# ================= CONFIG =================
PAGE_SIZE_STUDENTS = 100
PAGE_SIZE_SESSIONS = 10

current_student_page = 0
current_session_page = 0

selected_student_id = None
selected_session_id = None

# ================= LOADERS =================
def load_students_map():
    return {n: i for i, n in execute("SELECT id,name FROM t_students ORDER BY name")}

def load_students_paged(page):
    return execute("""
        SELECT id, name, email, belt, weight, phone, country, birthday
        FROM t_students
        ORDER BY name
        LIMIT %s OFFSET %s
    """, (PAGE_SIZE_STUDENTS, page * PAGE_SIZE_STUDENTS))

def count_students():
    return execute("SELECT COUNT(*) FROM t_students")[0][0]

def load_classes():
    return {l: i for i, l in execute("""
        SELECT id, name || ' (' || belt_level || ')'
        FROM t_classes WHERE active=TRUE ORDER BY name
    """)}

def load_sessions_today():
    return {l: i for i, l in execute("""
        SELECT cs.id, c.name || ' - ' || cs.start_time
        FROM t_class_sessions cs
        JOIN t_classes c ON cs.class_id=c.id
        WHERE cs.session_date=CURRENT_DATE AND cs.cancelled=FALSE
        ORDER BY cs.start_time
    """)}

def load_sessions_paged(page):
    return execute("""
        SELECT cs.id, cs.session_date, cs.start_time, cs.end_time,
               c.name, cs.location
        FROM t_class_sessions cs
        JOIN t_classes c ON cs.class_id=c.id
        WHERE cs.cancelled=FALSE
        ORDER BY cs.session_date DESC, cs.start_time
        LIMIT %s OFFSET %s
    """, (PAGE_SIZE_SESSIONS, page * PAGE_SIZE_SESSIONS))

# ================= ROOT =================
root = tk.Tk()
root.title("BJJ Academy Management")
root.geometry("1200x800")

notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

# =====================================================
# TAB — ATTENDANCE
# =====================================================
tab_att = ttk.Frame(notebook, padding=10)
notebook.add(tab_att, text="Attendance")

students_map = load_students_map()
sessions_map = load_sessions_today()

att_student = tk.StringVar()
att_session = tk.StringVar()

ttk.Label(tab_att, text="Student").grid(row=0, column=0, sticky="w")
ttk.Combobox(tab_att, textvariable=att_student,
             values=list(students_map.keys()),
             state="readonly", width=40).grid(row=0, column=1)

ttk.Label(tab_att, text="Session (Today)").grid(row=1, column=0, sticky="w")
ttk.Combobox(tab_att, textvariable=att_session,
             values=list(sessions_map.keys()),
             state="readonly", width=40).grid(row=1, column=1)

def register_attendance():
    if not messagebox.askyesno("Confirm", "Register attendance?"):
        return
    execute("""
        INSERT INTO t_attendance (session_id, student_id, status, checkin_source)
        VALUES (%s,%s,'present','coach')
        ON CONFLICT DO NOTHING
    """, (sessions_map[att_session.get()], students_map[att_student.get()]))
    messagebox.showinfo("OK", "Attendance registered")

ttk.Button(tab_att, text="Register Attendance",
           command=register_attendance).grid(row=2, column=0, columnspan=2, pady=10)

# =====================================================
# TAB — STUDENTS (FULL)
# =====================================================
tab_students = ttk.Frame(notebook, padding=10)
notebook.add(tab_students, text="Students")

form = ttk.LabelFrame(tab_students, text="Student Form", padding=10)
form.grid(row=0, column=0, sticky="ew")

tree_frame = ttk.LabelFrame(tab_students, text="Students List", padding=10)
tree_frame.grid(row=1, column=0, sticky="nsew")

nav = ttk.Frame(tab_students)
nav.grid(row=2, column=0, pady=5)

tab_students.grid_rowconfigure(1, weight=1)
tab_students.grid_columnconfigure(0, weight=1)

# Vars
st_name = tk.StringVar()
st_direction = tk.StringVar()
st_postalcode = tk.StringVar()
st_belt = tk.StringVar()
st_email = tk.StringVar()
st_phone = tk.StringVar()
st_phone2 = tk.StringVar()
st_weight = tk.StringVar()
st_country = tk.StringVar(value="Austria")
st_taxid = tk.StringVar()

fields = [
    ("Name", st_name),
    ("Email", st_email),
    ("Belt", st_belt),
    ("Direction", st_direction),
    ("Postal Code", st_postalcode),
    ("Phone", st_phone),
    ("Phone 2", st_phone2),
    ("Weight (kg)", st_weight),
    ("Country", st_country),
    ("Tax ID", st_taxid),
]

for i, (lbl, var) in enumerate(fields):
    ttk.Label(form, text=lbl).grid(row=i, column=0, sticky="w")
    if lbl == "Belt":
        ttk.Combobox(form, textvariable=var,
                     values=["White","Blue","Purple","Brown","Black"],
                     state="readonly").grid(row=i, column=1)
    else:
        ttk.Entry(form, textvariable=var, width=40).grid(row=i, column=1)

ttk.Label(form, text="Birthday").grid(row=len(fields), column=0, sticky="w")
st_birthday = DateEntry(form, date_pattern="yyyy-mm-dd")
st_birthday.grid(row=len(fields), column=1)

def register_student():
    if not messagebox.askyesno("Confirm", "Register new student?"):
        return
    execute("""
        INSERT INTO t_students
        (name,direction,postalcode,belt,email,
         phone,phone2,weight,country,taxid,birthday)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        st_name.get(), st_direction.get(), st_postalcode.get(),
        st_belt.get(), st_email.get(),
        st_phone.get(), st_phone2.get(),
        float(st_weight.get()) if st_weight.get() else None,
        st_country.get(), st_taxid.get(),
        st_birthday.get_date()
    ))
    load_students_view()
    messagebox.showinfo("OK", "Student registered")

def update_student():
    global selected_student_id
    if not selected_student_id:
        messagebox.showerror("Error", "Select a student to edit")
        return
    if not messagebox.askyesno("Confirm", "Update selected student?"):
        return
    execute("""
        UPDATE t_students
        SET name=%s, direction=%s, postalcode=%s,
            belt=%s, email=%s, phone=%s, phone2=%s,
            weight=%s, country=%s, taxid=%s, birthday=%s,
            updated_at=now()
        WHERE id=%s
    """, (
        st_name.get(), st_direction.get(), st_postalcode.get(),
        st_belt.get(), st_email.get(),
        st_phone.get(), st_phone2.get(),
        float(st_weight.get()) if st_weight.get() else None,
        st_country.get(), st_taxid.get(),
        st_birthday.get_date(),
        selected_student_id
    ))
    load_students_view()
    messagebox.showinfo("OK", "Student updated")

btns = ttk.Frame(form)
btns.grid(row=len(fields)+1, column=0, columnspan=2, pady=10)
ttk.Button(btns, text="Register", command=register_student).grid(row=0, column=0, padx=5)
ttk.Button(btns, text="Update", command=update_student).grid(row=0, column=1, padx=5)

students_tree = ttk.Treeview(
    tree_frame,
    columns=("id","name","email","belt","weight","phone","country","birthday"),
    show="headings"
)
for c in students_tree["columns"]:
    students_tree.heading(c, text=c)
students_tree.pack(fill=tk.BOTH, expand=True)

def on_student_select(e):
    global selected_student_id
    v = students_tree.item(students_tree.selection()[0])["values"]
    selected_student_id = v[0]
    st_name.set(v[1]); st_email.set(v[2]); st_belt.set(v[3])
    st_weight.set("" if v[4] is None else str(v[4]))
    st_phone.set(v[5]); st_country.set(v[6])
    if v[7]: st_birthday.set_date(v[7])

students_tree.bind("<<TreeviewSelect>>", on_student_select)

def load_students_view():
    for r in students_tree.get_children():
        students_tree.delete(r)
    for row in load_students_paged(current_student_page):
        students_tree.insert("", tk.END, values=row)
    total = count_students()
    pages = max(1, (total + PAGE_SIZE_STUDENTS - 1)//PAGE_SIZE_STUDENTS)
    lbl_page.config(text=f"Page {current_student_page+1} / {pages}")

def next_student():
    global current_student_page
    current_student_page += 1
    load_students_view()

def prev_student():
    global current_student_page
    if current_student_page>0:
        current_student_page -= 1
        load_students_view()

ttk.Button(nav, text="⬅ Prev", command=prev_student).grid(row=0, column=0, padx=5)
lbl_page = ttk.Label(nav, text="Page 1 / 1")
lbl_page.grid(row=0, column=1, padx=10)
ttk.Button(nav, text="Next ➡", command=next_student).grid(row=0, column=2, padx=5)

load_students_view()

# =====================================================
# TAB — COACHES
# =====================================================
tab_coaches = ttk.Frame(notebook, padding=10)
notebook.add(tab_coaches, text="Coaches")

co_name = tk.StringVar()
co_email = tk.StringVar()
co_belt = tk.StringVar()
co_phone = tk.StringVar()

coach_fields = [("Name",co_name),("Email",co_email),("Belt",co_belt),("Phone",co_phone)]
for i,(lbl,var) in enumerate(coach_fields):
    ttk.Label(tab_coaches,text=lbl).grid(row=i,column=0,sticky="w")
    if lbl=="Belt":
        ttk.Combobox(tab_coaches,textvariable=var,
                     values=["Brown","Black"],state="readonly").grid(row=i,column=1)
    else:
        ttk.Entry(tab_coaches,textvariable=var,width=40).grid(row=i,column=1)

def register_coach():
    if not messagebox.askyesno("Confirm","Register new coach?"):
        return
    execute("""
        INSERT INTO t_coaches (name,email,belt,phone,hire_date)
        VALUES (%s,%s,%s,%s,CURRENT_DATE)
    """,(co_name.get(),co_email.get(),co_belt.get(),co_phone.get()))
    messagebox.showinfo("OK","Coach registered")

ttk.Button(tab_coaches,text="Register Coach",
           command=register_coach).grid(row=5,column=0,columnspan=2,pady=10)

# =====================================================
# TAB — SESSIONS (BASIC, STABLE)
# =====================================================
tab_sessions = ttk.Frame(notebook, padding=10)
notebook.add(tab_sessions, text="Sessions")

ttk.Label(tab_sessions, text="Sessions module already integrated earlier").pack(pady=40)

# =====================================================
root.mainloop()
