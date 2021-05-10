-- phpMyAdmin SQL Dump
-- version 5.1.0
-- https://www.phpmyadmin.net/
--
-- Máy chủ: 127.0.0.1
-- Thời gian đã tạo: Th5 10, 2021 lúc 07:23 AM
-- Phiên bản máy phục vụ: 10.4.18-MariaDB
-- Phiên bản PHP: 8.0.5

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Cơ sở dữ liệu: `digitaltwindb`
--

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `bim3d`
--

CREATE TABLE `bim3d` (
  `id` int(11) NOT NULL,
  `point_clound` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `detected` int(11) NOT NULL,
  `bim_generated` int(11) NOT NULL,
  `url_ply` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `2d` int(11) NOT NULL,
  `2d_format` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `3d` int(11) NOT NULL,
  `3d_format` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `bim3d`
--

INSERT INTO `bim3d` (`id`, `point_clound`, `detected`, `bim_generated`, `url_ply`, `2d`, `2d_format`, `3d`, `3d_format`) VALUES
(1, 'meeting room 1', 0, 0, '', 0, '1,2', 0, '1,2'),
(2, 'meeting room 2', 0, 0, '', 1, '1,2', 0, '1,2'),
(3, 'meeting room 3', 1, 0, '', 1, '1,2', 0, ''),
(4, 'meeting room 4', 0, 0, '', 0, '1,2', 0, '1,2'),
(5, 'meeting room 5', 0, 0, '', 0, '1,2', 0, '1,2'),
(6, 'meeting room 6', 0, 0, '', 0, '1,2', 0, '1,2'),
(7, 'meeting room 7', 0, 0, '', 1, '1,2', 0, ''),
(8, 'meeting room 8', 0, 0, '', 1, '1,2', 0, '1,2'),
(9, 'meeting room 9', 0, 0, '', 0, '', 0, ''),
(10, 'meeting room 10', 0, 0, '', 0, '1,2', 0, '1,2'),
(11, 'meeting room 11', 0, 0, '', 1, '1,2', 0, '1,2'),
(12, 'meeting room 12', 0, 0, '', 0, '1,2', 0, ''),
(13, 'meeting room 13', 0, 0, '', 0, '', 0, '1,2'),
(14, 'meeting room 14', 0, 0, '', 0, '1,2', 0, '1,2');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `format_file`
--

CREATE TABLE `format_file` (
  `id` int(11) NOT NULL,
  `format` varchar(5) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `format_file`
--

INSERT INTO `format_file` (`id`, `format`) VALUES
(1, 'abc'),
(2, 'def'),
(3, 'ghi'),
(4, 'jkl');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `point_cloud_data`
--

CREATE TABLE `point_cloud_data` (
  `id` int(11) NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `2d_url` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `3d_url` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `json_detected_url` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `point_cloud_data`
--

INSERT INTO `point_cloud_data` (`id`, `name`, `2d_url`, `3d_url`, `json_detected_url`) VALUES
(1, 'Meeting1', '/Meeting1.ply', '/Meeting1.dxf', ''),
(2, 'Meeting2', '/Meeting2.ply', '/Meeting2.dxf', '');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `project`
--

CREATE TABLE `project` (
  `id` int(11) NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` int(5) NOT NULL,
  `id_pointCloud` int(5) NOT NULL,
  `detected` int(11) NOT NULL,
  `bmi_generated` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `project`
--

INSERT INTO `project` (`id`, `name`, `user_id`, `id_pointCloud`, `detected`, `bmi_generated`) VALUES
(1, 'Meeting1', 0, 1, 0, 0);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `user`
--

CREATE TABLE `user` (
  `id` int(11) NOT NULL,
  `account` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `userconnectting`
--

CREATE TABLE `userconnectting` (
  `id` int(11) NOT NULL,
  `userID` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `cookies` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` int(11) NOT NULL,
  `timeStart` int(11) NOT NULL,
  `timeEnd` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Chỉ mục cho các bảng đã đổ
--

--
-- Chỉ mục cho bảng `bim3d`
--
ALTER TABLE `bim3d`
  ADD PRIMARY KEY (`id`);

--
-- Chỉ mục cho bảng `format_file`
--
ALTER TABLE `format_file`
  ADD PRIMARY KEY (`id`);

--
-- Chỉ mục cho bảng `point_cloud_data`
--
ALTER TABLE `point_cloud_data`
  ADD PRIMARY KEY (`id`);

--
-- Chỉ mục cho bảng `project`
--
ALTER TABLE `project`
  ADD PRIMARY KEY (`id`);

--
-- Chỉ mục cho bảng `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT cho các bảng đã đổ
--

--
-- AUTO_INCREMENT cho bảng `bim3d`
--
ALTER TABLE `bim3d`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=58;

--
-- AUTO_INCREMENT cho bảng `format_file`
--
ALTER TABLE `format_file`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT cho bảng `point_cloud_data`
--
ALTER TABLE `point_cloud_data`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT cho bảng `project`
--
ALTER TABLE `project`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT cho bảng `user`
--
ALTER TABLE `user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
