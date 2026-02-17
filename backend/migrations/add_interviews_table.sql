-- Create interviews table for scheduled interviews with Accept/Reject token (run once)
-- MySQL:
CREATE TABLE IF NOT EXISTS interviews (
  id INT AUTO_INCREMENT PRIMARY KEY,
  interviewer_id INT NOT NULL,
  candidate_id INT NOT NULL,
  date DATE NOT NULL,
  time TIME NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
  custom_message TEXT NULL,
  secure_token VARCHAR(64) NOT NULL,
  token_expiry DATETIME(6) NOT NULL,
  created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
  UNIQUE KEY uq_interviews_secure_token (secure_token),
  KEY ix_interviews_secure_token (secure_token),
  KEY ix_interviews_interviewer_id (interviewer_id),
  KEY ix_interviews_candidate_id (candidate_id),
  CONSTRAINT fk_interviews_interviewer FOREIGN KEY (interviewer_id) REFERENCES interviewers (id) ON DELETE CASCADE,
  CONSTRAINT fk_interviews_candidate FOREIGN KEY (candidate_id) REFERENCES candidates (id) ON DELETE CASCADE
);
