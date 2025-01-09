-- Create the database
CREATE DATABASE supply_chains;

-- Use the database
USE supply_chains;

-- Create the `disruptions` table
CREATE TABLE disruptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    location VARCHAR(255) NOT NULL,
    cause VARCHAR(255) NOT NULL,
    impact VARCHAR(255) NOT NULL,
    date DATETIME NOT NULL
);
