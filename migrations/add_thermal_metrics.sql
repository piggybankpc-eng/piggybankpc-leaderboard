-- Add thermal metrics columns to submissions table
-- Run this with: sqlite3 instance/leaderboard.db < migrations/add_thermal_metrics.sql

-- GPU thermal metrics
ALTER TABLE submissions ADD COLUMN gpu_temp_min FLOAT;
ALTER TABLE submissions ADD COLUMN gpu_util_min FLOAT;
ALTER TABLE submissions ADD COLUMN gpu_util_avg FLOAT;
ALTER TABLE submissions ADD COLUMN gpu_util_max FLOAT;

-- CPU thermal metrics
ALTER TABLE submissions ADD COLUMN cpu_temp_min FLOAT;
ALTER TABLE submissions ADD COLUMN cpu_temp_avg FLOAT;
ALTER TABLE submissions ADD COLUMN cpu_temp_max FLOAT;
ALTER TABLE submissions ADD COLUMN cpu_util_min FLOAT;
ALTER TABLE submissions ADD COLUMN cpu_util_avg FLOAT;
ALTER TABLE submissions ADD COLUMN cpu_util_max FLOAT;
