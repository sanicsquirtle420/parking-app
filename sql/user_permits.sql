DROP TABLE IF EXISTS user_permits ;

CREATE TABLE user_permits (
    user_id VARCHAR(20),
    permit_id VARCHAR(5),
    issued_date DATE,
    expiration_date DATE,
    PRIMARY KEY (user_id, permit_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (permit_id) REFERENCES permits(permit_id)
);

INSERT INTO user_permits (user_id, permit_id, issued_date, expiration_date) VALUES
('stu001', 'RC',  '2025-08-20', '2026-05-15'),
('stu002', 'S',   '2025-08-20', '2026-05-15'),
('stu003', 'RW',  '2025-08-20', '2026-05-15'),
('stu004', 'PK',  '2025-08-20', '2026-05-15'),
('fac001', 'FC',  '2025-08-01', '2026-07-31'),
('fac002', 'FW',  '2025-08-01', '2026-07-31'),
('fac003', 'FC',  '2025-08-01', '2026-07-31'),
('fac003', 'ADA', '2025-08-01', '2026-07-31'),
('vis001', 'V',   '2026-03-10', '2026-03-10'),
('vis002', 'V',   '2026-03-15', '2026-03-16');