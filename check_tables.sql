-- Run this in Supabase SQL Editor to check what tables exist

-- Check all tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';

-- Check users table columns (if it exists)
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'users' 
  AND table_schema = 'public';

-- Check submissions table columns (if it exists)
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'submissions' 
  AND table_schema = 'public';
