-- Fix level and experience_range columns (allow longer values like "Senior Lead", "10+")
-- Run once if you get "Data truncated for column 'level'" when adding an interviewer.
-- MySQL:
ALTER TABLE interviewers MODIFY COLUMN level VARCHAR(255) NULL;
ALTER TABLE interviewers MODIFY COLUMN experience_range VARCHAR(255) NULL;
