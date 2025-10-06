DROP TABLE IF EXISTS user;
DROP TABLE if EXISTS otps;
DROP TABLE if EXISTS user_details;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  is_registered BOOLEAN DEFAULT FALSE
);

CREATE TABLE otps (
  id INTEGER NOT NULL,
  otp TEXT,
  created BIGINT,
  FOREIGN KEY (id) REFERENCES user (id)
);

CREATE TABLE user_details (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  age INTEGER,
  gender TEXT,
  income INTEGER,
  caste TEXT,
  states TEXT,
  occupation TEXT,
  aadhar TEXT,
  pan TEXT,
  user_id INTEGER
)
