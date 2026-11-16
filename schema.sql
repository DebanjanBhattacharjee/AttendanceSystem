-- Students
CREATE TABLE IF NOT EXISTS students (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL UNIQUE COLLATE NOCASE,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- Attendance: one row per student per date
CREATE TABLE IF NOT EXISTS attendance (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL REFERENCES students(id),
    date       TEXT NOT NULL,  -- YYYY-MM-DD
    status     TEXT NOT NULL CHECK (status IN ('Present', 'Absent')),
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    UNIQUE (student_id, date)
);

CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(date);

-- Records are read-only: the database itself refuses edits and deletes,
-- so even a bug in the app (or a manual SQL query) cannot change saved data.
CREATE TRIGGER IF NOT EXISTS attendance_no_update
BEFORE UPDATE ON attendance
BEGIN
    SELECT RAISE(ABORT, 'Attendance records cannot be changed.');
END;

CREATE TRIGGER IF NOT EXISTS attendance_no_delete
BEFORE DELETE ON attendance
BEGIN
    SELECT RAISE(ABORT, 'Attendance records cannot be deleted.');
END;

CREATE TRIGGER IF NOT EXISTS students_no_update
BEFORE UPDATE ON students
BEGIN
    SELECT RAISE(ABORT, 'Student records cannot be changed.');
END;

CREATE TRIGGER IF NOT EXISTS students_no_delete
BEFORE DELETE ON students
BEGIN
    SELECT RAISE(ABORT, 'Student records cannot be deleted.');
END;
