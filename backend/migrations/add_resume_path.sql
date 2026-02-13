-- Add S3 path for resume file storage (run once)
-- MySQL:
ALTER TABLE candidates ADD COLUMN resume_path VARCHAR(512) NULL AFTER email;
