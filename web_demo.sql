-- phpMyAdmin SQL Dump
-- version 5.0.4
-- https://www.phpmyadmin.net/
--
-- Máy chủ: mysql
-- Thời gian đã tạo: Th2 19, 2021 lúc 07:20 AM
-- Phiên bản máy phục vụ: 5.7.33
-- Phiên bản PHP: 7.4.13

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Cơ sở dữ liệu: `web_demo`
--

DELIMITER $$
--
-- Thủ tục
--
CREATE DEFINER=`root`@`%` PROCEDURE `sp_checkPoint` (IN `p_location` VARCHAR(250))  BEGIN
    select * from point_running where 	p_address = p_location;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_createBooking` (IN `o_id_user` INT(10), IN `o_name` VARCHAR(50), IN `o_phone` VARCHAR(50), IN `o_pickup_point_start` VARCHAR(500), IN `o_address_start` VARCHAR(250), IN `o_pickup_point_end` VARCHAR(500), IN `o_address_end` VARCHAR(50), IN `o_chair_type` VARCHAR(20), IN `o_quantity` VARCHAR(50), IN `o_start_date` DATE, IN `o_start_time` VARCHAR(10), IN `o_stop_date` DATE, IN `o_stop_time` VARCHAR(10))  BEGIN
	insert into order_trip(
        user_id,
	    name,
	    phone,
	    pickup_point_start,
	    address_start,
	    pickup_point_end,
	    address_end,
	    chair_type,
	    quantity,
	    start_date,
	    start_time,
	    stop_date,
	    stop_time,
        trip_id
	)
	values
	(
        o_id_user,
		o_name,
        o_phone,
        o_pickup_point_start,
        o_address_start,
        o_pickup_point_end,
        o_address_end,
        o_chair_type,
        o_quantity,
        o_start_date,
        o_start_time,
        o_stop_date,
        o_stop_time,
        1
	);
    if ( select exists (select 1 from point_running where p_address = o_address_start) ) 
    THEN
        UPDATE `web_demo`.`point_running` 
        SET `p_pick_up` = `p_pick_up` + 1, 
        `time_update` = CURRENT_TIMESTAMP
        WHERE p_address = o_address_start;
	ELSE
    insert into point_running(p_name,p_address,p_pick_up,p_drop,trip_id,time_update) VALUES (o_pickup_point_start,o_address_start,1,0,1,CURRENT_TIMESTAMP);

END IF;
if ( select exists (select 1 from point_running where p_address = o_address_end) ) 
    THEN
        UPDATE `web_demo`.`point_running` 
        SET `p_drop` = `p_drop` + 1, 
        `time_update` = CURRENT_TIMESTAMP 
        WHERE p_address = o_address_end;
	ELSE
    insert into point_running(p_name,p_address,p_pick_up,p_drop,trip_id,time_update) VALUES (o_pickup_point_end,o_address_end,0,1,1,CURRENT_TIMESTAMP );

END IF;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_createUser` (IN `p_name` VARCHAR(200), IN `p_username` VARCHAR(200), IN `p_password` VARCHAR(200), IN `p_phone` VARCHAR(15), IN `p_birth` DATE)  BEGIN
	if ( select exists (select user_username from tbl_user where user_username = p_username) ) THEN
	
		select 'Username Exists !!';
	
	ELSE
	
		insert into tbl_user
		(
			user_name,
			user_username,
			user_password,
            user_phone_number,
            user_birth_date
		)
		values
		(
			p_name,
			p_username,
			p_password,
            p_phone,
            p_birth
		);
	
	END IF;
END$$

CREATE DEFINER=`root`@`%` PROCEDURE `sp_getOrder` (IN `p_trip_id` INT)  BEGIN
    select id from order_trip where trip_id = p_trip_id;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_getPoint` (IN `p_trip_id` INT)  BEGIN
select `p_name`,`p_address`,`p_pick_up`,`p_drop` from point_running where trip_id = p_trip_id ORDER BY `p_drop` ASC ;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_getTrip` (IN `p_trip_id` INT)  BEGIN
select `trip_id`, `car_id`,`blank_seats`,`seated`,`name_start_point`,`start_point`,`name_stop_point`,`stop_point` from trip_running where trip_id = p_trip_id;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_validateLogin` (IN `p_username` LONGTEXT)  BEGIN
    select * from tbl_user where user_username = p_username;
END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `car`
--

CREATE TABLE `car` (
  `id` int(11) NOT NULL,
  `car_number` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `license_plates` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `driver` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ordinaly_chair_number` int(11) NOT NULL,
  `disability_seat_number` int(11) NOT NULL,
  `type` int(11) NOT NULL,
  `info` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `car`
--

INSERT INTO `car` (`id`, `car_number`, `license_plates`, `driver`, `ordinaly_chair_number`, `disability_seat_number`, `type`, `info`) VALUES
(1, '1', '123', 'zxc', 20, 0, 1, 1),
(2, '2', '345', 'gdgdf', 20, 0, 1, 1),
(3, '3', '456', 'ljkljkljk', 20, 0, 1, 1);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `order_trip`
--

CREATE TABLE `order_trip` (
  `id` int(11) NOT NULL,
  `user_id` int(10) NOT NULL,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `pickup_point_start` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `address_start` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `pickup_point_end` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `address_end` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `chair_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `quantity` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `start_date` date NOT NULL,
  `start_time` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `stop_date` date NOT NULL,
  `stop_time` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `trip_id` int(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `order_trip`
--

INSERT INTO `order_trip` (`id`, `user_id`, `name`, `phone`, `pickup_point_start`, `address_start`, `pickup_point_end`, `address_end`, `chair_type`, `quantity`, `start_date`, `start_time`, `stop_date`, `stop_time`, `trip_id`) VALUES
(211, 20, 'Trinh Huu Duc', '(+84) 33-98-0209', 'Ngõ 78 - Duy Tân, Cầu Giấy, Quận Cầu Giấy, Hà Nội, 122863, Việt Nam', '21.0303347,105.7835052', 'Lotte Center Hanoi, 54, Liễu Giai, Ngọc Khánh, Phường Ngọc Khánh, Quận Ba Đình, Hà Nội, 11150, Việt Nam', '21.032189000000002,105.81263795', '0', '0', '2021-01-29', '13:00', '2021-01-29', '13:00', 1),
(212, 20, 'Trinh Huu Duc', '(+84) 33-98-0209', 'Ngõ 78 - Duy Tân, Cầu Giấy, Quận Cầu Giấy, Hà Nội, 122863, Việt Nam', '21.0303347,105.7835052', 'Lotte Center Hanoi, 54, Liễu Giai, Ngọc Khánh, Phường Ngọc Khánh, Quận Ba Đình, Hà Nội, 11150, Việt Nam', '21.032189000000002,105.81263795', '0', '0', '2021-01-29', '13:00', '2021-01-29', '13:00', 1),
(213, 20, 'Trinh Huu Duc', '(+84) 33-98-0209', 'Ngõ 78 - Duy Tân, Cầu Giấy, Quận Cầu Giấy, Hà Nội, 122863, Việt Nam', '21.0303347,105.7835052', 'Lotte Center Hanoi, 54, Liễu Giai, Ngọc Khánh, Phường Ngọc Khánh, Quận Ba Đình, Hà Nội, 11150, Việt Nam', '21.032189000000002,105.81263795', '0', '0', '2021-01-29', '13:00', '2021-01-29', '13:00', 1),
(214, 20, 'Trinh Huu Duc', '(+84) 33-98-0209', 'Hà Nội, Việt Nam', '21.0294498,105.8544441', 'Lotte Center Hanoi, 54, Liễu Giai, Ngọc Khánh, Phường Ngọc Khánh, Quận Ba Đình, Hà Nội, 11150, Việt Nam', '21.032189000000002,105.81263795', '0', '0', '2021-01-29', '13:00', '2021-01-29', '13:00', 1),
(216, 20, 'Trinh Huu Duc', '(+84) 33-98-0209', 'Demo', '21.02789,105.82479', 'demo', '21.032189000000002,105.81263795', '0', '0', '2021-01-29', '13:00', '2021-01-29', '13:00', 2),
(217, 20, 'Trinh Huu Duc', '(+84) 33-98-0209', 'Demo', '21.00991,105.82309', 'demo', '21.032189000000002,105.81263795', '0', '0', '2021-01-29', '13:00', '2021-01-29', '13:00', 2),
(218, 20, 'Trinh Huu Duc', '(+84) 33-98-0209', 'Demo', '21.00031,105.81595', 'demo', '21.032189000000002,105.81263795', '0', '0', '2021-01-29', '13:00', '2021-01-29', '13:00', 2),
(221, 20, 'Trinh Huu Duc', '(+84) 33-98-0209', 'Demo', '21.04450,105.80580', 'demo', '21.032189000000002,105.81263795', '0', '0', '2021-01-29', '13:00', '2021-01-29', '13:00', 3),
(222, 20, 'Trinh Huu Duc', '(+84) 33-98-0209', 'Demo', '21.03701,105.80657', 'demo', '21.032189000000002,105.81263795', '0', '0', '2021-01-29', '13:00', '2021-01-29', '13:00', 3),
(223, 20, 'Trinh Huu Duc', '(+84) 33-98-0209', 'Demo', '21.02416,105.79822', 'demo', '21.032189000000002,105.81263795', '0', '0', '2021-01-29', '13:00', '2021-01-29', '13:00', 3),
(224, 20, 'Trinh Huu Duc', '(+84) 33-98-0209', 'Demo', '21.01502,105.80538', 'demo', '21.032189000000002,105.81263795', '0', '0', '2021-01-29', '13:00', '2021-01-29', '13:00', 3),
(225, 20, 'Trinh Huu Duc', '(+84) 33-98-0209', 'Demo', '21.00228,105.82263', 'demo', '21.032189000000002,105.81263795', '0', '0', '2021-01-29', '13:00', '2021-01-29', '13:00', 3);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `point_running`
--

CREATE TABLE `point_running` (
  `p_id` int(10) NOT NULL,
  `p_name` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `p_address` varchar(250) COLLATE utf8mb4_unicode_ci NOT NULL,
  `p_pick_up` int(10) NOT NULL,
  `p_drop` int(10) NOT NULL,
  `trip_id` int(10) NOT NULL,
  `time_update` varchar(250) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `point_running`
--

INSERT INTO `point_running` (`p_id`, `p_name`, `p_address`, `p_pick_up`, `p_drop`, `trip_id`, `time_update`) VALUES
(52, 'Ngõ 78 - Duy Tân, Cầu Giấy, Quận Cầu Giấy, Hà Nội, 122863, Việt Nam', '21.0303347,105.7835052', 3, 0, 1, '2021-02-05 08:53:06'),
(53, 'Lotte Center Hanoi, 54, Liễu Giai, Ngọc Khánh, Phường Ngọc Khánh, Quận Ba Đình, Hà Nội, 11150, Việt Nam', '21.032189000000002,105.81263795', 0, 4, 1, '2021-02-05 08:53:22'),
(54, 'Hà Nội, Việt Nam', '21.0294498,105.8544441', 1, 0, 1, '2021-02-05 08:53:22'),
(56, 'demo', '21.02789,105.82479', 1, 0, 2, '2021-02-05 08:53:22'),
(57, 'demo', '21.00991,105.82309', 1, 0, 2, '2021-02-05 08:53:22'),
(58, 'demo', '21.00031,105.81595', 1, 0, 2, '2021-02-05 08:53:22'),
(60, 'demo', '21.04450,105.80580', 6, 0, 3, '2021-02-05 08:53:22'),
(61, 'demo', '21.03701,105.80657', 3, 2, 3, '2021-02-05 08:53:22'),
(62, 'demo', '21.02416,105.79822', 1, 2, 3, '2021-02-05 08:53:22'),
(63, 'demo', '21.01502,105.80538', 2, 3, 3, '2021-02-05 08:53:22'),
(64, 'demo', '21.00228,105.82263', 3, 1, 3, '2021-02-05 08:53:22');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `tbl_user`
--

CREATE TABLE `tbl_user` (
  `user_id` bigint(20) NOT NULL,
  `user_name` longtext COLLATE utf8mb4_unicode_ci,
  `user_username` varchar(450) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_password` varchar(450) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_phone_number` varchar(15) COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_birth_date` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `tbl_user`
--

INSERT INTO `tbl_user` (`user_id`, `user_name`, `user_username`, `user_password`, `user_phone_number`, `user_birth_date`) VALUES
(20, 'khoi', 'dtkhoimail@gmail.com', 'pbkdf2:sha256:150000$Ob27Q6kB$4ae6f83cd3d62a9364aa282aeb3a9789f25ed930576f8ba129dddcdff92c1661', '0123456789', '2021-02-04'),
(21, 'dsadsda', 'dtkhoimail30@gmail.com', 'pbkdf2:sha256:150000$Ael4Wpjh$765006e2b5cc2b4e2750cd28ae9fe4af4bce3ca0e3d7f9e8ebcc5bbfaad57c3d', '313213546545', '2021-02-05'),
(22, '11111111', 'dtkhoimail32@gmail.com', 'pbkdf2:sha256:150000$RsC7jeEz$96b4c2f3a89150957c20aeda03575416704ac42ee205269676a5e026d238951f', '313213546545', '2021-02-06'),
(23, 'zxcxzcxzc', 'dtkhoimail3cxzcx0@gmail.com', 'pbkdf2:sha256:150000$CWkxpsCe$4abbdc3d547d6fcf13f5d917790fac0060b30e722033843e837fdc8e14cf48bf', '0123456789', '2021-02-06'),
(25, 'vcvxc', 'dtkhoimail30@gmail.comcxvxcvxc', 'pbkdf2:sha256:150000$4tCuXdJU$ba49f683fa7dc4b1d0a7e6f6be8e6c6da0d3d336944acfbb5db9e174f7325c6f', '0123456789', '2021-02-05'),
(26, 'vcvxc', 'dtkhoimvcbvcbvcbail30@gmail.com', 'pbkdf2:sha256:150000$u30gVYzl$585ad61101c283d8c639ac985ae33ed8d5ab6ba8485c85e2806df6c239918fd4', '0123456789', '2021-02-05'),
(27, 'vcvxc', 'dtkhoimvcbvcbbnvcbail30@gmail.com', 'pbkdf2:sha256:150000$SUuSyoli$b5c5bae0fc5d1e919474612bc8aaf2218ce0ab5997fcffca3bb4c147ff463e24', '0123456789', '2021-02-05'),
(28, 'xcvxcv', 'dtkhoivcvcvcmail30@gmail.com', 'pbkdf2:sha256:150000$Ijb3eg4I$80a664d8cbf8fa36c992aed256bd5a599e3f6487b05b17246ec88529edb9b383', '0123456789', '2021-02-06'),
(29, 'xcvxcv', 'dtkhoivcvcvhcmail30@gmail.com', 'pbkdf2:sha256:150000$zGVuRuAK$6cf9822052dfe302523552fa46285f62a5377b6ea248b0dec920db2be7bdee08', '0123456789', '2021-02-06'),
(30, 'fsdf', 'dtkhoidsfsdmail30@gmail.com', 'pbkdf2:sha256:150000$hjpsPRV4$8789598989a84c58d3986fc004060d35a3acf5b3b254461a347a1d134e8d6346', '313213546545', '2021-02-06'),
(31, 'sdfsdfsdfsf', 'dtkhoimail40@gmail.com', 'pbkdf2:sha256:150000$ahwMlbXt$f2987f4c3bbc216f580b21611b65f79a14515dab26060cab9f1fbfd9c93c7dae', '0123456789', '2021-02-04'),
(32, 'sadsadsadsadsadsad', 'dtkhoimail41@gmail.com', 'pbkdf2:sha256:150000$VXLMixJa$6bd891ff9944068d56f3a78bfb9e9e57d7b1982ede97da69faba31020fb17403', '313213546545', '2021-02-05');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `trip`
--

CREATE TABLE `trip` (
  `id` int(11) NOT NULL,
  `list_user` varchar(1000) COLLATE utf8mb4_unicode_ci NOT NULL,
  `car_id` int(11) NOT NULL,
  `list_place` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `time_start` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `expected_time_finish` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `additional_information` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `note` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `trip`
--

INSERT INTO `trip` (`id`, `list_user`, `car_id`, `list_place`, `time_start`, `expected_time_finish`, `additional_information`, `note`) VALUES
(1, '1', 1, 'zxc', '2021-02-01 13:21:44', '2021-02-10 13:21:44', 'sdadadsad', 'asdsadsad'),
(2, '2', 1, 'zxc', '2021-02-01 13:21:44', '2021-02-10 18:00:00', 'sdadadsadvn', 'asdsadsadnvbb'),
(3, '3', 1, 'zxciooi', '2021-02-01 13:00:00', '2021-02-10 18:00:00', 'sdadadsadvn', 'asdsadsadnvbb');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `trip_running`
--

CREATE TABLE `trip_running` (
  `id` int(11) NOT NULL,
  `trip_id` int(11) NOT NULL,
  `list_user` varchar(1000) COLLATE utf8mb4_unicode_ci NOT NULL,
  `car_id` int(11) NOT NULL,
  `blank_seats` int(11) NOT NULL,
  `seated` int(11) NOT NULL,
  `name_start_point` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `start_point` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name_stop_point` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `stop_point` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `trip_running`
--

INSERT INTO `trip_running` (`id`, `trip_id`, `list_user`, `car_id`, `blank_seats`, `seated`, `name_start_point`, `start_point`, `name_stop_point`, `stop_point`) VALUES
(1, 1, 'zxcxzczxcxz', 1, 10, 10, '78 Duy Tan', '21.0247401,105.7883781', 'Lotee Center', '21.0320000,105.8128000'),
(2, 2, 'zxcxzczxcxz', 2, 10, 10, 'demo', '21.03207,105.82943', 'demo', '20.96711,105.77080'),
(3, 3, 'zxcxzczxcxz', 3, 10, 10, 'demo', '21.06251,105.80435', 'demo', '21.02188,105.89314');

--
-- Chỉ mục cho các bảng đã đổ
--

--
-- Chỉ mục cho bảng `car`
--
ALTER TABLE `car`
  ADD PRIMARY KEY (`id`);

--
-- Chỉ mục cho bảng `order_trip`
--
ALTER TABLE `order_trip`
  ADD PRIMARY KEY (`id`);

--
-- Chỉ mục cho bảng `point_running`
--
ALTER TABLE `point_running`
  ADD PRIMARY KEY (`p_id`);

--
-- Chỉ mục cho bảng `tbl_user`
--
ALTER TABLE `tbl_user`
  ADD PRIMARY KEY (`user_id`);

--
-- Chỉ mục cho bảng `trip`
--
ALTER TABLE `trip`
  ADD PRIMARY KEY (`id`),
  ADD KEY `car_id` (`car_id`);

--
-- Chỉ mục cho bảng `trip_running`
--
ALTER TABLE `trip_running`
  ADD PRIMARY KEY (`id`),
  ADD KEY `trip_id` (`trip_id`);

--
-- AUTO_INCREMENT cho các bảng đã đổ
--

--
-- AUTO_INCREMENT cho bảng `car`
--
ALTER TABLE `car`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT cho bảng `order_trip`
--
ALTER TABLE `order_trip`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=227;

--
-- AUTO_INCREMENT cho bảng `point_running`
--
ALTER TABLE `point_running`
  MODIFY `p_id` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=65;

--
-- AUTO_INCREMENT cho bảng `tbl_user`
--
ALTER TABLE `tbl_user`
  MODIFY `user_id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=33;

--
-- AUTO_INCREMENT cho bảng `trip`
--
ALTER TABLE `trip`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT cho bảng `trip_running`
--
ALTER TABLE `trip_running`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Các ràng buộc cho các bảng đã đổ
--

--
-- Các ràng buộc cho bảng `trip`
--
ALTER TABLE `trip`
  ADD CONSTRAINT `trip_ibfk_1` FOREIGN KEY (`car_id`) REFERENCES `car` (`id`);

--
-- Các ràng buộc cho bảng `trip_running`
--
ALTER TABLE `trip_running`
  ADD CONSTRAINT `trip_running_ibfk_1` FOREIGN KEY (`trip_id`) REFERENCES `trip` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
