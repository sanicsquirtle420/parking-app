INSERT INTO permits (permit_id, permit_name, description) VALUES
/*residential*/
('RE', 'Residential East', 'East campus residential areas'),
('RW', 'Residential West', 'West campus residential areas'),
('RNW', 'Residential Northwest', 'Northwest campus residential areas'),
('RC', 'Residential Central', 'Central campus residential areas'),
('RS', 'Residential South', 'South campus residential areas'),
('CW', 'Campus Walk', 'Campus walk permit area'),
('RG', 'Residential Garage', 'Garage parking available to all residential zones except Campus Walk'),
('RON', 'Residential Overflow North', 'Overflow parking for residential students located at the Jackson Avenue Center (JAC)'),
('ROS', 'Residential Overflow South', 'Overflow parking for residential students located at the South Campus Recreation Center (SCRC)'),

/*Commuters*/
('CB', 'Commuter Blue', 'Commuter parking closer to the core of campus and academic buildings; higher cost option'),
('CR', 'Commuter Red', 'Commuter parking farther from campus center or at satellite locations like Jackson Avenue Center and South Oxford Center; lower cost option with shuttle service available Monday–Friday 7:00am–7:00pm'),

/*Faculty*/
('FS', 'Faculty/Staff', 'Access to Faculty/Staff, Commuter Blue, and Commuter Red lots'),
('PG', 'Pavilion Garage Reserved', 'Reserved numbered space in Pavilion Garage'),
('FR', 'Faculty/Staff Reserved', 'Reserved parking space for faculty/staff with limited access to other zones');

/*Visitors*/
('VSD', 'Visitor Daily', 'Visitor Daily Parking Pass'),
('VSM', 'Visitor Monthly', 'Visitor Monthly Parking Pass'),
('VSY', 'Visitor Yearly', 'Visitor Yearly Parking Pass');

INSERT INTO users (user_id, first_name, last_name, email, password_hash, role) VALUES
('dtaylor', 'Drew', 'Taylor', 'dtaylor@go.olemiss.edu', '123abc', 'student'),
('jsmith1', 'Jordan', 'Smith', 'jsmith1@go.olemiss.edu', 'abc123', 'student'),
('ajohnson2', 'Avery', 'Johnson', 'ajohnson2@olemiss.edu', 'faculty1', 'faculty'),
('tbrown3', 'Taylor', 'Brown', 'tbrown3@gmail.com', 'visitor', 'visitor'),
('mdavis4', 'Morgan', 'Davis', 'mdavis4@olemiss.edu', 'admin123', 'admin');

INSERT INTO user_permits (user_id, permit_id, issued_date, expiration_date) VALUES
('dtaylor', 'RE', '2025-08-01', '2026-08-15'),
('jsmith1', 'CB', '2025-08-01', '2026-08-15'),  
('ajohnson2', 'FS', '2025-08-01', '2026-08-15'),
('tbrown3', 'VSD', '2025-08-01', '2026-08-15'), 
('mdavis4', 'FS', '2025-08-01', '2026-08-15'); 

INSERT INTO parking_lots (lot_name, latitude, longitude, capacity, current_occupancy, ev_charger_count) VALUES
-- Residential Northwest
('North Stockard/Martin Lot', 34.371300, -89.537300, 120, 45, 2),
('South Stockard/Martin Lot', 34.370100, -89.537200, 90, 30, 1),

-- Residential Central
('Crosby Lot', 34.370800, -89.534700, 110, 60, 2),
('Womens Terrace Lot', 34.368600, -89.534800, 80, 50, 1),

-- Commuter Red
('Jackson Avenue Lot', 34.370200, -89.546800, 200, 120, 4),
('Jackson Annex Lot', 34.369100, -89.546400, 100, 70, 2),
('South Campus Recreation Lot', 34.354100, -89.542200, 180, 90, 6),
('South Lot', 34.356900, -89.535500, 250, 150, 3),
('East Track Lot', 34.358500, -89.536200, 140, 85, 2),

-- Commuter Blue
('Ford Center East Lot', 34.365800, -89.527700, 130, 100, 2),
('Ford Center West Lot', 34.366400, -89.528200, 160, 130, 3),
('Music Building Lot', 34.363400, -89.530400, 120, 95, 2),
('Baseball North Lot', 34.363200, -89.528800, 90, 60, 1),
('Law School Lot', 34.363700, -89.543000, 110, 75, 2),

-- Residential Garage
('Residential Garage', 34.369700, -89.540200, 300, 210, 10);

INSERT INTO parking_rules (lot_id, permit_id, day_of_week, start_time, end_time, is_allowed) VALUES
-- Residential Northwest & Central → RNW, RC
(1, 'RNW', 'Mon,Tue,Wed,Thu,Fri,Sat,Sun', '00:00:00', '23:59:59', TRUE),
(2, 'RNW', 'Mon,Tue,Wed,Thu,Fri,Sat,Sun', '00:00:00', '23:59:59', TRUE),
(3, 'RC',  'Mon,Tue,Wed,Thu,Fri,Sat,Sun', '00:00:00', '23:59:59', TRUE),
(4, 'RC',  'Mon,Tue,Wed,Thu,Fri,Sat,Sun', '00:00:00', '23:59:59', TRUE),

-- Commuter Red
(5, 'CR', 'Mon,Tue,Wed,Thu,Fri', '07:00:00', '19:00:00', TRUE),
(6, 'CR', 'Mon,Tue,Wed,Thu,Fri', '07:00:00', '19:00:00', TRUE),
(7, 'CR', 'Mon,Tue,Wed,Thu,Fri', '07:00:00', '19:00:00', TRUE),
(8, 'CR', 'Mon,Tue,Wed,Thu,Fri', '07:00:00', '19:00:00', TRUE),
(9, 'CR', 'Mon,Tue,Wed,Thu,Fri', '07:00:00', '19:00:00', TRUE),

-- Commuter Blue
(10, 'CB', 'Mon,Tue,Wed,Thu,Fri', '07:00:00', '19:00:00', TRUE),
(11, 'CB', 'Mon,Tue,Wed,Thu,Fri', '07:00:00', '19:00:00', TRUE),
(12, 'CB', 'Mon,Tue,Wed,Thu,Fri', '07:00:00', '19:00:00', TRUE),
(13, 'CB', 'Mon,Tue,Wed,Thu,Fri', '07:00:00', '19:00:00', TRUE),
(14, 'CB', 'Mon,Tue,Wed,Thu,Fri', '07:00:00', '19:00:00', TRUE),

-- Residential Garage
(15, 'RG', 'Mon,Tue,Wed,Thu,Fri,Sat,Sun', '00:00:00', '23:59:59', TRUE);

INSERT INTO parking_occupancy_log (lot_id, recorded_at, occupancy, ev_chargers_in_use) VALUES
(1, '2026-04-01 08:00:00', 50, 1),
(5, '2026-04-01 10:00:00', 140, 3),
(7, '2026-04-01 12:00:00', 110, 4),
(10,'2026-04-01 09:00:00', 115, 2),
(15,'2026-04-01 14:00:00', 230, 7);

INSERT INTO tickets (user_id, amount, status, description) VALUES
('jsmith1', 50.00, 'Unpaid', 'Parked in Commuter Blue without permit'),
('ajohnson2', 25.00, 'Paid', 'Expired permit'),
('tbrown3', 75.00, 'Pending', 'Unauthorized residential parking'),
('mdavis4', 0.00, 'Paid', 'Warning - no violation fee');