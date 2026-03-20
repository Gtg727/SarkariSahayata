-- ===============================
-- DROP TABLES (ORDER MATTERS)
-- ===============================

DROP TABLE IF EXISTS otps;
DROP TABLE IF EXISTS user_details;
DROP TABLE IF EXISTS schemes;
DROP TABLE IF EXISTS user;


-- ===============================
-- USER TABLE
-- ===============================

CREATE TABLE user (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(100) UNIQUE NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  password VARCHAR(200) NOT NULL,
  is_registered BOOLEAN DEFAULT FALSE,
  user_type VARCHAR(15) DEFAULT 'user'
);


-- ===============================
-- OTP TABLE
-- ===============================

CREATE TABLE otps (
  id INT AUTO_INCREMENT PRIMARY KEY,
  otp VARCHAR(100),
  created BIGINT,
  FOREIGN KEY (id) REFERENCES user(id) ON DELETE CASCADE
);


-- ===============================
-- USER DETAILS TABLE
-- ===============================

CREATE TABLE user_details (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  age INT,
  gender VARCHAR(100),
  income INT,
  caste VARCHAR(100),
  states VARCHAR(100),
  occupation VARCHAR(100),
  aadhar VARCHAR(100),
  pan VARCHAR(100),
  user_id INT,
  FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);


-- ===============================
-- SCHEMES TABLE (NEW - STEP 1)
-- ===============================

CREATE TABLE schemes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  category VARCHAR(100),
  description TEXT,
  benefits TEXT,
  eligibility TEXT
);

 ALTER TABLE schemes
ADD COLUMN objectives TEXT,
ADD COLUMN application_process TEXT,
ADD COLUMN documents TEXT,
ADD COLUMN min_age INT,
ADD COLUMN max_age INT,
ADD COLUMN max_income INT,
ADD COLUMN gender VARCHAR(50),
ADD COLUMN caste VARCHAR(50),
ADD COLUMN state VARCHAR(100),
ADD COLUMN occupation VARCHAR(100);