-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Jul 05, 2025 at 08:55 AM
-- Server version: 8.0.31
-- PHP Version: 8.2.0

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `event_management`
--

-- --------------------------------------------------------

--
-- Table structure for table `admins`
--

DROP TABLE IF EXISTS `admins`;
CREATE TABLE IF NOT EXISTS `admins` (
  `admin_id` int NOT NULL,
  `name` varchar(100) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`admin_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `admins`
--

INSERT INTO `admins` (`admin_id`, `name`, `created_at`, `updated_at`) VALUES
(3, 'System Administrator', '2025-06-01 05:47:39', '2025-06-01 05:47:39');

-- --------------------------------------------------------

--
-- Table structure for table `bookings`
--

DROP TABLE IF EXISTS `bookings`;
CREATE TABLE IF NOT EXISTS `bookings` (
  `booking_id` int NOT NULL AUTO_INCREMENT,
  `customer_id` int NOT NULL,
  `event_id` int NOT NULL,
  `quantity` int NOT NULL,
  `total_amount` decimal(10,2) DEFAULT NULL,
  `booking_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `status` enum('booked','cancelled') DEFAULT 'booked',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`booking_id`),
  KEY `event_id` (`event_id`),
  KEY `idx_bookings_customer_id` (`customer_id`)
) ;

--
-- Dumping data for table `bookings`
--

INSERT INTO `bookings` (`booking_id`, `customer_id`, `event_id`, `quantity`, `total_amount`, `booking_time`, `status`, `updated_at`) VALUES
(2, 1, 1, 1, '50.00', '2025-06-02 12:41:26', 'booked', '2025-06-02 12:41:26'),
(3, 1, 1, 1, '50.00', '2025-06-03 07:57:43', 'booked', '2025-06-03 07:57:43'),
(4, 1, 1, 1, '50.00', '2025-06-03 08:04:53', 'booked', '2025-06-03 08:04:53'),
(5, 1, 2, 1, '20.00', '2025-06-18 13:19:52', 'booked', '2025-06-18 13:19:52');

-- --------------------------------------------------------

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
CREATE TABLE IF NOT EXISTS `categories` (
  `category_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`category_id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `categories`
--

INSERT INTO `categories` (`category_id`, `name`, `created_at`, `updated_at`) VALUES
(1, 'music concert', '2025-06-01 11:37:50', '2025-06-01 11:37:50'),
(2, 'Political', '2025-06-24 11:54:26', '2025-06-24 11:54:26'),
(3, 'bussiness', '2025-06-24 11:55:01', '2025-06-24 11:55:01'),
(4, 'social', '2025-06-24 11:55:30', '2025-06-24 11:55:30'),
(5, 'wedding', '2025-06-29 09:50:03', '2025-06-29 09:50:03');

-- --------------------------------------------------------

--
-- Table structure for table `customers`
--

DROP TABLE IF EXISTS `customers`;
CREATE TABLE IF NOT EXISTS `customers` (
  `customer_id` int NOT NULL,
  `name` varchar(100) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `preferences` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`customer_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `customers`
--

INSERT INTO `customers` (`customer_id`, `name`, `phone`, `address`, `preferences`, `created_at`, `updated_at`) VALUES
(1, 'Catherine Denny', '55', 'aa', 'music events', '2025-05-31 01:51:26', '2025-05-31 01:51:26');

-- --------------------------------------------------------

--
-- Table structure for table `events`
--

DROP TABLE IF EXISTS `events`;
CREATE TABLE IF NOT EXISTS `events` (
  `event_id` int NOT NULL AUTO_INCREMENT,
  `organizer_id` int NOT NULL,
  `title` varchar(200) NOT NULL,
  `price` decimal(10,2) DEFAULT '0.00',
  `description` text,
  `location` varchar(255) DEFAULT NULL,
  `category_id` int DEFAULT NULL,
  `event_date` datetime DEFAULT NULL,
  `total_seats` int NOT NULL,
  `available_seats` int NOT NULL,
  `image_url` varchar(255) DEFAULT NULL,
  `status` enum('pending','approved','rejected') DEFAULT 'pending',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`event_id`),
  KEY `idx_events_category_id` (`category_id`),
  KEY `idx_events_date` (`event_date`),
  KEY `idx_events_organizer_id` (`organizer_id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `events`
--

INSERT INTO `events` (`event_id`, `organizer_id`, `title`, `price`, `description`, `location`, `category_id`, `event_date`, `total_seats`, `available_seats`, `image_url`, `status`, `created_at`, `updated_at`) VALUES
(1, 2, 'Music concert', '50.00', 'eventt', 'kochi', 1, '2025-06-11 14:02:00', 20, 15, '/static/uploads/events/20250601_194846_banner_8.jpg', 'approved', '2025-06-01 08:48:47', '2025-06-03 08:04:53'),
(2, 2, 'Sangeeth raav', '20.00', 'music concert', 'kochi convention centre', 1, '2025-06-20 02:19:00', 20, 19, '/static/uploads/events/20250619_001830_register-bg.jpg', 'approved', '2025-06-18 13:18:30', '2025-06-18 13:19:52');

-- --------------------------------------------------------

--
-- Table structure for table `feedback`
--

DROP TABLE IF EXISTS `feedback`;
CREATE TABLE IF NOT EXISTS `feedback` (
  `feedback_id` int NOT NULL AUTO_INCREMENT,
  `customer_id` int NOT NULL,
  `event_id` int NOT NULL,
  `rating` int NOT NULL,
  `comments` text,
  `sentiment` varchar(20) DEFAULT NULL,
  `submitted_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `sentiment_score` float DEFAULT '0',
  `emotion_tags` text,
  `key_phrases` text,
  PRIMARY KEY (`feedback_id`),
  KEY `customer_id` (`customer_id`),
  KEY `idx_feedback_event_id` (`event_id`)
) ;

--
-- Dumping data for table `feedback`
--

INSERT INTO `feedback` (`feedback_id`, `customer_id`, `event_id`, `rating`, `comments`, `sentiment`, `submitted_at`, `updated_at`, `sentiment_score`, `emotion_tags`, `key_phrases`) VALUES
(1, 1, 1, 5, 'Absolutely amazing event! 🎉 The organization was flawless and the speakers were incredibly inspiring. I learned so much and made great connections. Will definitely attend again!', 'positive', '2024-01-15 09:00:00', '2024-01-15 09:00:00', 0, NULL, NULL),
(2, 2, 1, 5, 'BEST EVENT EVER!!! 😍 Everything was perfect from start to finish. The venue was stunning, food was delicious, and the content was mind-blowing. Worth every penny!', 'positive', '2024-01-15 11:15:00', '2024-01-15 11:15:00', 0, NULL, NULL),
(3, 3, 1, 5, 'Outstanding experience! The attention to detail was remarkable. Professional staff, excellent facilities, and top-notch presentations. Exceeded all my expectations!', 'positive', '2024-01-16 03:50:00', '2024-01-16 03:50:00', 0, NULL, NULL),
(4, 4, 1, 4, 'Really enjoyed this event. Great speakers and well-organized. The networking opportunities were fantastic. Only minor issue was the parking situation.', 'positive', '2024-01-16 05:45:00', '2024-01-16 05:45:00', 0, NULL, NULL),
(5, 5, 1, 5, 'Incredible! This event changed my perspective completely. The workshops were interactive and engaging. Thank you for such a wonderful experience! 🙏', 'positive', '2024-01-16 08:10:00', '2024-01-16 08:10:00', 0, NULL, NULL),
(6, 6, 1, 4, 'Very good event overall. Learned a lot and met interesting people. The venue was nice and the catering was decent. Would recommend to others.', 'positive', '2024-01-16 09:55:00', '2024-01-16 09:55:00', 0, NULL, NULL),
(7, 7, 1, 5, 'Phenomenal! Every session was valuable and the organizers did an amazing job. The event flow was smooth and the content was relevant and practical.', 'positive', '2024-01-17 03:20:00', '2024-01-17 03:20:00', 0, NULL, NULL),
(8, 8, 1, 4, 'Great event with excellent speakers. The topics were current and the discussions were thought-provoking. Minor delays but overall very satisfied.', 'positive', '2024-01-17 05:00:00', '2024-01-17 05:00:00', 0, NULL, NULL),
(9, 9, 1, 5, 'Absolutely loved it! 💖 The energy was infectious and the content was top-tier. Best investment I made this year. Looking forward to the next one!', 'positive', '2024-01-17 06:45:00', '2024-01-17 06:45:00', 0, NULL, NULL),
(10, 10, 1, 4, 'Solid event with good value. The presentations were informative and the networking breaks were well-timed. Appreciated the professional organization.', 'positive', '2024-01-17 08:50:00', '2024-01-17 08:50:00', 0, NULL, NULL),
(11, 1, 1, 3, 'It was okay. Some parts were interesting, others not so much. The venue was average and the food was standard conference fare. Nothing special but not bad either.', 'neutral', '2024-01-18 04:15:00', '2024-01-18 04:15:00', 0, NULL, NULL),
(12, 2, 1, 3, 'Mixed feelings about this event. Some speakers were great, others were boring. The organization was decent but could be improved. Average experience overall.', 'neutral', '2024-01-18 06:00:00', '2024-01-18 06:00:00', 0, NULL, NULL),
(13, 3, 1, 3, 'The event was fine. Met my basic expectations but nothing more. Content was somewhat relevant. Would consider attending again if the topics improve.', 'neutral', '2024-01-18 07:45:00', '2024-01-18 07:45:00', 0, NULL, NULL),
(14, 4, 1, 3, 'Decent event. Some useful information but felt like it could have been more engaging. The networking was limited and the schedule was a bit rushed.', 'neutral', '2024-01-18 09:30:00', '2024-01-18 09:30:00', 0, NULL, NULL),
(15, 5, 1, 3, 'Not bad, not great. The content was relevant but the delivery was somewhat dry. Venue was acceptable. Might attend future events depending on the topic.', 'neutral', '2024-01-18 11:15:00', '2024-01-18 11:15:00', 0, NULL, NULL),
(16, 6, 1, 2, 'Disappointing experience. The event was poorly organized and the speakers seemed unprepared. Long delays and uncomfortable seating. Expected much better.', 'negative', '2024-01-19 04:50:00', '2024-01-19 04:50:00', 0, NULL, NULL),
(17, 7, 1, 1, 'Terrible event! 😠 Complete waste of time and money. Disorganized, boring speakers, and awful venue. The food was cold and the WiFi didn\'t work. Never again!', 'negative', '2024-01-19 06:35:00', '2024-01-19 06:35:00', 0, NULL, NULL),
(18, 8, 1, 2, 'Very disappointed. The content was outdated and irrelevant. Poor sound quality made it hard to hear. The registration process was a nightmare. Not worth it.', 'negative', '2024-01-19 09:00:00', '2024-01-19 09:00:00', 0, NULL, NULL),
(19, 9, 1, 1, 'Worst event I\'ve ever attended. Unprofessional staff, terrible organization, and completely useless content. Felt like a scam. Demanding a refund!', 'negative', '2024-01-19 10:45:00', '2024-01-19 10:45:00', 0, NULL, NULL),
(20, 10, 1, 2, 'Not impressed at all. The event started late, ended early, and the middle was boring. Overpriced for what was delivered. Poor value for money.', 'negative', '2024-01-19 12:30:00', '2024-01-19 12:30:00', 0, NULL, NULL),
(21, 1, 2, 5, 'WOW! What an incredible experience! 🌟 This event exceeded every expectation. The speakers were world-class and the content was revolutionary. Life-changing!', 'positive', '2024-02-10 04:00:00', '2024-02-10 04:00:00', 0, NULL, NULL),
(22, 2, 2, 5, 'Absolutely brilliant! The best event I\'ve attended in years. Every minute was valuable and the networking opportunities were amazing. Highly recommend! 👏', 'positive', '2024-02-10 06:15:00', '2024-02-10 06:15:00', 0, NULL, NULL),
(23, 3, 2, 4, 'Excellent event! Very well organized and the content was cutting-edge. Great venue and fantastic catering. Minor technical issues but overall outstanding.', 'positive', '2024-02-10 07:50:00', '2024-02-10 07:50:00', 0, NULL, NULL),
(24, 4, 2, 5, 'Perfect in every way! The organizers thought of everything. Inspiring speakers, comfortable venue, delicious food, and seamless execution. Bravo! 🎊', 'positive', '2024-02-10 09:40:00', '2024-02-10 09:40:00', 0, NULL, NULL),
(25, 5, 2, 4, 'Really impressive event. High-quality speakers and relevant content. The interactive sessions were particularly valuable. Well worth the investment.', 'positive', '2024-02-10 11:55:00', '2024-02-10 11:55:00', 0, NULL, NULL),
(26, 6, 2, 5, 'Phenomenal! This event was a game-changer for me. The insights I gained will transform my business. Thank you for such an amazing experience! 🚀', 'positive', '2024-02-11 03:10:00', '2024-02-11 03:10:00', 0, NULL, NULL),
(27, 7, 2, 4, 'Great event with excellent production value. The speakers were knowledgeable and engaging. Good mix of theory and practical applications. Enjoyed it thoroughly.', 'positive', '2024-02-11 05:25:00', '2024-02-11 05:25:00', 0, NULL, NULL),
(28, 8, 2, 5, 'Outstanding! Every aspect was professionally handled. The content was fresh and actionable. Made valuable connections. Looking forward to implementing what I learned.', 'positive', '2024-02-11 07:00:00', '2024-02-11 07:00:00', 0, NULL, NULL),
(29, 9, 2, 4, 'Very good event. Learned a lot and met great people. The venue was beautiful and the organization was smooth. Minor room temperature issues but overall excellent.', 'positive', '2024-02-11 08:45:00', '2024-02-11 08:45:00', 0, NULL, NULL),
(30, 10, 2, 5, 'Incredible experience! The quality of speakers and content was unmatched. Professional execution and attention to detail. This is how events should be done! ⭐', 'positive', '2024-02-11 10:30:00', '2024-02-11 10:30:00', 0, NULL, NULL),
(31, 1, 2, 3, 'The event was okay. Some sessions were interesting while others felt like filler content. The venue was nice but the catering was mediocre. Average overall.', 'neutral', '2024-02-12 03:45:00', '2024-02-12 03:45:00', 0, NULL, NULL),
(32, 2, 2, 3, 'Decent event but had higher expectations based on the marketing. Content was somewhat useful but not groundbreaking. Networking was limited due to poor layout.', 'neutral', '2024-02-12 05:30:00', '2024-02-12 05:30:00', 0, NULL, NULL),
(33, 3, 2, 3, 'It was fine. Nothing spectacular but not terrible either. Some good takeaways but felt like it could have been condensed into half the time. Moderately satisfied.', 'neutral', '2024-02-12 08:15:00', '2024-02-12 08:15:00', 0, NULL, NULL),
(34, 4, 2, 3, 'Mixed bag. Some excellent speakers but others were clearly just filling time. The event had potential but execution was inconsistent. Room for improvement.', 'neutral', '2024-02-12 10:00:00', '2024-02-12 10:00:00', 0, NULL, NULL),
(35, 5, 2, 2, 'Disappointing event. The marketing promised much more than was delivered. Several speakers cancelled last minute and replacements were subpar. Poor communication.', 'negative', '2024-02-13 04:50:00', '2024-02-13 04:50:00', 0, NULL, NULL),
(36, 6, 2, 1, 'Absolutely horrible! 😡 Worst organized event ever. Technical failures throughout, uncomfortable chairs, terrible food, and boring content. Total waste of money!', 'negative', '2024-02-13 07:05:00', '2024-02-13 07:05:00', 0, NULL, NULL),
(37, 7, 2, 2, 'Very poor experience. The event was oversold and overcrowded. Couldn\'t see or hear properly. Long lines for everything. Felt like a money grab rather than value delivery.', 'negative', '2024-02-13 09:20:00', '2024-02-13 09:20:00', 0, NULL, NULL),
(38, 8, 2, 1, 'Terrible! The speakers were unprepared and the content was outdated. The venue was too small and poorly ventilated. Regret attending and want my money back.', 'negative', '2024-02-13 10:55:00', '2024-02-13 10:55:00', 0, NULL, NULL),
(39, 9, 2, 2, 'Not worth it. The event felt rushed and disorganized. Poor time management led to important sessions being cut short. The networking was chaotic and unstructured.', 'negative', '2024-02-13 12:40:00', '2024-02-13 12:40:00', 0, NULL, NULL),
(40, 10, 2, 4, 'Great event! 👍 Loved the interactive workshops and the Q&A sessions. The coffee was excellent ☕ and the venue had good WiFi. Minor sound issues but overall fantastic!', 'positive', '2024-02-14 03:30:00', '2024-02-14 03:30:00', 0, NULL, NULL),
(41, 1, 2, 1, 'UGH! What a disaster! 💸 The event was a complete rip-off. Nothing worked properly - A/V failed, catering was late, and speakers were boring. #NeverAgain', 'negative', '2024-02-14 06:00:00', '2024-02-14 06:00:00', 0, NULL, NULL),
(42, 2, 2, 5, 'AMAZING!!! 🎉🎊 This event was absolutely perfect! Every detail was thoughtfully planned. The speakers were inspiring and the content was actionable. 10/10 would recommend! 💯', 'positive', '2024-02-14 07:45:00', '2024-02-14 07:45:00', 0, NULL, NULL),
(43, 3, 2, 3, 'Meh... 😐 It was an event. Some parts were good, some weren\'t. The price was reasonable but nothing really stood out. Probably won\'t attend next year unless major improvements.', 'neutral', '2024-02-14 10:15:00', '2024-02-14 10:15:00', 0, NULL, NULL),
(44, 4, 2, 2, 'Frustrated with this event 😤 The registration was a mess, the schedule kept changing, and half the promised speakers didn\'t show up. Poor planning and execution.', 'negative', '2024-02-14 11:50:00', '2024-02-14 11:50:00', 0, NULL, NULL),
(45, 5, 2, 5, 'Perfect! 🌟', 'positive', '2024-02-15 03:00:00', '2024-02-15 03:00:00', 0, NULL, NULL),
(46, 6, 2, 1, 'Awful.', 'negative', '2024-02-15 04:45:00', '2024-02-15 04:45:00', 0, NULL, NULL),
(47, 7, 2, 3, 'OK', 'neutral', '2024-02-15 06:30:00', '2024-02-15 06:30:00', 0, NULL, NULL),
(48, 8, 2, 4, 'This event was really well put together and I appreciate all the hard work that went into making it happen. The speakers were knowledgeable and presented complex topics in an accessible way. The venue was comfortable with good acoustics and lighting. The catering exceeded my expectations with a variety of healthy options. The networking sessions were well-structured and I made several valuable connections. The only minor complaint I have is that some sessions ran a bit long, which made the schedule tight. Overall, it was a very positive experience and I would definitely consider attending future events by this organizer. The value for money was excellent and I left feeling inspired and motivated. Thank you for a great day!', 'positive', '2024-02-15 09:00:00', '2024-02-15 09:00:00', 0, NULL, NULL),
(49, 9, 2, 3, 'The event had some really good moments, especially the keynote speaker who was absolutely brilliant! However, the afternoon sessions were quite disappointing and felt like a waste of time. The venue was beautiful but the catering was terrible - cold food and long queues. Mixed feelings overall... some parts were worth it, others definitely weren\'t. Would maybe attend again if they fix the issues.', 'neutral', '2024-02-15 11:15:00', '2024-02-15 11:15:00', 0, NULL, NULL),
(50, 10, 2, 2, 'Started with high hopes but quickly became disappointed 😞 The first speaker was great but it went downhill from there. Technical problems, poor organization, and overpriced food. The venue was nice though, and I did meet one interesting person during the break. Not sure if I\'d recommend it... maybe if they improve significantly for next time. The potential is there but execution needs work.', 'negative', '2024-02-15 12:50:00', '2024-02-15 12:50:00', 0, NULL, NULL),
(51, 1, 1, 4, 'As a professional in this industry for over 15 years, I found this event to be quite valuable. The content was well-researched and the speakers demonstrated deep expertise in their respective fields. The networking opportunities were strategically planned and facilitated meaningful connections. While there were minor logistical issues, the overall execution was professional and the ROI was positive.', 'positive', '2024-02-16 04:00:00', '2024-02-16 04:00:00', 0, NULL, NULL),
(52, 2, 1, 1, 'omg this was sooooo bad!!! like seriously the worst thing ever 😭😭😭 everything was broken and the food was gross and i was so bored i almost fell asleep!!! total waste of my saturday and my money!!! never going to anything like this again!!!', 'negative', '2024-02-16 05:45:00', '2024-02-16 05:45:00', 0, NULL, NULL),
(53, 3, 1, 5, 'Exceptional event! The curation of speakers was masterful, each bringing unique perspectives that complemented the overall narrative beautifully. The production quality was cinema-grade, and the attention to participant experience was evident in every detail. This sets a new benchmark for industry events. Congratulations to the entire team! 🏆', 'positive', '2024-02-16 07:30:00', '2024-02-16 07:30:00', 0, NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `organizers`
--

DROP TABLE IF EXISTS `organizers`;
CREATE TABLE IF NOT EXISTS `organizers` (
  `organizer_id` int NOT NULL,
  `name` varchar(100) NOT NULL,
  `organization_name` varchar(150) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `bio` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`organizer_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `organizers`
--

INSERT INTO `organizers` (`organizer_id`, `name`, `organization_name`, `phone`, `bio`, `created_at`, `updated_at`) VALUES
(2, 'Linkin Park', 'Linkin Park Ltd', '', 'Music Band', '2025-05-31 01:52:58', '2025-06-23 13:51:43');

-- --------------------------------------------------------

--
-- Table structure for table `payments`
--

DROP TABLE IF EXISTS `payments`;
CREATE TABLE IF NOT EXISTS `payments` (
  `payment_id` int NOT NULL AUTO_INCREMENT,
  `booking_id` int NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `payment_mode` varchar(50) DEFAULT NULL,
  `payment_status` enum('success','failed','pending') DEFAULT 'pending',
  `transaction_id` varchar(100) DEFAULT NULL,
  `payment_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`payment_id`),
  KEY `booking_id` (`booking_id`)
) ;

--
-- Dumping data for table `payments`
--

INSERT INTO `payments` (`payment_id`, `booking_id`, `amount`, `payment_mode`, `payment_status`, `transaction_id`, `payment_date`, `updated_at`) VALUES
(1, 4, '50.00', 'credit_card', 'success', 'TXN-20250603133502', '2025-06-03 08:05:02', '2025-06-03 08:05:02'),
(2, 5, '20.00', 'credit_card', 'success', 'TXN-20250618184956', '2025-06-18 13:19:57', '2025-06-18 13:19:57');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
CREATE TABLE IF NOT EXISTS `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` enum('admin','organizer','customer') NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `email`, `password_hash`, `role`, `created_at`, `updated_at`) VALUES
(1, 'cathy@gmail.com', 'scrypt:32768:8:1$8v6SymC5hODFhzrG$930af2f6cfd1c3bfb82d4cd14af331583491d044d8a7a9d1eda3bf2779bb98e9fe00b50b400e81ae5a4ced294cadd05beee8cdd9bb48b158af6f20aa180488d8', 'customer', '2025-05-31 01:51:26', '2025-05-31 01:51:26'),
(2, 'linkin@gmail.com', 'scrypt:32768:8:1$PzHFoXvCLS6IKDXE$679cc11129541dd20c82ba29f9b5500370f75d071176eb0d001afda2736e793dc030a02710d7de622e9fdf429f844d2507dda7d7935af95dcba1f1855105d761', 'organizer', '2025-05-31 01:52:58', '2025-05-31 01:52:58'),
(3, 'admin@gmail.com', 'scrypt:32768:8:1$oSiTMUI4t6u0Iq9L$1d2a9769e45e75a573b66dd0a8f814bc9b731bc8d0243d99b37b25ec8d8c523375f5a0e14c942a9c3e3e883dec7bfe367e3aae5fe4da238e6b03c020f26c0d50', 'admin', '2025-06-01 05:47:39', '2025-06-01 05:47:39');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
