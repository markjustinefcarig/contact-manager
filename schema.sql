CREATE DATABASE contact_manager;
USE contact_manager;

CREATE TABLE `contacts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `address` text,
  `relationship` varchar(50) DEFAULT NULL,
  `notes` text,
  PRIMARY KEY (`id`)
);