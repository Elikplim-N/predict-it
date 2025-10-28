-- FRESH START: Complete Supabase Schema for ML Competition Platform
-- Run this entire script in Supabase SQL Editor

-- Drop everything first (clean slate)
DROP VIEW IF EXISTS leaderboard_view CASCADE;
DROP TABLE IF EXISTS submissions CASCADE;
DROP TABLE IF EXISTS ground_truth CASCADE;
DROP TABLE IF EXISTS settings CASCADE;
DROP TABLE IF EXISTS admin CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create users table (students)
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    student_index TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create admin table
CREATE TABLE admin (
    id BIGSERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create ground_truth table (stores CSV as text)
CREATE TABLE ground_truth (
    id BIGSERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    file_data TEXT NOT NULL,
    upload_date TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Create submissions table
CREATE TABLE submissions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    rmse DOUBLE PRECISION,
    submission_date TIMESTAMPTZ DEFAULT NOW()
);

-- Create settings table
CREATE TABLE settings (
    id BIGSERIAL PRIMARY KEY,
    setting_key TEXT UNIQUE NOT NULL,
    setting_value TEXT
);

-- Create indexes for performance
CREATE INDEX idx_submissions_user_id ON submissions(user_id);
CREATE INDEX idx_submissions_rmse ON submissions(rmse);
CREATE INDEX idx_ground_truth_active ON ground_truth(is_active);
CREATE INDEX idx_users_student_index ON users(student_index);

-- Create leaderboard view
CREATE VIEW leaderboard_view AS
SELECT 
    users.student_index,
    users.name,
    MIN(submissions.rmse) as best_rmse,
    COUNT(submissions.id) as submission_count,
    MAX(submissions.submission_date) as last_submission
FROM users
LEFT JOIN submissions ON users.id = submissions.user_id
WHERE submissions.rmse IS NOT NULL
GROUP BY users.id, users.student_index, users.name
ORDER BY best_rmse ASC;

-- Insert default admin (you'll update the password hash later)
INSERT INTO admin (username, password_hash)
VALUES ('isaaceinst3in', 'TEMP_HASH_UPDATE_THIS')
ON CONFLICT (username) DO NOTHING;

-- Insert default settings
INSERT INTO settings (setting_key, setting_value)
VALUES 
    ('id_column', 'id'),
    ('value_column', 'value')
ON CONFLICT (setting_key) DO UPDATE 
SET setting_value = EXCLUDED.setting_value;

-- Enable Row Level Security (optional but recommended)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE ground_truth ENABLE ROW LEVEL SECURITY;
ALTER TABLE settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin ENABLE ROW LEVEL SECURITY;

-- Create permissive policies (API handles auth)
CREATE POLICY "Allow all for service role" ON users FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON submissions FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON ground_truth FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON settings FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON admin FOR ALL USING (true);

-- Verify tables created
SELECT 'Tables created successfully!' as status;
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;
