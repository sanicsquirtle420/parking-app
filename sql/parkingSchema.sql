DROP TABLES IF EXISTS permit_types, users, parking_lots, parking_rules;

CREATE TABLE permits (
    permit_id VARCHAR(5) PRIMARY KEY,
    permit_name VARCHAR(50) NOT NULL
);

CREATE TABLE users (
    user_id CHAR(8) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    password_hash TEXT NOT NULL,
    permit_id VARCHAR(5),
    FOREIGN KEY (permit_id) REFERENCES permits(permit_id)
);

CREATE TABLE parking_lots (
    lot_id INT AUTO_INCREMENT PRIMARY KEY,
    lot_name VARCHAR(100) NOT NULL,
    permit_id VARCHAR(5),
    capacity INT,
    FOREIGN KEY (permit_id) REFERENCES permits(permit_id)
);