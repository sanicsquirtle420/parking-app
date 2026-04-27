DROP TABLE IF EXISTS tickets ;

CREATE TABLE tickets (
    ticket_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL,
    issue_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    amount DECIMAL(10,2) NOT NULL,
    status ENUM('Unpaid', 'Pending', 'Paid') DEFAULT 'Unpaid',
    description VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);