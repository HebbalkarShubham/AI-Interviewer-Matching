-- Fix "Incorrect string value" when saving resume text with special Unicode characters.
-- Run once on EC2: sudo mysql employee < backend/migrations/fix_candidates_utf8mb4.sql
-- Or: sudo mysql employee -e "source /path/to/fix_candidates_utf8mb4.sql"

ALTER TABLE candidates
  CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
