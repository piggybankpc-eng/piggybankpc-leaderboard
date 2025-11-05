-- Add Intel 13th/14th Gen CPU tracking column
-- Run this with: sqlite3 instance/leaderboard.db < migrations/add_intel_cpu_tracking.sql

-- Add column to track Intel 13th/14th gen CPUs (for degradation warnings)
ALTER TABLE submissions ADD COLUMN intel_13_14_gen_cpu BOOLEAN DEFAULT 0;

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_intel_13_14_gen_cpu ON submissions(intel_13_14_gen_cpu);
