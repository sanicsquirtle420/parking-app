-- Seed permits, demo users, and active permit assignments.

INSERT INTO permits
    (permit_id, permit_name, description, duration_days, display_color_hex, is_active, sort_order)
VALUES
    ('FS', 'Faculty', '365 days - Faculty and staff permit for faculty zones shown on the campus map.', 365, '#F83EFF', TRUE, 10),
    ('CB', 'Commuter Blue', '365 days - Commuter Blue permit for student blue lots shown on the campus map.', 365, '#008BD7', TRUE, 20),
    ('CR', 'Commuter Red', '365 days - Commuter Red permit for student red lots shown on the campus map.', 365, '#FF0000', TRUE, 30),
    ('CW', 'Campus Walk', '365 days - Campus Walk residential permit for campus walk housing lots.', 365, '#0CFF00', TRUE, 40),
    ('RE', 'Residential East', '365 days - Residential East permit for east residential lots shown on the map.', 365, '#4AFFFA', TRUE, 50),
    ('RC', 'Residential Central', '365 days - Residential Central permit for central residential lots shown on the map.', 365, '#895129', TRUE, 60),
    ('RNW', 'Residential Northwest', '365 days - Residential Northwest permit for northwest residential lots shown on the map.', 365, '#00A308', TRUE, 70),
    ('RS', 'Residential South', '365 days - Residential South permit for south residential lots shown on the map.', 365, '#FFAA3B', TRUE, 80),
    ('VSD', 'Visitor', '30 days - Visitor permit for guest and timed visitor parking on the map.', 30, '#6B0096', TRUE, 90);

INSERT INTO users
    (user_id, first_name, last_name, email, password_hash, role, is_active)
VALUES
    ('admin001', 'Maya', 'Admin', 'admin@parking.test', '$2y$12$YTMwnbsKUuPOxeuZ3/NY1..4HNBsEcScnOPPKKyYfE45LkBoEfH.G', 'admin', TRUE),
    ('fac001', 'Felix', 'Stafford', 'faculty@parking.test', '$2y$12$UkT2x3XMDafedQp6WjL.jOH6YvJjl1xl2xjr7Pa4EzIq4AuuCaszi', 'faculty', TRUE),
    ('cb001', 'Brooke', 'Blue', 'commuter.blue@parking.test', '$2y$12$LSckAhAQzd/.cFibOuQ6ZO/kDkmI.zSFmIB/nm6d.YRguqi3L4GDK', 'student', TRUE),
    ('cr001', 'Riley', 'Red', 'commuter.red@parking.test', '$2y$12$HnuKmPGSDDFq60GNp38R3es2Wa3PM91FgTfLr.kQOFkaMIVm14aJG', 'student', TRUE),
    ('cw001', 'Casey', 'Walker', 'campus.walk@parking.test', '$2y$12$ntGf5k0MIT/jlD4Ik0tZDO8olEPpqgldHMCObuMBJ3oXcvcRkZ/uy', 'student', TRUE),
    ('re001', 'Eden', 'East', 'res.east@parking.test', '$2y$12$m952xTig9d7ZcJBFdUnG2eVSwLmnZ84yekfnuBczMGn3DLbNa6Nye', 'student', TRUE),
    ('rc001', 'Chris', 'Central', 'res.central@parking.test', '$2y$12$vZFQ9TmT6vlgin9ZAvYfTenQiVyZD/Burd4j0YfVjNBgx1Du7KQz.', 'student', TRUE),
    ('rnw001', 'Nora', 'Northwest', 'res.northwest@parking.test', '$2y$12$4Ej6nyuATWv.gWERlfrg5.vd3WORWyKnepqwGU42lFqb95AmG7n4W', 'student', TRUE),
    ('rs001', 'Sage', 'South', 'res.south@parking.test', '$2y$12$H.SMIjnNYwUYY0rjJOYj.e6P8jSMtGnbc.dQLE/vDr.j627y.Mesi', 'student', TRUE),
    ('vis001', 'Vera', 'Guest', 'visitor@parking.test', '$2y$12$nLJXG5lxcEOelIXXHiwvx.xu7isDCtEHmK5r/BYBodX2P.MWH1roy', 'visitor', TRUE);

INSERT INTO user_permits
    (user_id, permit_id, issued_date, expiration_date, status, assigned_by, note)
VALUES
    ('fac001', 'FS', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 365 DAY), 'active', 'seed', 'Seeded compatibility account'),
    ('cb001', 'CB', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 365 DAY), 'active', 'seed', 'Seeded compatibility account'),
    ('cr001', 'CR', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 365 DAY), 'active', 'seed', 'Seeded compatibility account'),
    ('cw001', 'CW', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 365 DAY), 'active', 'seed', 'Seeded compatibility account'),
    ('re001', 'RE', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 365 DAY), 'active', 'seed', 'Seeded compatibility account'),
    ('rc001', 'RC', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 365 DAY), 'active', 'seed', 'Seeded compatibility account'),
    ('rnw001', 'RNW', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 365 DAY), 'active', 'seed', 'Seeded compatibility account'),
    ('rs001', 'RS', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 365 DAY), 'active', 'seed', 'Seeded compatibility account'),
    ('vis001', 'VSD', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 30 DAY), 'active', 'seed', 'Seeded compatibility account');
