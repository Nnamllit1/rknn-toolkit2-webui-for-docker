-- SQL-Migration: Erweitere die Spalte password_hash auf VARCHAR(255)
ALTER TABLE users MODIFY password_hash VARCHAR(255);
