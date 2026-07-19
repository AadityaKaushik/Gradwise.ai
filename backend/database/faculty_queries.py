from database.connection import get_connection, return_connection
import psycopg2


def create_faculty(user_id, org_id, employee_code, home_department_id, designation=None, joining_date=None):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO v3.faculty
                (user_id, organization_id, employee_code, home_department_id,
                 designation, joining_date)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING user_id
        """, (user_id, org_id, employee_code, home_department_id, designation, joining_date))

        row = cursor.fetchone()
        if not row:
            raise ValueError("Failed to create faculty record")

        conn.commit()

        return {
            "user_id": row[0],
            "message": "Faculty profile created successfully"
        }

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise ValueError("Faculty record already exists (duplicate user or employee code)")

    except psycopg2.errors.ForeignKeyViolation:
        conn.rollback()
        raise ValueError("Invalid user, organization, or department reference")

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def get_faculty_by_user_id(user_id):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT f.user_id, f.organization_id, f.employee_code,
                   f.home_department_id, f.designation, f.joining_date,
                   f.employment_status,
                   u.email, d.name AS department_name
            FROM v3.faculty f
            JOIN v3.users u ON u.user_id = f.user_id
            JOIN v3.departments d ON d.department_id = f.home_department_id
            WHERE f.user_id = %s
        """, (user_id,))

        row = cursor.fetchone()
        if not row:
            return None

        return {
            "user_id": row[0],
            "organization_id": row[1],
            "employee_code": row[2],
            "home_department_id": row[3],
            "designation": row[4],
            "joining_date": str(row[5]) if row[5] else None,
            "employment_status": row[6],
            "email": row[7],
            "department_name": row[8],
        }

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def get_faculty_by_org(org_id):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT f.user_id, f.employee_code, f.designation,
                   f.employment_status,
                   u.email, d.name AS department_name
            FROM v3.faculty f
            JOIN v3.users u ON u.user_id = f.user_id
            JOIN v3.departments d ON d.department_id = f.home_department_id
            WHERE f.organization_id = %s
            ORDER BY d.name, f.employee_code
        """, (org_id,))

        rows = cursor.fetchall()
        return [
            {
                "user_id": r[0],
                "employee_code": r[1],
                "designation": r[2],
                "employment_status": r[3],
                "email": r[4],
                "department_name": r[5],
            }
            for r in rows
        ]

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def get_faculty_by_department(department_id):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT f.user_id, f.employee_code, f.designation,
                   f.employment_status, u.email
            FROM v3.faculty f
            JOIN v3.users u ON u.user_id = f.user_id
            WHERE f.home_department_id = %s
            ORDER BY f.employee_code
        """, (department_id,))

        rows = cursor.fetchall()
        return [
            {
                "user_id": r[0],
                "employee_code": r[1],
                "designation": r[2],
                "employment_status": r[3],
                "email": r[4],
            }
            for r in rows
        ]

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)
