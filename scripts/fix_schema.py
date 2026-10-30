#!/usr/bin/env python
"""Fix schema.sql to use IF NOT EXISTS"""
import re

with open('src/db/schema.sql', 'r') as f:
    content = f.read()

# Add IF NOT EXISTS to all CREATE statements
content = re.sub(r'CREATE TABLE ', 'CREATE TABLE IF NOT EXISTS ', content)
content = re.sub(r'CREATE VIEW ', 'CREATE VIEW IF NOT EXISTS ', content)
content = re.sub(r'CREATE INDEX ', 'CREATE INDEX IF NOT EXISTS ', content)
content = re.sub(r'CREATE TRIGGER ', 'CREATE TRIGGER IF NOT EXISTS ', content)

with open('src/db/schema.sql', 'w') as f:
    f.write(content)

print("Schema updated with IF NOT EXISTS")