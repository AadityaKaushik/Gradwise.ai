from database.connection import get_connection, return_connection
import psycopg2


def create_session(offering_id, session_date, topic=None):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO v3.attendance_sessions (offering_id, session_date, topic)
            VALUES (%s, %s, %s)
            RETURNING session_id
        """, (offering_id, session_date, topic))

        row = cursor.fetchone()
        if not row:
            raise ValueError("Failed to create attendance session")

        session_id = row[0]
        conn.commit()

        return {
            "session_id": session_id,
            "message": "Attendance session created successfully"
        }

    except psycopg2.errors.ForeignKeyViolation:
        conn.rollback()
        raise ValueError("Invalid course offering reference")

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def get_sessions_by_offering(offering_id):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT session_id, session_date, topic
            FROM v3.attendance_sessions
            WHERE offering_id = %s
            ORDER BY session_date DESC
        """, (offering_id,))

        rows = cursor.fetchall()
        return [
            {
                "session_id": r[0],
                "session_date": str(r[1]),
                "topic": r[2],
            }
            for r in rows
        ]

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def record_attendance(session_id, student_user_id, status):
    """Insert or update a single attendance record."""
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO v3.attendance_records (session_id, student_user_id, status)
            VALUES (%s, %s, %s)
            ON CONFLICT (session_id, student_user_id)
                DO UPDATE SET status = EXCLUDED.status
            RETURNING record_id
        """, (session_id, student_user_id, status))

        row = cursor.fetchone()
        record_id = row[0]
        conn.commit()

        return {
            "record_id": record_id,
            "message": "Attendance recorded successfully"
        }

    except psycopg2.errors.ForeignKeyViolation:
        conn.rollback()
        raise ValueError("Invalid session or student reference")

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def bulk_record_attendance(session_id, records):
    """
    Batch record attendance for multiple students.
    records: list of dicts with 'student_user_id' and 'status'.
    """
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        for record in records:
            cursor.execute("""
                INSERT INTO v3.attendance_records (session_id, student_user_id, status)
                VALUES (%s, %s, %s)
                ON CONFLICT (session_id, student_user_id)
                    DO UPDATE SET status = EXCLUDED.status
            """, (session_id, record["student_user_id"], record["status"]))

        conn.commit()

        return {
            "count": len(records),
            "message": f"Attendance recorded for {len(records)} students"
        }

    except psycopg2.errors.ForeignKeyViolation:
        conn.rollback()
        raise ValueError("Invalid session or student reference in batch")

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def get_attendance_by_session(session_id):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT ar.record_id, ar.student_user_id, ar.status,
                   s.roll_no, u.email
            FROM v3.attendance_records ar
            JOIN v3.students s ON s.user_id = ar.student_user_id
            JOIN v3.users u ON u.user_id = s.user_id
            WHERE ar.session_id = %s
            ORDER BY s.roll_no
        """, (session_id,))

        rows = cursor.fetchall()
        return [
            {
                "record_id": r[0],
                "student_user_id": r[1],
                "status": r[2],
                "roll_no": r[3],
                "email": r[4],
            }
            for r in rows
        ]

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def get_student_attendance_summary(student_user_id, offering_id):
    """Count attendance by status for a student in a specific course offering."""
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT ar.status, COUNT(*) as count
            FROM v3.attendance_records ar
            JOIN v3.attendance_sessions asess ON asess.session_id = ar.session_id
            WHERE ar.student_user_id = %s AND asess.offering_id = %s
            GROUP BY ar.status
        """, (student_user_id, offering_id))

        rows = cursor.fetchall()
        summary = {r[0]: r[1] for r in rows}

        # Also get total sessions for this offering
        cursor.execute("""
            SELECT COUNT(*) FROM v3.attendance_sessions
            WHERE offering_id = %s
        """, (offering_id,))
        total_sessions = cursor.fetchone()[0]

        present = summary.get("PRESENT", 0)
        late = summary.get("LATE", 0)
        absent = summary.get("ABSENT", 0)
        excused = summary.get("EXCUSED", 0)
        attended = present + late

        return {
            "student_user_id": student_user_id,
            "offering_id": offering_id,
            "total_sessions": total_sessions,
            "present": present,
            "late": late,
            "absent": absent,
            "excused": excused,
            "attendance_percentage": round((attended / total_sessions * 100), 2) if total_sessions > 0 else 0,
        }

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)
