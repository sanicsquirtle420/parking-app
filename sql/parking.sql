DROP TABLE IF EXISTS parking_occupancy_log;
DROP TABLE IF EXISTS parking_rules;
DROP TABLE IF EXISTS user_permits;
DROP TABLE IF EXISTS parking_lots;
DROP TABLE IF EXISTS permits;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS tickets;

CREATE TABLE permits (
    permit_id VARCHAR(5) PRIMARY KEY,
    permit_name VARCHAR(50) NOT NULL,
    description VARCHAR(200)
);

CREATE TABLE users (
    user_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(150),
    password_hash TEXT NOT NULL,
    role ENUM('student', 'faculty', 'visitor', 'admin') DEFAULT 'student'
);

CREATE TABLE user_permits (
    user_id VARCHAR(20),
    permit_id VARCHAR(5),
    issued_date DATE,
    expiration_date DATE,
    PRIMARY KEY (user_id, permit_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (permit_id) REFERENCES permits(permit_id)
);

CREATE TABLE parking_lots (
    lot_id INT AUTO_INCREMENT PRIMARY KEY,
    lot_name VARCHAR(100) NOT NULL,
    latitude DECIMAL(8,6),
    longitude DECIMAL(9,6),
    capacity INT NOT NULL,
    current_occupancy INT NOT NULL DEFAULT 0,
    ev_charger_count INT NOT NULL DEFAULT 0
);

CREATE TABLE parking_rules (
    rule_id INT AUTO_INCREMENT PRIMARY KEY,
    lot_id INT NOT NULL,
    permit_id VARCHAR(5) NOT NULL,
    day_of_week SET('Mon','Tue','Wed','Thu','Fri','Sat','Sun') NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_allowed BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (lot_id) REFERENCES parking_lots(lot_id),
    FOREIGN KEY (permit_id) REFERENCES permits(permit_id)
);

CREATE TABLE parking_occupancy_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    lot_id INT NOT NULL,
    recorded_at DATETIME NOT NULL,
    occupancy INT NOT NULL,
    ev_chargers_in_use INT NOT NULL DEFAULT 0,
    FOREIGN KEY (lot_id) REFERENCES parking_lots(lot_id)
);

CREATE TABLE tickets (
    ticket_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL,
    issue_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    amount DECIMAL(10,2) NOT NULL,
    status ENUM('Unpaid', 'Pending', 'Paid') DEFAULT 'Unpaid',
    description VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);