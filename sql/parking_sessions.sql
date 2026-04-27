DROP TABLE IF EXISTS parking_sessions;

CREATE TABLE parking_sessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL,
    lot_id VARCHAR(50) NOT NULL,
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