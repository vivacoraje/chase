/*
 Navicat MySQL Data Transfer

 Source Server         : chase
 Source Server Type    : MySQL
 Source Server Version : 80011
 Source Host           : localhost:3306
 Source Schema         : chase

 Target Server Type    : MySQL
 Target Server Version : 80011
 File Encoding         : 65001

 Date: 20/04/2019 12:55:36
*/

CREATE USER 'chase'@'%' IDENTIFIED WITH mysql_native_password BY '123456';
create database `chase`;
use chase;
GRANT ALL ON chase.* TO 'chase'@'%'; 

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for fetch_record
-- ----------------------------
DROP TABLE IF EXISTS `fetch_record`;
CREATE TABLE `fetch_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `updated` tinyint(1) DEFAULT NULL,
  `timestamp` int(11) DEFAULT NULL,
  `weekday` int(11) DEFAULT NULL,
  `schedule` varchar(64) DEFAULT NULL,
  `fetcher_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fetcher_id` (`fetcher_id`),
  CONSTRAINT `fetch_record_ibfk_1` FOREIGN KEY (`fetcher_id`) REFERENCES `fetchers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for fetchers
-- ----------------------------
DROP TABLE IF EXISTS `fetchers`;
CREATE TABLE `fetchers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url` varchar(128) DEFAULT NULL,
  `ended` tinyint(1) DEFAULT NULL,
  `subscription_id` int(11) DEFAULT NULL,
  `address_type` varchar(32) DEFAULT NULL,
  `current_schedule` blob,
  `adjusted_schedule` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `subscription_id` (`subscription_id`),
  CONSTRAINT `fetchers_ibfk_1` FOREIGN KEY (`subscription_id`) REFERENCES `subscriptions` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for movies
-- ----------------------------
DROP TABLE IF EXISTS `movies`;
CREATE TABLE `movies` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(128) DEFAULT NULL,
  `poster_path` varchar(128) DEFAULT NULL,
  `episode_aired` varchar(32) DEFAULT NULL,
  `episode_count` int(11) DEFAULT NULL,
  `synopsis` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `title` (`title`),
  UNIQUE KEY `poster_path` (`poster_path`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for refes
-- ----------------------------
DROP TABLE IF EXISTS `refes`;
CREATE TABLE `refes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url` varchar(64) DEFAULT NULL,
  `second_level_domain` varchar(16) DEFAULT NULL,
  `rating_value` float DEFAULT NULL,
  `rating_count` int(11) DEFAULT NULL,
  `fetchable` tinyint(1) DEFAULT NULL,
  `movie_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `movie_id` (`movie_id`),
  CONSTRAINT `refes_ibfk_1` FOREIGN KEY (`movie_id`) REFERENCES `movies` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for search
-- ----------------------------
DROP TABLE IF EXISTS `search`;
CREATE TABLE `search` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `keywords` varchar(128) DEFAULT NULL,
  `timestamp` int(11) DEFAULT NULL,
  `hit` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for subscriptions
-- ----------------------------
DROP TABLE IF EXISTS `subscriptions`;
CREATE TABLE `subscriptions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(128) DEFAULT NULL,
  `user_count` int(11) DEFAULT NULL,
  `ended` tinyint(1) DEFAULT NULL,
  `movie_id` int(11) DEFAULT NULL,
  `create_at` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `title` (`title`),
  KEY `movie_id` (`movie_id`),
  CONSTRAINT `subscriptions_ibfk_1` FOREIGN KEY (`movie_id`) REFERENCES `movies` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for user_subscription
-- ----------------------------
DROP TABLE IF EXISTS `user_subscription`;
CREATE TABLE `user_subscription` (
  `user_id` int(11) DEFAULT NULL,
  `subscription_id` int(11) DEFAULT NULL,
  KEY `user_id` (`user_id`),
  KEY `subscription_id` (`subscription_id`),
  CONSTRAINT `user_subscription_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `user_subscription_ibfk_2` FOREIGN KEY (`subscription_id`) REFERENCES `subscriptions` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for user_video
-- ----------------------------
DROP TABLE IF EXISTS `user_video`;
CREATE TABLE `user_video` (
  `user_id` int(11) NOT NULL,
  `video_id` int(11) NOT NULL,
  `finished` tinyint(1) DEFAULT NULL,
  `subs_id` int(11) NOT NULL,
  PRIMARY KEY (`user_id`,`video_id`,`subs_id`),
  KEY `video_id` (`video_id`),
  KEY `subs_id` (`subs_id`),
  CONSTRAINT `user_video_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `user_video_ibfk_2` FOREIGN KEY (`video_id`) REFERENCES `videos` (`id`),
  CONSTRAINT `user_video_ibfk_3` FOREIGN KEY (`subs_id`) REFERENCES `subscriptions` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(32) NOT NULL,
  `email` varchar(32) NOT NULL,
  `password_hash` varchar(256) DEFAULT NULL,
  `avatar_hash` varchar(32) DEFAULT NULL,
  `login_count` int(11) DEFAULT NULL,
  `member_since` int(11) DEFAULT NULL,
  `last_seen` int(11) DEFAULT NULL,
  `confirmed` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for videos
-- ----------------------------
DROP TABLE IF EXISTS `videos`;
CREATE TABLE `videos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(64) DEFAULT NULL,
  `address` varchar(512) DEFAULT NULL,
  `fetcher_id` int(11) DEFAULT NULL,
  `timestamp` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `address` (`address`),
  KEY `fetcher_id` (`fetcher_id`),
  CONSTRAINT `videos_ibfk_1` FOREIGN KEY (`fetcher_id`) REFERENCES `fetchers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

SET FOREIGN_KEY_CHECKS = 1;
