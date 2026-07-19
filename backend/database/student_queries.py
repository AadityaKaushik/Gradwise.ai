from database.connection import get_connection, return_connection
import psycopg2


def create_student(user_id, org_id, program_id, roll_no, admission_year):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO v3.students
                (user_id, organization_id, program_id, roll_no, admission_year)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING user_id
        """, (user_id, org_id, program_id, roll_no, admission_year))

        row = cursor.fetchone()
        if not row:
            raise ValueError("Failed to create student record")

        conn.commit()

        return {
            "user_id": row[0],
            "message": "Student profile created successfully"
        }

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise ValueError("Student record already exists (duplicate user or roll number)")

    except psycopg2.errors.ForeignKeyViolation:
        conn.rollback()
        raise ValueError("Invalid user, organization, or program reference")

    except psycopg2.errors.CheckViolation:
        conn.rollback()
        raise ValueError("Admission year must be between 2000 and 2100")

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def get_student_by_user_id(user_id):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT s.user_id, s.organization_id, s.program_id, s.roll_no,
                   s.admission_year, s.academic_status,
                   u.email, p.name AS program_name
            FROM v3.students s
            JOIN v3.users u ON u.user_id = s.user_id
            JOIN v3.programs p ON p.program_id = s.program_id
            WHERE s.user_id = %s
        """, (user_id,))

        row = cursor.fetchone()
        if not row:
            return None

        return {
            "user_id": row[0],
            "organization_id": row[1],
            "program_id": row[2],
            "roll_no": row[3],
            "admission_year": row[4],
            "academic_status": row[5],
            "email": row[6],
            "program_name": row[7],
        }

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def get_students_by_org(org_id):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT s.user_id, s.roll_no, s.admission_year, s.academic_status,
                   u.email, p.name AS program_name
            FROM v3.students s
            JOIN v3.users u ON u.user_id = s.user_id
            JOIN v3.programs p ON p.program_id = s.program_id
            WHERE s.organization_id = %s
            ORDER BY s.roll_no
        """, (org_id,))

        rows = cursor.fetchall()
        return [
            {
                "user_id": r[0],
                "roll_no": r[1],
                "admission_year": r[2],
                "academic_status": r[3],
                "email": r[4],
                "program_name": r[5],
            }
            for r in rows
        ]

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def get_students_by_program(program_id):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT s.user_id, s.roll_no, s.admission_year, s.academic_status,
                   u.email
            FROM v3.students s
            JOIN v3.users u ON u.user_id = s.user_id
            WHERE s.program_id = %s
            ORDER BY s.roll_no
        """, (program_id,))

        rows = cursor.fetchall()
        return [
            {
                "user_id": r[0],
                "roll_no": r[1],
                "admission_year": r[2],
                "academic_status": r[3],
                "email": r[4],
            }
            for r in rows
        ]

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def update_academic_status(user_id, new_status):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE v3.students
            SET academic_status = %s
            WHERE user_id = %s
            RETURNING user_id, academic_status
        """, (new_status, user_id))

        row = cursor.fetchone()
        if not row:
            raise ValueError("Student not found")

        conn.commit()

        return {
            "user_id": row[0],
            "academic_status": row[1],
            "message": "Academic status updated successfully"
        }

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)
