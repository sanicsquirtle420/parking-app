INSERT INTO permits (permit_id, permit_name) VALUES
('RC', 'Residential Central');

INSERT INTO users (user_id, first_name, last_name, password_hash, permit_id) VALUES
('student1', 'John', 'Doe', 'hashedpassword123', 'RC');

INSERT INTO parking_lots (lot_name, permit_id, capacity) VALUES
('Residential Central Lot', 'RC', 200);