

DROP TABLE IF EXISTS parking_sessions;
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS parking_occupancy_log;
DROP TABLE IF EXISTS parking_rules;
DROP TABLE IF EXISTS user_permits;
DROP TABLE IF EXISTS parking_lots;
DROP TABLE IF EXISTS permits;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'student',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_users_email (email),
    KEY idx_users_role (role),
    CONSTRAINT chk_users_role
        CHECK (role IN ('student', 'faculty', 'admin', 'visitor')),
    CONSTRAINT chk_users_user_id
        CHECK (user_id REGEXP '^(stu|fac|adm|vis)[0-9]{3,}$')
);

CREATE TABLE permits (
    permit_id VARCHAR(10) PRIMARY KEY,
    permit_name VARCHAR(100) NOT NULL,
    description VARCHAR(200),
    duration_days INT NOT NULL DEFAULT 365,
    display_color_hex CHAR(7),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    sort_order INT NOT NULL DEFAULT 0,
    UNIQUE KEY uq_permits_name (permit_name)
);

CREATE TABLE parking_lots (
    lot_id INT AUTO_INCREMENT PRIMARY KEY,
    polygon_id VARCHAR(50) NOT NULL,
    lot_name VARCHAR(255) NOT NULL,
    zone VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    capacity INT NOT NULL,
    current_occupancy INT NOT NULL DEFAULT 0,
    ev_charger_count INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_parking_lots_polygon (polygon_id),
    KEY idx_parking_lots_name (lot_name),
    KEY idx_parking_lots_zone (zone)
);

CREATE TABLE user_permits (
    assignment_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL,
    permit_id VARCHAR(10) NOT NULL,
    issued_date DATETIME NOT NULL,
    expiration_date DATETIME NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    assigned_by VARCHAR(20),
    note VARCHAR(255),
    UNIQUE KEY uq_user_permits_user (user_id),
    KEY idx_user_permits_permit (permit_id),
    CONSTRAINT fk_user_permits_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_user_permits_permit
        FOREIGN KEY (permit_id) REFERENCES permits(permit_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE parking_rules (
    rule_id INT AUTO_INCREMENT PRIMARY KEY,
    lot_id INT NOT NULL,
    permit_id VARCHAR(10) NOT NULL,
    day_of_week VARCHAR(50) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_allowed BOOLEAN NOT NULL DEFAULT TRUE,
    rule_source VARCHAR(20) NOT NULL DEFAULT 'seed',
    KEY idx_parking_rules_lot (lot_id),
    KEY idx_parking_rules_permit (permit_id),
    CONSTRAINT fk_parking_rules_lot
        FOREIGN KEY (lot_id) REFERENCES parking_lots(lot_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_parking_rules_permit
        FOREIGN KEY (permit_id) REFERENCES permits(permit_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE parking_occupancy_log (
    log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    lot_id INT NOT NULL,
    recorded_at DATETIME NOT NULL,
    occupancy INT NOT NULL,
    ev_chargers_in_use INT NOT NULL DEFAULT 0,
    source VARCHAR(20) NOT NULL DEFAULT 'seed',
    KEY idx_parking_occupancy_log_lot_time (lot_id, recorded_at),
    CONSTRAINT fk_parking_occupancy_log_lot
        FOREIGN KEY (lot_id) REFERENCES parking_lots(lot_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE tickets (
    ticket_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL,
    lot_id INT,
    permit_id VARCHAR(10),
    issue_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Unpaid',
    description VARCHAR(255),
    offense_type VARCHAR(100),
    resolved_date DATETIME,
    KEY idx_tickets_user (user_id),
    KEY idx_tickets_status (status),
    CONSTRAINT fk_tickets_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_tickets_lot
        FOREIGN KEY (lot_id) REFERENCES parking_lots(lot_id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_tickets_permit
        FOREIGN KEY (permit_id) REFERENCES permits(permit_id)
        ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE parking_sessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL,
    lot_id INT NOT NULL,
    polygon_id VARCHAR(50),
    lot_name VARCHAR(100),
    start_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME DEFAULT NULL,
    KEY idx_parking_sessions_user_active (user_id, end_time),
    KEY idx_parking_sessions_lot (lot_id),
    CONSTRAINT fk_parking_sessions_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_parking_sessions_lot
        FOREIGN KEY (lot_id) REFERENCES parking_lots(lot_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);
