from fastapi import FastAPI, HTTPException
from db import get_cursor
from schemas import AttendanceCreate

app = FastAPI(title="BJJ Academy Backend")

# ------------------------------------------------
# Insert attendance
# ------------------------------------------------
@app.post("/attendance")
def register_attendance(data: AttendanceCreate):
    cur = get_cursor()

    try:
        cur.execute("""
            INSERT INTO t_attendance (session_id, student_id, status, checkin_source)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (session_id, student_id) DO NOTHING
        """, (
            data.session_id,
            data.student_id,
            data.status,
            data.checkin_source
        ))
        return {"status": "ok", "message": "Attendance registered"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ------------------------------------------------
# Attendance by session
# ------------------------------------------------
@app.get("/attendance/session/{session_id}")
def attendance_by_session(session_id: int):
    cur = get_cursor()

    cur.execute("""
        SELECT 
            st.name AS student,
            c.name AS class_name,
            cs.session_date,
            a.status,
            a.checkin_time
        FROM t_attendance a
        JOIN t_students st ON a.student_id = st.id
        JOIN t_class_sessions cs ON a.session_id = cs.id
        JOIN t_classes c ON cs.class_id = c.id
        WHERE cs.id = %s
        ORDER BY st.name
    """, (session_id,))

    rows = cur.fetchall()
    return rows

# ------------------------------------------------
# Attendance by student
# ------------------------------------------------
@app.get("/attendance/student/{student_id}")
def attendance_by_student(student_id: int):
    cur = get_cursor()

    cur.execute("""
        SELECT 
            c.name AS class_name,
            cs.session_date,
            a.status,
            a.checkin_time
        FROM t_attendance a
        JOIN t_class_sessions cs ON a.session_id = cs.id
        JOIN t_classes c ON cs.class_id = c.id
        WHERE a.student_id = %s
        ORDER BY cs.session_date DESC
    """, (student_id,))

    return cur.fetchall()
