DROP TABLE if EXISTS otps;
DROP TABLE IF EXISTS user;
DROP TABLE if EXISTS user_details;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  username varchar(100) UNIQUE NOT NULL,
  email varchar(100) UNIQUE NOT NULL,
  password varchar(200) NOT NULL,
  is_registered BOOLEAN DEFAULT FALSE
);

CREATE TABLE otps (
  id INTEGER NOT NULL,
  otp varchar(100),
  created BIGINT,
  FOREIGN KEY (id) REFERENCES user (id)
);

CREATE TABLE user_details (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  name varchar(100),
  age INTEGER,
  gender varchar(100),
  income INTEGER,
  caste varchar(100),
  states varchar(100),
  occupation varchar(100),
  aadhar varchar(100),
  pan varchar(100),
  user_id INTEGER
);
