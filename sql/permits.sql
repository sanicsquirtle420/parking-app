DROP TABLE IF EXISTS permits;

CREATE TABLE permits (
    permit_id VARCHAR(5) PRIMARY KEY,
    permit_name VARCHAR(50) NOT NULL,
    description VARCHAR(200)
);

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