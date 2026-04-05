-- ============================================================================
-- GRADWISE v3 SCHEMA
-- Generated: 2026-04-05
-- PostgreSQL 15+
-- ============================================================================
-- Changes from v2:
--   • GENERATED ALWAYS AS IDENTITY on all PKs (consistent auto-generation)
--   • NOT NULL on every FK column
--   • TIMESTAMPTZ everywhere instead of TIMESTAMP
--   • CHECK constraints on all enum-like TEXT columns
--   • organization_id denormalized onto core tables for RLS / tenant isolation
--   • course_offerings references academic_periods instead of raw ints
--   • Explicit ON DELETE / ON UPDATE on every FK
--   • updated_at + auto-update trigger on mutable tables
--   • Proper UNIQUE constraints (roll_no, employee_code, course_offerings, etc.)
--   • Essential indexes for query performance
-- ============================================================================

-- ========================
-- SCHEMA
-- ========================
CREATE SCHEMA IF NOT EXISTS v3;

-- ========================
-- UTILITY: auto-update trigger for updated_at
-- ========================
CREATE OR REPLACE FUNCTION v3.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ========================
-- ENUM TYPES
-- ========================
CREATE TYPE v3.account_status      AS ENUM ('ACTIVE', 'SUSPENDED', 'DELETED');
CREATE TYPE v3.membership_role     AS ENUM ('PENDING', 'ADMIN', 'FACULTY', 'STUDENT');
CREATE TYPE v3.membership_status   AS ENUM ('ACTIVE', 'INACTIVE', 'INVITED');
CREATE TYPE v3.program_level       AS ENUM ('UG', 'PG', 'PHD', 'DIPLOMA', 'CERTIFICATE');
CREATE TYPE v3.academic_status     AS ENUM ('ACTIVE', 'GRADUATED', 'DROPPED', 'SUSPENDED', 'ON_LEAVE');
CREATE TYPE v3.employment_status   AS ENUM ('ACTIVE', 'RESIGNED', 'RETIRED', 'ON_LEAVE', 'TERMINATED');
CREATE TYPE v3.enrollment_status   AS ENUM ('ENROLLED', 'DROPPED', 'COMPLETED', 'WITHDRAWN');
CREATE TYPE v3.assessment_type     AS ENUM ('QUIZ', 'MIDTERM', 'FINAL', 'ASSIGNMENT', 'PROJECT', 'LAB', 'PRESENTATION', 'OTHER');
CREATE TYPE v3.attendance_status   AS ENUM ('PRESENT', 'ABSENT', 'LATE', 'EXCUSED');

-- ========================
-- TABLES
-- ========================

-- 1. Users
CREATE TABLE v3.users (
    user_id         INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email           TEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,
    account_status  v3.account_status NOT NULL DEFAULT 'ACTIVE',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON v3.users
    FOR EACH ROW EXECUTE FUNCTION v3.set_updated_at();

-- 2. Organizations
CREATE TABLE v3.organizations (
    organization_id    INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name               TEXT NOT NULL,
    invite_key         TEXT NOT NULL UNIQUE,
    invite_expires_at  TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '72 hours'),
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_organizations_updated_at
    BEFORE UPDATE ON v3.organizations
    FOR EACH ROW EXECUTE FUNCTION v3.set_updated_at();

-- 3. Organization Memberships
CREATE TABLE v3.organization_memberships (
    membership_id    INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id          INTEGER NOT NULL,
    organization_id  INTEGER NOT NULL,
    role             v3.membership_role NOT NULL DEFAULT 'PENDING',
    status           v3.membership_status NOT NULL DEFAULT 'ACTIVE',
    joined_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (user_id, organization_id)
);

CREATE TRIGGER trg_org_memberships_updated_at
    BEFORE UPDATE ON v3.organization_memberships
    FOR EACH ROW EXECUTE FUNCTION v3.set_updated_at();

-- 4. Academic Periods (semesters / terms)
CREATE TABLE v3.academic_periods (
    period_id        INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    organization_id  INTEGER NOT NULL,
    label            VARCHAR(50) NOT NULL,             -- e.g. "Fall 2025", "Spring 2026"
    semester_number  INTEGER NOT NULL,                 -- 1, 2, 3 (summer), etc.
    academic_year    VARCHAR(9) NOT NULL,              -- "2025-2026"
    start_date       DATE NOT NULL,
    end_date         DATE NOT NULL,
    is_current       BOOLEAN NOT NULL DEFAULT FALSE,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_period_dates CHECK (end_date > start_date),
    CONSTRAINT chk_semester_number CHECK (semester_number > 0),
    UNIQUE (organization_id, label)
);

CREATE TRIGGER trg_academic_periods_updated_at
    BEFORE UPDATE ON v3.academic_periods
    FOR EACH ROW EXECUTE FUNCTION v3.set_updated_at();

-- 5. Departments
CREATE TABLE v3.departments (
    department_id    INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    organization_id  INTEGER NOT NULL,
    name             TEXT NOT NULL,
    code             TEXT,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (organization_id, name),
    UNIQUE (organization_id, code)
);

CREATE TRIGGER trg_departments_updated_at
    BEFORE UPDATE ON v3.departments
    FOR EACH ROW EXECUTE FUNCTION v3.set_updated_at();

-- 6. Programs
CREATE TABLE v3.programs (
    program_id       INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    department_id    INTEGER NOT NULL,
    organization_id  INTEGER NOT NULL,      -- denormalized for tenant isolation
    name             TEXT NOT NULL,
    level            v3.program_level NOT NULL,
    duration_years   INTEGER NOT NULL,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_duration CHECK (duration_years > 0 AND duration_years <= 10),
    UNIQUE (department_id, name)
);

CREATE TRIGGER trg_programs_updated_at
    BEFORE UPDATE ON v3.programs
    FOR EACH ROW EXECUTE FUNCTION v3.set_updated_at();

-- 7. Courses (scoped to organization)
CREATE TABLE v3.courses (
    course_id        INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    organization_id  INTEGER NOT NULL,
    course_code      TEXT NOT NULL,
    course_name      TEXT NOT NULL,
    credits          INTEGER NOT NULL,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_credits CHECK (credits > 0 AND credits <= 20),
    UNIQUE (organization_id, course_code)
);

CREATE TRIGGER trg_courses_updated_at
    BEFORE UPDATE ON v3.courses
    FOR EACH ROW EXECUTE FUNCTION v3.set_updated_at();

-- 8. Program–Course mapping
CREATE TABLE v3.program_courses (
    program_id  INTEGER NOT NULL,
    course_id   INTEGER NOT NULL,
    semester    INTEGER NOT NULL,
    is_core     BOOLEAN NOT NULL DEFAULT TRUE,

    PRIMARY KEY (program_id, course_id),
    CONSTRAINT chk_pc_semester CHECK (semester > 0)
);

-- 9. Students
CREATE TABLE v3.students (
    user_id          INTEGER PRIMARY KEY,           -- 1:1 with users
    organization_id  INTEGER NOT NULL,              -- denormalized for tenant isolation
    program_id       INTEGER NOT NULL,
    roll_no          TEXT NOT NULL,
    admission_year   INTEGER NOT NULL,
    academic_status  v3.academic_status NOT NULL DEFAULT 'ACTIVE',
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_admission_year CHECK (admission_year >= 2000 AND admission_year <= 2100),
    UNIQUE (program_id, roll_no)
);

CREATE TRIGGER trg_students_updated_at
    BEFORE UPDATE ON v3.students
    FOR EACH ROW EXECUTE FUNCTION v3.set_updated_at();

-- 10. Faculty
CREATE TABLE v3.faculty (
    user_id              INTEGER PRIMARY KEY,       -- 1:1 with users
    organization_id      INTEGER NOT NULL,          -- denormalized for tenant isolation
    employee_code        TEXT NOT NULL,
    home_department_id   INTEGER NOT NULL,
    designation          TEXT,
    joining_date         DATE,
    employment_status    v3.employment_status NOT NULL DEFAULT 'ACTIVE',
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (organization_id, employee_code)
);

CREATE TRIGGER trg_faculty_updated_at
    BEFORE UPDATE ON v3.faculty
    FOR EACH ROW EXECUTE FUNCTION v3.set_updated_at();

-- 11. Course Offerings (now references academic_periods)
CREATE TABLE v3.course_offerings (
    offering_id      INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    organization_id  INTEGER NOT NULL,              -- denormalized for tenant isolation
    course_id        INTEGER NOT NULL,
    faculty_user_id  INTEGER NOT NULL,
    period_id        INTEGER NOT NULL,              -- replaces raw semester + academic_year
    section          TEXT NOT NULL DEFAULT 'A',
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (course_id, period_id, section)
);

CREATE TRIGGER trg_course_offerings_updated_at
    BEFORE UPDATE ON v3.course_offerings
    FOR EACH ROW EXECUTE FUNCTION v3.set_updated_at();

-- 12. Enrollments
CREATE TABLE v3.enrollments (
    enrollment_id      INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    student_user_id    INTEGER NOT NULL,
    offering_id        INTEGER NOT NULL,
    status             v3.enrollment_status NOT NULL DEFAULT 'ENROLLED',
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (student_user_id, offering_id)
);

CREATE TRIGGER trg_enrollments_updated_at
    BEFORE UPDATE ON v3.enrollments
    FOR EACH ROW EXECUTE FUNCTION v3.set_updated_at();

-- 13. Assessments
CREATE TABLE v3.assessments (
    assessment_id    INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    offering_id      INTEGER NOT NULL,
    type             v3.assessment_type NOT NULL,
    title            TEXT,                          -- e.g. "Quiz 1", "Midterm Exam"
    max_marks        INTEGER NOT NULL,
    weightage        NUMERIC(5, 2) NOT NULL,        -- percentage, e.g. 25.00
    assessment_date  DATE,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_max_marks CHECK (max_marks > 0),
    CONSTRAINT chk_weightage CHECK (weightage > 0 AND weightage <= 100)
);

CREATE TRIGGER trg_assessments_updated_at
    BEFORE UPDATE ON v3.assessments
    FOR EACH ROW EXECUTE FUNCTION v3.set_updated_at();

-- 14. Assessment Scores
CREATE TABLE v3.assessment_scores (
    score_id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    assessment_id     INTEGER NOT NULL,
    student_user_id   INTEGER NOT NULL,
    marks             NUMERIC(7, 2) NOT NULL,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_marks_positive CHECK (marks >= 0),
    UNIQUE (assessment_id, student_user_id)
);

CREATE TRIGGER trg_assessment_scores_updated_at
    BEFORE UPDATE ON v3.assessment_scores
    FOR EACH ROW EXECUTE FUNCTION v3.set_updated_at();

-- 15. Attendance Sessions
CREATE TABLE v3.attendance_sessions (
    session_id    INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    offering_id   INTEGER NOT NULL,
    session_date  DATE NOT NULL,
    topic         TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
    -- no updated_at: sessions are immutable once created
);

-- 16. Attendance Records
CREATE TABLE v3.attendance_records (
    record_id         INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    session_id        INTEGER NOT NULL,
    student_user_id   INTEGER NOT NULL,
    status            v3.attendance_status NOT NULL,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (session_id, student_user_id)
);

CREATE TRIGGER trg_attendance_records_updated_at
    BEFORE UPDATE ON v3.attendance_records
    FOR EACH ROW EXECUTE FUNCTION v3.set_updated_at();

-- 17. Final Results (1:1 with enrollment)
CREATE TABLE v3.final_results (
    enrollment_id  INTEGER PRIMARY KEY,             -- PK = FK, enforces 1:1
    final_grade    TEXT NOT NULL,
    grade_points   NUMERIC(4, 2) NOT NULL,
    published_at   TIMESTAMPTZ,

    CONSTRAINT chk_grade_points CHECK (grade_points >= 0 AND grade_points <= 10)
);


-- ========================
-- FOREIGN KEYS
-- ========================

-- organization_memberships
ALTER TABLE v3.organization_memberships
    ADD CONSTRAINT fk_om_user
    FOREIGN KEY (user_id) REFERENCES v3.users(user_id) ON DELETE CASCADE;

ALTER TABLE v3.organization_memberships
    ADD CONSTRAINT fk_om_organization
    FOREIGN KEY (organization_id) REFERENCES v3.organizations(organization_id) ON DELETE CASCADE;

-- academic_periods
ALTER TABLE v3.academic_periods
    ADD CONSTRAINT fk_ap_organization
    FOREIGN KEY (organization_id) REFERENCES v3.organizations(organization_id) ON DELETE CASCADE;

-- departments
ALTER TABLE v3.departments
    ADD CONSTRAINT fk_dept_organization
    FOREIGN KEY (organization_id) REFERENCES v3.organizations(organization_id) ON DELETE CASCADE;

-- programs
ALTER TABLE v3.programs
    ADD CONSTRAINT fk_prog_department
    FOREIGN KEY (department_id) REFERENCES v3.departments(department_id) ON DELETE CASCADE;

ALTER TABLE v3.programs
    ADD CONSTRAINT fk_prog_organization
    FOREIGN KEY (organization_id) REFERENCES v3.organizations(organization_id) ON DELETE CASCADE;

-- courses
ALTER TABLE v3.courses
    ADD CONSTRAINT fk_course_organization
    FOREIGN KEY (organization_id) REFERENCES v3.organizations(organization_id) ON DELETE CASCADE;

-- program_courses
ALTER TABLE v3.program_courses
    ADD CONSTRAINT fk_pc_program
    FOREIGN KEY (program_id) REFERENCES v3.programs(program_id) ON DELETE CASCADE;

ALTER TABLE v3.program_courses
    ADD CONSTRAINT fk_pc_course
    FOREIGN KEY (course_id) REFERENCES v3.courses(course_id) ON DELETE CASCADE;

-- students
ALTER TABLE v3.students
    ADD CONSTRAINT fk_stu_user
    FOREIGN KEY (user_id) REFERENCES v3.users(user_id) ON DELETE CASCADE;

ALTER TABLE v3.students
    ADD CONSTRAINT fk_stu_program
    FOREIGN KEY (program_id) REFERENCES v3.programs(program_id) ON DELETE RESTRICT;

ALTER TABLE v3.students
    ADD CONSTRAINT fk_stu_organization
    FOREIGN KEY (organization_id) REFERENCES v3.organizations(organization_id) ON DELETE CASCADE;

-- faculty
ALTER TABLE v3.faculty
    ADD CONSTRAINT fk_fac_user
    FOREIGN KEY (user_id) REFERENCES v3.users(user_id) ON DELETE CASCADE;

ALTER TABLE v3.faculty
    ADD CONSTRAINT fk_fac_department
    FOREIGN KEY (home_department_id) REFERENCES v3.departments(department_id) ON DELETE RESTRICT;

ALTER TABLE v3.faculty
    ADD CONSTRAINT fk_fac_organization
    FOREIGN KEY (organization_id) REFERENCES v3.organizations(organization_id) ON DELETE CASCADE;

-- course_offerings
ALTER TABLE v3.course_offerings
    ADD CONSTRAINT fk_co_course
    FOREIGN KEY (course_id) REFERENCES v3.courses(course_id) ON DELETE CASCADE;

ALTER TABLE v3.course_offerings
    ADD CONSTRAINT fk_co_faculty
    FOREIGN KEY (faculty_user_id) REFERENCES v3.faculty(user_id) ON DELETE RESTRICT;

ALTER TABLE v3.course_offerings
    ADD CONSTRAINT fk_co_period
    FOREIGN KEY (period_id) REFERENCES v3.academic_periods(period_id) ON DELETE RESTRICT;

ALTER TABLE v3.course_offerings
    ADD CONSTRAINT fk_co_organization
    FOREIGN KEY (organization_id) REFERENCES v3.organizations(organization_id) ON DELETE CASCADE;

-- enrollments
ALTER TABLE v3.enrollments
    ADD CONSTRAINT fk_enr_student
    FOREIGN KEY (student_user_id) REFERENCES v3.students(user_id) ON DELETE CASCADE;

ALTER TABLE v3.enrollments
    ADD CONSTRAINT fk_enr_offering
    FOREIGN KEY (offering_id) REFERENCES v3.course_offerings(offering_id) ON DELETE CASCADE;

-- assessments
ALTER TABLE v3.assessments
    ADD CONSTRAINT fk_asm_offering
    FOREIGN KEY (offering_id) REFERENCES v3.course_offerings(offering_id) ON DELETE CASCADE;

-- assessment_scores
ALTER TABLE v3.assessment_scores
    ADD CONSTRAINT fk_score_assessment
    FOREIGN KEY (assessment_id) REFERENCES v3.assessments(assessment_id) ON DELETE CASCADE;

ALTER TABLE v3.assessment_scores
    ADD CONSTRAINT fk_score_student
    FOREIGN KEY (student_user_id) REFERENCES v3.students(user_id) ON DELETE CASCADE;

-- attendance_sessions
ALTER TABLE v3.attendance_sessions
    ADD CONSTRAINT fk_attsess_offering
    FOREIGN KEY (offering_id) REFERENCES v3.course_offerings(offering_id) ON DELETE CASCADE;

-- attendance_records
ALTER TABLE v3.attendance_records
    ADD CONSTRAINT fk_attrec_session
    FOREIGN KEY (session_id) REFERENCES v3.attendance_sessions(session_id) ON DELETE CASCADE;

ALTER TABLE v3.attendance_records
    ADD CONSTRAINT fk_attrec_student
    FOREIGN KEY (student_user_id) REFERENCES v3.students(user_id) ON DELETE CASCADE;

-- final_results
ALTER TABLE v3.final_results
    ADD CONSTRAINT fk_result_enrollment
    FOREIGN KEY (enrollment_id) REFERENCES v3.enrollments(enrollment_id) ON DELETE CASCADE;


-- ========================
-- INDEXES
-- ========================

-- Users
CREATE INDEX idx_users_email              ON v3.users (email);
CREATE INDEX idx_users_account_status     ON v3.users (account_status);

-- Organization Memberships
CREATE INDEX idx_om_user_id               ON v3.organization_memberships (user_id);
CREATE INDEX idx_om_organization_id       ON v3.organization_memberships (organization_id);
CREATE INDEX idx_om_role                  ON v3.organization_memberships (organization_id, role);

-- Academic Periods
CREATE UNIQUE INDEX idx_ap_org_current     ON v3.academic_periods (organization_id)
    WHERE is_current = TRUE;

-- Departments
CREATE INDEX idx_dept_organization        ON v3.departments (organization_id);

-- Programs
CREATE INDEX idx_prog_department          ON v3.programs (department_id);
CREATE INDEX idx_prog_organization        ON v3.programs (organization_id);

-- Courses
CREATE INDEX idx_course_organization      ON v3.courses (organization_id);
CREATE INDEX idx_course_code              ON v3.courses (organization_id, course_code);

-- Students
CREATE INDEX idx_stu_program              ON v3.students (program_id);
CREATE INDEX idx_stu_organization         ON v3.students (organization_id);
CREATE INDEX idx_stu_status               ON v3.students (organization_id, academic_status);

-- Faculty
CREATE INDEX idx_fac_department           ON v3.faculty (home_department_id);
CREATE INDEX idx_fac_organization         ON v3.faculty (organization_id);

-- Course Offerings
CREATE INDEX idx_co_course                ON v3.course_offerings (course_id);
CREATE INDEX idx_co_faculty               ON v3.course_offerings (faculty_user_id);
CREATE INDEX idx_co_period                ON v3.course_offerings (period_id);
CREATE INDEX idx_co_organization          ON v3.course_offerings (organization_id);

-- Enrollments
CREATE INDEX idx_enr_student              ON v3.enrollments (student_user_id);
CREATE INDEX idx_enr_offering             ON v3.enrollments (offering_id);
CREATE INDEX idx_enr_status               ON v3.enrollments (offering_id, status);

-- Assessments
CREATE INDEX idx_asm_offering             ON v3.assessments (offering_id);

-- Assessment Scores
CREATE INDEX idx_score_assessment         ON v3.assessment_scores (assessment_id);
CREATE INDEX idx_score_student            ON v3.assessment_scores (student_user_id);

-- Attendance Sessions
CREATE INDEX idx_attsess_offering         ON v3.attendance_sessions (offering_id);
CREATE INDEX idx_attsess_date             ON v3.attendance_sessions (offering_id, session_date);

-- Attendance Records
CREATE INDEX idx_attrec_session           ON v3.attendance_records (session_id);
CREATE INDEX idx_attrec_student           ON v3.attendance_records (student_user_id);

-- Final Results (PK covers the only column needing an index)

-- ========================
-- DONE
-- ========================
