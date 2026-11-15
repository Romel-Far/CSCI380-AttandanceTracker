CREATE SCHEMA Attandance_Tracker;

USE Attandance_Tracker;

CREATE TABLE Students (
    student_id int,
    student_name VARCHAR(225),
    student_email VARCHAR(255),
    grade_level INT,
    Accommodation BOOLEAN,
    is_attending BOOL,
    PRIMARY KEY (student_id)
);

CREATE TABLE Professors (
    professor_id INT,
    professor_name VARCHAR(255),
    professor_email VARCHAR(255),
    professor_password VARCHAR(255),
    department VARCHAR(255),
    is_teaching BOOL,
    PRIMARY KEY (professor_id)
);

CREATE TABLE Registrar (
    registrar_id INT AUTO_INCREMENT,
    registrar_name VARCHAR(255),
    registrar_password VARCHAR(255),
    PRIMARY KEY (registrar_id)
);


CREATE TABLE Classes (
    class_id INT AUTO_INCREMENT,
    class_name VARCHAR(255),
    class_level INT,
    size INT,
    professor_id INT,
    PRIMARY KEY (class_id),
    FOREIGN KEY (professor_id) REFERENCES Professors(professor_id) ON DELETE CASCADE
);

CREATE TABLE Attandance (
    Attendance_id INT AUTO_INCREMENT,
    student_id INT, 
    student_confirmation BOOL,
    professor_confirmation BOOL,
    PRIMARY KEY (Attendance_id),
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE
);


-- =========================================
-- 1. STUDENTS TABLE
-- =========================================

INSERT INTO Students
(student_id, student_name, student_email, grade_level, Accommodation, is_attending)
VALUES
(1, 'James Wilson', 'james.wilson@school.edu', 9, FALSE, TRUE),
(2, 'Sophia Martinez', 'sophia.martinez@school.edu', 10, TRUE, TRUE),
(3, 'Ethan Thompson', 'ethan.thompson@school.edu', 11, FALSE, TRUE),
(4, 'Olivia Johnson', 'olivia.johnson@school.edu', 12, FALSE, TRUE),
(5, 'Noah Williams', 'noah.williams@school.edu', 9, TRUE, TRUE),
(6, 'Ava Brown', 'ava.brown@school.edu', 10, FALSE, FALSE),
(7, 'Liam Davis', 'liam.davis@school.edu', 11, FALSE, TRUE);


-- =========================================
-- 2. PROFESSORS TABLE
-- =========================================

INSERT INTO Professors
(professor_id, professor_name, professor_email, professor_password, department, is_teaching)
VALUES
(1, 'Dr. Michael Anderson', 'manderson@school.edu', 'DemoPass123!', 'Mathematics', TRUE),
(2, 'Prof. Emily Carter', 'ecarter@school.edu', 'DemoPass123!', 'English', TRUE),
(3, 'Dr. Robert Garcia', 'rgarcia@school.edu', 'DemoPass123!', 'Science', TRUE),
(4, 'Prof. Jessica Miller', 'jmiller@school.edu', 'DemoPass123!', 'History', TRUE),
(5, 'Dr. Daniel Wilson', 'dwilson@school.edu', 'DemoPass123!', 'Computer Science', TRUE),
(6, 'Prof. Sarah Moore', 'smoore@school.edu', 'DemoPass123!', 'Physical Education', FALSE),
(7, 'Dr. David Taylor', 'dtaylor@school.edu', 'DemoPass123!', 'Art', TRUE);


-- =========================================
-- 3. REGISTRAR TABLE
-- =========================================

INSERT INTO Registrar
(registrar_name, registrar_password)
VALUES
('Amanda Lewis', 'RegistrarDemo123!'),
('Christopher Hall', 'RegistrarDemo123!'),
('Rachel Adams', 'RegistrarDemo123!'),
('Matthew Scott', 'RegistrarDemo123!'),
('Lauren Baker', 'RegistrarDemo123!'),
('Andrew Nelson', 'RegistrarDemo123!'),
('Victoria Clark', 'RegistrarDemo123!');


-- =========================================
-- 4. CLASSES TABLE
-- =========================================

INSERT INTO Classes
(class_name, class_level, size, professor_id)
VALUES
('Algebra I', 9, 25, 1),
('English Literature', 10, 28, 2),
('Biology', 11, 24, 3),
('World History', 12, 22, 4),
('Introduction to Programming', 11, 20, 5),
('Physical Education', 9, 30, 6),
('Digital Art', 10, 18, 7);














