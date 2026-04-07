-- ============================================================
-- SmartAttendanceAI – Database Schema
-- Khalsa College of Engineering and Technology
-- ============================================================
CREATE DATABASE IF NOT EXISTS smart_attendance_db
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE smart_attendance_db;

-- ── Teachers ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS Teachers (
    teacher_id  INT          AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(150) NOT NULL UNIQUE,
    password    CHAR(64)     NOT NULL COMMENT 'SHA-256 hex digest',
    subject     VARCHAR(100),
    created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

-- Default admin (password: admin123)
INSERT IGNORE INTO Teachers (name, email, password, subject)
VALUES ('Admin Teacher', 'admin@kcet.ac.in', SHA2('admin123',256), 'Administration');

-- ── Students ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS Students (
    student_id   VARCHAR(20)  PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    class        VARCHAR(50)  NOT NULL,
    email        VARCHAR(150),
    parent_email VARCHAR(150),
    photo_path   VARCHAR(255),
    enrolled_at  DATE         DEFAULT (CURDATE()),
    is_active    TINYINT(1)   DEFAULT 1
);

-- ── Attendance ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS Attendance (
    id          INT    AUTO_INCREMENT PRIMARY KEY,
    student_id  VARCHAR(20) NOT NULL,
    date        DATE        NOT NULL,
    time        TIME        NOT NULL,
    subject     VARCHAR(100) DEFAULT 'General',
    status      ENUM('Present','Absent','Late') DEFAULT 'Present',
    marked_by   ENUM('AI','Manual')             DEFAULT 'AI',
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE,
    INDEX idx_date    (date),
    INDEX idx_student (student_id),
    INDEX idx_subject (subject)
);

-- ── Alert Logs ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS AlertLogs (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL,
    alert_type VARCHAR(50),
    sent_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message    TEXT,
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE
);