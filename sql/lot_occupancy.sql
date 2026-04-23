DROP TABLE IF EXISTS parking_occupancy_log;

CREATE TABLE parking_occupancy_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    lot_id VARCHAR(50) NOT NULL,
    recorded_at DATETIME NOT NULL,
    occupancy INT NOT NULL,
    ev_chargers_in_use INT NOT NULL DEFAULT 0,
    FOREIGN KEY (lot_id) REFERENCES parking_lots(lot_id)
);

-- DATA
-- Commuter Red: Jackson Avenue Lot
INSERT INTO parking_occupancy_log (lot_id, recorded_at, occupancy, ev_chargers_in_use) VALUES
("com_rd11", '2026-03-17 06:00:00',  20, 0),
("com_rd11", '2026-03-17 08:00:00', 130, 1),
("com_rd11", '2026-03-17 10:00:00', 210, 2),
("com_rd11", '2026-03-17 12:00:00', 195, 2),
("com_rd11", '2026-03-17 14:00:00', 185, 1),
("com_rd11", '2026-03-17 16:00:00', 140, 1),
("com_rd11", '2026-03-17 18:00:00',  65, 0),
("com_rd11", '2026-03-17 20:00:00',  25, 0),
("com_rd11", '2026-03-17 22:00:00',  10, 0);

-- Residential Northwest: Stockard / Martin Lot
INSERT INTO parking_occupancy_log (lot_id, recorded_at, occupancy, ev_chargers_in_use) VALUES
("res_nw3", '2026-03-17 06:00:00',  15, 0),
("res_nw3", '2026-03-17 08:00:00', 105, 2),
("res_nw3", '2026-03-17 10:00:00', 180, 4),
("res_nw3", '2026-03-17 12:00:00', 165, 5),
("res_nw3", '2026-03-17 14:00:00', 155, 3),
("res_nw3", '2026-03-17 16:00:00', 110, 2),
("res_nw3", '2026-03-17 18:00:00',  45, 1),
("res_nw3", '2026-03-17 20:00:00',  18, 0),
("res_nw3", '2026-03-17 22:00:00',   5, 0);

-- Visitor: Martindale-Cole On Street Lot
INSERT INTO parking_occupancy_log (lot_id, recorded_at, occupancy, ev_chargers_in_use) VALUES
("vis3", '2026-03-17 06:00:00',   8, 0),
("vis3", '2026-03-17 08:00:00',  55, 1),
("vis3", '2026-03-17 10:00:00',  92, 2),
("vis3", '2026-03-17 12:00:00',  95, 2),
("vis3", '2026-03-17 14:00:00',  88, 2),
("vis3", '2026-03-17 16:00:00',  70, 1),
("vis3", '2026-03-17 18:00:00',  35, 0),
("vis3", '2026-03-17 20:00:00',  12, 0),
("vis3", '2026-03-17 22:00:00',   4, 0);