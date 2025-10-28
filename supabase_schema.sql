-- Supabase PostgreSQL Schema for ML Competition Platform (Serverless)

-- Users table (students)
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    student_index TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Admin table
CREATE TABLE IF NOT EXISTS admin (
    id BIGSERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Ground truth table - stores CSV data directly in file_data column
CREATE TABLE IF NOT EXISTS ground_truth (
    id BIGSERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    file_data TEXT NOT NULL,  -- CSV content stored as text
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Submissions table
CREATE TABLE IF NOT EXISTS submissions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    filename TEXT NOT NULL,
    rmse DOUBLE PRECISION,
    submission_date TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Settings table for column configuration
CREATE TABLE IF NOT EXISTS settings (
    id BIGSERIAL PRIMARY KEY,
    setting_key TEXT UNIQUE NOT NULL,
    setting_value TEXT
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_submissions_user_id ON submissions(user_id);
CREATE INDEX IF NOT EXISTS idx_submissions_rmse ON submissions(rmse);
CREATE INDEX IF NOT EXISTS idx_ground_truth_active ON ground_truth(is_active);

-- Create leaderboard view for efficient queries
CREATE OR REPLACE VIEW leaderboard_view AS
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

-- Insert default admin user (change password in production!)
INSERT INTO admin (username, password_hash)
VALUES ('isaaceinst3in', 'scrypt:32768:8:1$YOUR_HASHED_PASSWORD_HERE')
ON CONFLICT (username) DO NOTHING;

-- Insert default column settings
INSERT INTO settings (setting_key, setting_value)
VALUES 
    ('id_column', 'id'),
    ('value_column', 'value')
ON CONFLICT (setting_key) DO UPDATE SET setting_value = EXCLUDED.setting_value;

-- Enable Row Level Security (RLS) - Optional but recommended
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE ground_truth ENABLE ROW LEVEL SECURITY;
ALTER TABLE settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin ENABLE ROW LEVEL SECURITY;

-- Create policies for service role (API access)
-- Note: Adjust these policies based on your security requirements
-- For now, allowing service role full access (API will handle auth)
CREATE POLICY "Service role has full access to users" ON users
    FOR ALL USING (true);

CREATE POLICY "Service role has full access to submissions" ON submissions
    FOR ALL USING (true);

CREATE POLICY "Service role has full access to ground_truth" ON ground_truth
    FOR ALL USING (true);

CREATE POLICY "Service role has full access to settings" ON settings
    FOR ALL USING (true);

CREATE POLICY "Service role has full access to admin" ON admin
    FOR ALL USING (true);
