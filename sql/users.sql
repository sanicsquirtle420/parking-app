DROP TABLE IF EXISTS users ;

CREATE TABLE users (
    user_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(150),
    password_hash TEXT NOT NULL,
    role ENUM('student', 'faculty', 'visitor', 'admin') DEFAULT 'student'
);