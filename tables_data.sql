
INSERT INTO permits (permit_id, permit_name, description) VALUES
('RC',  'Residential Central',   'Central campus residential areas'),
('RW',  'Residential West',      'West campus residential areas'),
('S',   'Student Commuter',      'General student commuter lots'),
('FC',  'Faculty/Staff Central', 'Faculty and staff central campus'),
('FW',  'Faculty/Staff West',    'Faculty and staff west campus'),
('PK',  'Park-N-Ride',           'Remote lots with shuttle service'),
('V',   'Visitor',               'Short-term visitor parking'),
('ADA', 'Accessible',            'ADA accessible parking spaces');


-- ============================================
-- users (10 rows)
-- 4 students, 3 faculty, 2 visitors, 1 admin
-- ============================================
INSERT INTO users (user_id, first_name, last_name, email, password_hash, role) VALUES
('stu001', 'John',    'Doe',      'jdoe@go.olemiss.edu',      'hashed_pw_001', 'student'),
('stu002', 'Maria',   'Garcia',   'mgarcia@go.olemiss.edu',   'hashed_pw_002', 'student'),
('stu003', 'Tyler',   'Brown',    'tbrown@go.olemiss.edu',    'hashed_pw_003', 'student'),
('stu004', 'Aisha',   'Patel',    'apatel@go.olemiss.edu',    'hashed_pw_004', 'student'),
('fac001', 'Robert',  'Smith',    'rsmith@olemiss.edu',       'hashed_pw_005', 'faculty'),
('fac002', 'Linda',   'Johnson',  'ljohnson@olemiss.edu',     'hashed_pw_006', 'faculty'),
('fac003', 'James',   'Williams', 'jwilliams@olemiss.edu',    'hashed_pw_007', 'faculty'),
('vis001', 'Sarah',   'Miller',   'smiller@gmail.com',        'hashed_pw_008', 'visitor'),
('vis002', 'David',   'Lee',      'dlee@yahoo.com',           'hashed_pw_009', 'visitor'),
('adm001', 'Karen',   'Davis',    'kdavis@olemiss.edu',       'hashed_pw_010', 'admin');


-- ============================================
-- user_permits (10 rows)
-- Note: fac003 has TWO permits (FC + ADA)
-- Note: vis001 has a single-day permit
-- ============================================
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


-- ============================================
-- parking_lots (12 rows)
-- Real Ole Miss coordinates for map markers
-- ============================================
INSERT INTO parking_lots (lot_name, latitude, longitude, capacity, current_occupancy, ev_charger_count) VALUES
('Stockard/Martin Lot',       34.3655, -89.5365, 150,  112, 0),
('Residential West Lot',      34.3620, -89.5420, 200,   85, 0),
('Coliseum Commuter Lot',     34.3600, -89.5340, 400,  370, 4),
('Turner Center Lot',         34.3675, -89.5395, 120,   98, 2),
('South Lot 6 (Park-N-Ride)', 34.3550, -89.5380, 600,  210, 6),
('Lyceum Circle Faculty Lot', 34.3648, -89.5385,  80,   74, 0),
('Student Union Lot',         34.3630, -89.5370, 100,   91, 2),
('Kennon Observatory Lot',    34.3690, -89.5350,  60,   22, 0),
('Law School Lot',            34.3615, -89.5310,  90,   67, 0),
('Visitor Center Lot',        34.3660, -89.5400,  50,   38, 0),
('Vaught-Hemingway Lot',      34.3580, -89.5345, 500,  145, 8),
('Jackson Avenue Garage',     34.3640, -89.5355, 350,  320, 12);


-- ============================================
-- parking_rules (54 rows)
-- The rule engine: each row = one eligibility rule
-- ============================================

-- Lot 1: Stockard/Martin Lot (capacity 150)
-- RC all day weekdays; S, FC after 5pm weekdays; open weekends
INSERT INTO parking_rules (lot_id, permit_id, day_of_week, start_time, end_time) VALUES
(1, 'RC',  'Mon,Tue,Wed,Thu,Fri', '00:00:00', '23:59:59'),
(1, 'S',   'Mon,Tue,Wed,Thu,Fri', '17:00:00', '23:59:59'),
(1, 'FC',  'Mon,Tue,Wed,Thu,Fri', '17:00:00', '23:59:59'),
(1, 'RC',  'Sat,Sun',             '00:00:00', '23:59:59'),
(1, 'S',   'Sat,Sun',             '00:00:00', '23:59:59'),
(1, 'FC',  'Sat,Sun',             '00:00:00', '23:59:59');

-- Lot 2: Residential West Lot (capacity 200)
-- RW all day weekdays; S after 5pm weekdays; open weekends
INSERT INTO parking_rules (lot_id, permit_id, day_of_week, start_time, end_time) VALUES
(2, 'RW',  'Mon,Tue,Wed,Thu,Fri', '00:00:00', '23:59:59'),
(2, 'S',   'Mon,Tue,Wed,Thu,Fri', '17:00:00', '23:59:59'),
(2, 'RW',  'Sat,Sun',             '00:00:00', '23:59:59'),
(2, 'S',   'Sat,Sun',             '00:00:00', '23:59:59');

-- Lot 3: Coliseum Commuter Lot (capacity 400)
-- S, FC, FW weekdays 7am-5pm; S open weekends
INSERT INTO parking_rules (lot_id, permit_id, day_of_week, start_time, end_time) VALUES
(3, 'S',   'Mon,Tue,Wed,Thu,Fri', '07:00:00', '17:00:00'),
(3, 'FC',  'Mon,Tue,Wed,Thu,Fri', '07:00:00', '17:00:00'),
(3, 'FW',  'Mon,Tue,Wed,Thu,Fri', '07:00:00', '17:00:00'),
(3, 'S',   'Sat,Sun',             '00:00:00', '23:59:59');

-- Lot 4: Turner Center Lot (capacity 120)
-- FC weekdays 7am-5pm; S after 5pm; open weekends
INSERT INTO parking_rules (lot_id, permit_id, day_of_week, start_time, end_time) VALUES
(4, 'FC',  'Mon,Tue,Wed,Thu,Fri', '07:00:00', '17:00:00'),
(4, 'S',   'Mon,Tue,Wed,Thu,Fri', '17:00:00', '23:59:59'),
(4, 'FC',  'Sat,Sun',             '00:00:00', '23:59:59'),
(4, 'S',   'Sat,Sun',             '00:00:00', '23:59:59');

-- Lot 5: South Lot 6 Park-N-Ride (capacity 600)
-- PK, S weekdays 6am-10pm; open weekends for PK, S, RC
INSERT INTO parking_rules (lot_id, permit_id, day_of_week, start_time, end_time) VALUES
(5, 'PK',  'Mon,Tue,Wed,Thu,Fri', '06:00:00', '22:00:00'),
(5, 'S',   'Mon,Tue,Wed,Thu,Fri', '06:00:00', '22:00:00'),
(5, 'PK',  'Sat,Sun',             '00:00:00', '23:59:59'),
(5, 'S',   'Sat,Sun',             '00:00:00', '23:59:59'),
(5, 'RC',  'Sat,Sun',             '00:00:00', '23:59:59');

-- Lot 6: Lyceum Circle Faculty Lot (capacity 80)
-- FC, FW weekdays 7am-5pm; S after 5pm; FC, S weekends
INSERT INTO parking_rules (lot_id, permit_id, day_of_week, start_time, end_time) VALUES
(6, 'FC',  'Mon,Tue,Wed,Thu,Fri', '07:00:00', '17:00:00'),
(6, 'FW',  'Mon,Tue,Wed,Thu,Fri', '07:00:00', '17:00:00'),
(6, 'S',   'Mon,Tue,Wed,Thu,Fri', '17:00:00', '23:59:59'),
(6, 'FC',  'Sat,Sun',             '00:00:00', '23:59:59'),
(6, 'S',   'Sat,Sun',             '00:00:00', '23:59:59');

-- Lot 7: Student Union Lot (capacity 100)
-- FC, V weekdays 7am-5pm; S after 5pm; S weekends
INSERT INTO parking_rules (lot_id, permit_id, day_of_week, start_time, end_time) VALUES
(7, 'FC',  'Mon,Tue,Wed,Thu,Fri', '07:00:00', '17:00:00'),
(7, 'S',   'Mon,Tue,Wed,Thu,Fri', '17:00:00', '23:59:59'),
(7, 'V',   'Mon,Tue,Wed,Thu,Fri', '07:00:00', '17:00:00'),
(7, 'S',   'Sat,Sun',             '00:00:00', '23:59:59');

-- Lot 8: Kennon Observatory Lot (capacity 60)
-- FC weekdays 7am-5pm; S after 5pm; FC weekends
INSERT INTO parking_rules (lot_id, permit_id, day_of_week, start_time, end_time) VALUES
(8, 'FC',  'Mon,Tue,Wed,Thu,Fri', '07:00:00', '17:00:00'),
(8, 'S',   'Mon,Tue,Wed,Thu,Fri', '17:00:00', '23:59:59'),
(8, 'FC',  'Sat,Sun',             '00:00:00', '23:59:59');

-- Lot 9: Law School Lot (capacity 90)
-- FC, S weekdays 7am-5pm; S weekends
INSERT INTO parking_rules (lot_id, permit_id, day_of_week, start_time, end_time) VALUES
(9, 'FC',  'Mon,Tue,Wed,Thu,Fri', '07:00:00', '17:00:00'),
(9, 'S',   'Mon,Tue,Wed,Thu,Fri', '07:00:00', '17:00:00'),
(9, 'S',   'Sat,Sun',             '00:00:00', '23:59:59');

-- Lot 10: Visitor Center Lot (capacity 50)
-- V weekdays 7am-5pm; S after 5pm; S, V weekends
INSERT INTO parking_rules (lot_id, permit_id, day_of_week, start_time, end_time) VALUES
(10, 'V',  'Mon,Tue,Wed,Thu,Fri', '07:00:00', '17:00:00'),
(10, 'S',  'Mon,Tue,Wed,Thu,Fri', '17:00:00', '23:59:59'),
(10, 'S',  'Sat,Sun',             '00:00:00', '23:59:59'),
(10, 'V',  'Sat,Sun',             '00:00:00', '23:59:59');

-- Lot 11: Vaught-Hemingway Lot (capacity 500)
-- S, PK weekdays 7am-5pm; S weekends
INSERT INTO parking_rules (lot_id, permit_id, day_of_week, start_time, end_time) VALUES
(11, 'S',   'Mon,Tue,Wed,Thu,Fri', '07:00:00', '17:00:00'),
(11, 'PK',  'Mon,Tue,Wed,Thu,Fri', '07:00:00', '17:00:00'),
(11, 'S',   'Sat,Sun',             '00:00:00', '23:59:59');

-- Lot 12: Jackson Avenue Garage (capacity 350)
-- All permit types weekdays 6am-10pm; S, FC, V, ADA weekends
INSERT INTO parking_rules (lot_id, permit_id, day_of_week, start_time, end_time) VALUES
(12, 'FC',  'Mon,Tue,Wed,Thu,Fri', '06:00:00', '22:00:00'),
(12, 'FW',  'Mon,Tue,Wed,Thu,Fri', '06:00:00', '22:00:00'),
(12, 'S',   'Mon,Tue,Wed,Thu,Fri', '06:00:00', '22:00:00'),
(12, 'RC',  'Mon,Tue,Wed,Thu,Fri', '06:00:00', '22:00:00'),
(12, 'V',   'Mon,Tue,Wed,Thu,Fri', '06:00:00', '22:00:00'),
(12, 'ADA', 'Mon,Tue,Wed,Thu,Fri', '06:00:00', '22:00:00'),
(12, 'S',   'Sat,Sun',             '00:00:00', '23:59:59'),
(12, 'FC',  'Sat,Sun',             '00:00:00', '23:59:59'),
(12, 'V',   'Sat,Sun',             '00:00:00', '23:59:59'),
(12, 'ADA', 'Sat,Sun',             '00:00:00', '23:59:59');


-- ============================================
-- parking_occupancy_log (54 rows)
-- Simulated readings every 2 hours
-- Monday, March 17, 2026 for 6 key lots
-- ============================================

-- Lot 3: Coliseum Commuter Lot (capacity 400, 4 EV chargers)
INSERT INTO parking_occupancy_log (lot_id, recorded_at, occupancy, ev_chargers_in_use) VALUES
(3, '2026-03-17 06:00:00',  45, 0),
(3, '2026-03-17 08:00:00', 280, 2),
(3, '2026-03-17 10:00:00', 385, 4),
(3, '2026-03-17 12:00:00', 370, 4),
(3, '2026-03-17 14:00:00', 360, 3),
(3, '2026-03-17 16:00:00', 290, 2),
(3, '2026-03-17 18:00:00', 120, 1),
(3, '2026-03-17 20:00:00',  55, 0),
(3, '2026-03-17 22:00:00',  15, 0);

-- Lot 12: Jackson Avenue Garage (capacity 350, 12 EV chargers)
INSERT INTO parking_occupancy_log (lot_id, recorded_at, occupancy, ev_chargers_in_use) VALUES
(12, '2026-03-17 06:00:00',  30, 1),
(12, '2026-03-17 08:00:00', 210, 6),
(12, '2026-03-17 10:00:00', 330, 11),
(12, '2026-03-17 12:00:00', 320, 12),
(12, '2026-03-17 14:00:00', 310, 10),
(12, '2026-03-17 16:00:00', 260, 8),
(12, '2026-03-17 18:00:00', 140, 4),
(12, '2026-03-17 20:00:00',  70, 2),
(12, '2026-03-17 22:00:00',  20, 0);

-- Lot 6: Lyceum Circle Faculty Lot (capacity 80, 0 EV chargers)
INSERT INTO parking_occupancy_log (lot_id, recorded_at, occupancy, ev_chargers_in_use) VALUES
(6, '2026-03-17 06:00:00',   5, 0),
(6, '2026-03-17 08:00:00',  62, 0),
(6, '2026-03-17 10:00:00',  78, 0),
(6, '2026-03-17 12:00:00',  74, 0),
(6, '2026-03-17 14:00:00',  76, 0),
(6, '2026-03-17 16:00:00',  58, 0),
(6, '2026-03-17 18:00:00',  20, 0),
(6, '2026-03-17 20:00:00',   8, 0),
(6, '2026-03-17 22:00:00',   2, 0);

-- Lot 5: South Lot 6 Park-N-Ride (capacity 600, 6 EV chargers)
INSERT INTO parking_occupancy_log (lot_id, recorded_at, occupancy, ev_chargers_in_use) VALUES
(5, '2026-03-17 06:00:00',  20, 0),
(5, '2026-03-17 08:00:00', 130, 1),
(5, '2026-03-17 10:00:00', 210, 2),
(5, '2026-03-17 12:00:00', 195, 2),
(5, '2026-03-17 14:00:00', 185, 1),
(5, '2026-03-17 16:00:00', 140, 1),
(5, '2026-03-17 18:00:00',  65, 0),
(5, '2026-03-17 20:00:00',  25, 0),
(5, '2026-03-17 22:00:00',  10, 0);

-- Lot 11: Vaught-Hemingway Lot (capacity 500, 8 EV chargers)
INSERT INTO parking_occupancy_log (lot_id, recorded_at, occupancy, ev_chargers_in_use) VALUES
(11, '2026-03-17 06:00:00',  15, 0),
(11, '2026-03-17 08:00:00', 105, 2),
(11, '2026-03-17 10:00:00', 180, 4),
(11, '2026-03-17 12:00:00', 165, 5),
(11, '2026-03-17 14:00:00', 155, 3),
(11, '2026-03-17 16:00:00', 110, 2),
(11, '2026-03-17 18:00:00',  45, 1),
(11, '2026-03-17 20:00:00',  18, 0),
(11, '2026-03-17 22:00:00',   5, 0);

-- Lot 7: Student Union Lot (capacity 100, 2 EV chargers)
INSERT INTO parking_occupancy_log (lot_id, recorded_at, occupancy, ev_chargers_in_use) VALUES
(7, '2026-03-17 06:00:00',   8, 0),
(7, '2026-03-17 08:00:00',  55, 1),
(7, '2026-03-17 10:00:00',  92, 2),
(7, '2026-03-17 12:00:00',  95, 2),
(7, '2026-03-17 14:00:00',  88, 2),
(7, '2026-03-17 16:00:00',  70, 1),
(7, '2026-03-17 18:00:00',  35, 0),
(7, '2026-03-17 20:00:00',  12, 0),
(7, '2026-03-17 22:00:00',   4, 0);