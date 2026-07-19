from database.connection import get_connection, return_connection
import psycopg2


def create_period(org_id, label, semester_number, academic_year, start_date, end_date):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO v3.academic_periods
                (organization_id, label, semester_number, academic_year, start_date, end_date)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING period_id
        """, (org_id, label, semester_number, academic_year, start_date, end_date))

        row = cursor.fetchone()
        if not row:
            raise ValueError("Failed to create academic period")

        period_id = row[0]
        conn.commit()

        return {
            "period_id": period_id,
            "message": "Academic period created successfully"
        }

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise ValueError("An academic period with this label already exists for this organization")

    except psycopg2.errors.CheckViolation:
        conn.rollback()
        raise ValueError("Invalid dates: end_date must be after start_date and semester_number must be > 0")

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def get_periods_by_org(org_id):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT period_id, label, semester_number, academic_year,
                   start_date, end_date, is_current
            FROM v3.academic_periods
            WHERE organization_id = %s
            ORDER BY start_date DESC
        """, (org_id,))

        rows = cursor.fetchall()
        return [
            {
                "period_id": r[0],
                "label": r[1],
                "semester_number": r[2],
                "academic_year": r[3],
                "start_date": str(r[4]),
                "end_date": str(r[5]),
                "is_current": r[6],
            }
            for r in rows
        ]

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def set_current_period(org_id, period_id):
    """Deactivate all periods for the org, then activate the target one."""
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        # Deactivate all periods for this org
        cursor.execute("""
            UPDATE v3.academic_periods
            SET is_current = FALSE
            WHERE organization_id = %s AND is_current = TRUE
        """, (org_id,))

        # Activate the target period
        cursor.execute("""
            UPDATE v3.academic_periods
            SET is_current = TRUE
            WHERE period_id = %s AND organization_id = %s
            RETURNING period_id, label
        """, (period_id, org_id))

        row = cursor.fetchone()
        if not row:
            raise ValueError("Academic period not found in this organization")

        conn.commit()

        return {
            "period_id": row[0],
            "label": row[1],
            "message": "Period activated successfully"
        }

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)


def get_current_period(org_id):
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT period_id, label, semester_number, academic_year,
                   start_date, end_date
            FROM v3.academic_periods
            WHERE organization_id = %s AND is_current = TRUE
        """, (org_id,))

        row = cursor.fetchone()
        if not row:
            return None

        return {
            "period_id": row[0],
            "label": row[1],
            "semester_number": row[2],
            "academic_year": row[3],
            "start_date": str(row[4]),
            "end_date": str(row[5]),
        }

    finally:
        if cursor:
            cursor.close()
        return_connection(conn)
