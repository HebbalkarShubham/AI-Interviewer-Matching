#!/usr/bin/env python3
"""Run fix_interviewer_level_experience_columns migration using app's DB config."""
import sys
from sqlalchemy import text

from app.config import settings
from app.database import engine

STATEMENTS = [
    "ALTER TABLE interviewers MODIFY COLUMN level VARCHAR(255) NULL",
    "ALTER TABLE interviewers MODIFY COLUMN experience_range VARCHAR(255) NULL",
]

def main():
    if not settings.DATABASE_URL:
        print("DATABASE_URL not set.", file=sys.stderr)
        sys.exit(1)
    with engine.connect() as conn:
        for sql in STATEMENTS:
            print(f"Running: {sql}")
            conn.execute(text(sql))
            conn.commit()
    print("Migration completed successfully.")

if __name__ == "__main__":
    main()
