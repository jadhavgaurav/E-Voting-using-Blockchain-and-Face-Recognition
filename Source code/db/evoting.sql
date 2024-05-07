-- phpMyAdmin SQL Dump
-- version 5.0.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 15, 2022 at 06:14 AM
-- Server version: 10.4.11-MariaDB
-- PHP Version: 7.4.1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `evoting`
--

-- --------------------------------------------------------

--
-- Table structure for table `admininfo`
--

CREATE TABLE `admininfo` (
  `ID` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(50) NOT NULL,
  `mobile` varchar(12) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `admininfo`
--

INSERT INTO `admininfo` (`ID`, `name`, `email`, `password`, `mobile`) VALUES
(1, 'admin', 'admin@gmail.com', '123', '123');

-- --------------------------------------------------------

--
-- Table structure for table `constituency`
--

CREATE TABLE `constituency` (
  `Id` int(11) NOT NULL,
  `area` varchar(255) DEFAULT NULL,
  `central` varchar(255) DEFAULT NULL,
  `state` varchar(255) DEFAULT NULL,
  `local` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `constituency`
--

INSERT INTO `constituency` (`Id`, `area`, `central`, `state`, `local`) VALUES
(1, 'Srikakulam', 'Bapatla (SC)', 'Andhra Pradesh', 'Bapatla'),
(2, 'Arunachal West', 'Arunachal West (SC)', 'Arunachal Pradesh', 'Arunachal West (SC)'),
(3, 'Arunachal East ', 'Arunachal East', 'Arunachal Pradesh ', 'Arunachal East '),
(4, 'Valmiki Nagar', 'THIRUVALLUR (SC)', 'Valmiki Nagar (SC)', 'Valmiki Nagar (SC)'),
(5, 'Avadi', 'THIRUVALLUR (SC)', 'Avadi', 'Avadi'),
(6, 'Madavaram', 'THIRUVALLUR (SC)', 'Madavaram', 'Madavaram'),
(7, 'Maharajganj', 'Bihar', 'Maharajganj', 'Maharajganj'),
(8, 'Dr.Radhakrishnan Nagar', 'CHENNAI NORTH', 'Dr.Radhakrishnan Nagar', 'Dr.Radhakrishnan Nagar'),
(9, 'Dr.Radhakrishnan Nagar', 'Dr.Radhakrishnan Nagar', 'Perambur', 'Dr.Radhakrishnan Nagar'),
(10, 'Perambur ', 'Perambur', 'CHENNAI NORTH ', 'Perambur '),
(11, 'Raipur', 'Raipur', 'Chhattisgarh', 'Raipur'),
(12, 'North Goa', 'North Goa', 'Goa', 'North Goa'),
(13, 'South Goa', 'South Goa', 'Goa', 'South Goa'),
(14, 'Kachchh (SC)', 'Kachchh (SC)', 'Gujarat', 'Kachchh (SC)'),
(15, 'Ahmedabad East', 'Ahmedabad East', 'Gujarat', 'Ahmedabad East'),
(16, 'Ahmedabad West (SC)', 'Ahmedabad West (SC)', 'Gujarat', 'Ahmedabad West (SC)'),
(17, 'Ambala', 'Ambala', 'Haryana', 'Ambala'),
(18, 'Bijapur SC', 'Bijapur SC', 'Karnataka', 'Bijapur SC'),
(19, 'Nandurbar (ST)', 'Nandurbar (ST)', 'Maharashtra', 'Nandurbar (ST)'),
(20, 'Dhule', 'Dhule', 'Maharashtra', 'Dhule'),
(21, 'Harbour ', 'CHENNAI CENTRAL', 'Harbour ', 'Harbour '),
(22, 'Nashik', 'Nashik', 'Mumbai Central', 'Nashik'),
(23, 'Palghar (ST)', 'Palghar (ST)', 'Maharastra', 'Palghar (ST)'),
(24, 'Bhiwandi', 'Bhiwandi', 'Maharastra', 'Bhiwandi'),
(25, 'Kalyan', 'Kalyan', 'Maharashtra', 'Kalyan'),
(26, 'Thane', 'Thane', 'Maharashtra', 'Thane'),
(27, 'Mumbai North', 'Mumbai North', 'Maharashtra', 'Mumbai North'),
(28, 'Mumbai North West', 'Mumbai North West', 'Mumbai Central', 'Mumbai North West'),
(29, 'Mumbai North East', 'Mumbai North East', 'Maharashtra', 'Mumbai North East'),
(30, 'Mumbai North Central', 'Mumbai North Central', 'Mumbai Central', 'Mumbai North Central'),
(31, 'Mumbai South', 'Mumbai South (SC)', 'Maharashtra', 'Mumbai South'),
(32, 'Raigad', 'Raigad', 'Maharashtra', 'Raigad'),
(33, 'Pune ', 'Pune (SC)', 'Maharashtra', 'Pune (SC)'),
(34, 'Madurantakam', 'KANCHEEPURAM (SC)', 'Madurantakam (SC)', 'Madurantakam (SC)'),
(35, 'Uthiramerur', 'KANCHEEPURAM (SC)', 'Uthiramerur', 'Uthiramerur'),
(36, 'Kancheepuram', 'KANCHEEPURAM (SC)', 'Kancheepuram', 'Kancheepuram');

-- --------------------------------------------------------

--
-- Table structure for table `electioninfo`
--

CREATE TABLE `electioninfo` (
  `ID` int(11) NOT NULL,
  `ename` varchar(200) NOT NULL,
  `edate` varchar(100) NOT NULL,
  `etype` varchar(100) NOT NULL,
  `econ` varchar(200) DEFAULT NULL,
  `STATUS` varchar(10) NOT NULL,
  `subtype` varchar(200) NOT NULL,
  `cname` varchar(200) NOT NULL,
  `flag` varchar(200) NOT NULL,
  `stime` time NOT NULL DEFAULT '12:03:00',
  `etime` time NOT NULL DEFAULT '01:00:00'
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `electioninfo`
--

INSERT INTO `electioninfo` (`ID`, `ename`, `edate`, `etype`, `econ`, `STATUS`, `subtype`, `cname`, `flag`, `stime`, `etime`) VALUES
(1, 'by-election', '2019-07-23', 'state', NULL, '2', 'Villivakkam', 'thiru', '4480db84ef86e524ed1124a0cba306c9.jpg', '15:25:00', '18:00:00'),
(2, 'by-election', '2019-07-23', 'state', NULL, '2', 'Villivakkam', 'maran', '953a5289ccf9ee4775dd2a5fc402e004.png', '15:25:00', '18:00:00'),
(3, 'by-election', '2019-07-23', 'state', NULL, '2', 'Villivakkam', 'babu', 'f1712d5f56babca7828535140ec27f6c.jpg', '15:25:00', '18:00:00'),
(4, 'sss', '2022-03-02', 'central', NULL, '0', 'CHENNAI SOUTH', 'ramkee', '3f60bd6435fb96f39b99297be4cd0e73.png', '12:22:00', '01:22:00'),
(5, 'sss', '2022-03-18', 'local', NULL, 'A', 'Villivakkam', 'maran', '41393bb0a6b0699fb9bac8e7aa4191cd.png', '12:29:00', '00:34:00'),
(6, 'sss', '2022-03-18', 'local', NULL, '2', 'Villivakkam', 'maran', '7d1a555ed741dc3d97d47660d0202d0c.png', '12:29:00', '00:34:00'),
(7, 'sss', '2022-03-18', 'local', NULL, '1', 'Poonamallee (SC)', 'raj', '889d0e2e038312241ce8a01e2d426606.png', '11:11:00', '04:12:00'),
(8, 'kkk', '2022-03-19', 'local', NULL, '2', 'Gummidipoondi', 'thiru', 'c46b5e08ec3c79880ccf75ceb72c297e.png', '16:35:00', '17:00:00'),
(9, 'kkk', '2022-03-19', 'local', NULL, '2', 'Gummidipoondi', 'karthick', 'dc1fc05e6a06523fafc960110a39db26.png', '16:35:00', '17:00:00'),
(10, 'kkk', '2022-03-24', 'local', NULL, 'A', 'Ponneri (SC)', 'raja', '510510edca2e52c3fca148a2035e40fd.png', '10:15:00', '03:20:00'),
(11, 'kkk', '2022-03-24', 'local', NULL, 'A', 'Ponneri (SC)', 'babu', '37126875fc01cfef6b2ec9f9e0633b9f.png', '10:15:00', '03:20:00'),
(12, 'sss', '2022-03-23', 'local', NULL, 'A', 'Ponneri (SC)', 'raja', '3d81e1f896afd7cabd2af02e304476c8.png', '10:17:00', '00:20:00'),
(13, 'rrr', '2022-03-23', 'local', NULL, '2', 'Ponneri (SC)', 'karthick', '2255a7cdf8427cd4f327e56bbd9e2ccb.png', '10:25:00', '15:26:00'),
(21, 'testelection', '2022-12-10', 'local', NULL, 'A', 'Ponneri (SC)', 'thiru', '47faf0c38dd8fa4336a483c1cdd85e36.png', '12:00:00', '12:00:00'),
(22, 'testelection', '2022-12-10', 'local', NULL, 'A', 'Ponneri (SC)', 'raja', '6c158cbcadb087cc57ea0cb1c92e1900.jpg', '12:00:00', '12:00:00'),
(23, 'testelection', '2022-12-10', 'local', NULL, 'A', 'Ponneri (SC)', 'ramkee', '913a0f91e84b5fbed75505ebfa60459e.jpg', '12:00:00', '12:00:00'),
(24, 'testelection', '2022-12-10', 'local', NULL, 'A', 'Ponneri (SC)', 'thiru', '385c86fe29a21c04cdb6edee713b35f1.png', '12:00:00', '12:00:00'),
(25, 'testelection', '2022-12-10', 'local', NULL, 'A', 'Ponneri (SC)', 'raja', 'dcbf8acb2f3fd90d3708ca50f51edfde.jpg', '12:00:00', '12:00:00'),
(26, 'testelection', '2022-12-10', 'local', NULL, 'A', 'Ponneri (SC)', 'ramkee', '762bc65dfc7b2a38081a51132f071441.jpg', '12:00:00', '12:00:00'),
(27, 'asdsad', '2022-12-15', 'local', NULL, '0', 'Gummidipoondi', 'thiru', 'bbf50ed93818699aa42960d0bff0b242.png', '12:00:00', '12:00:00'),
(28, 'asdsad', '2022-12-15', 'local', NULL, '0', 'Gummidipoondi', 'kar', '700d6ab2fca67c18c9ed003ac9c0dca3.jpg', '12:00:00', '12:00:00'),
(33, 'XYZ Election', '2022-12-10', 'local', NULL, '0', 'Ponneri (SC)', 'thiru', 'ee9dd903ad824a3e61cd732a76a1bda6.png', '09:00:00', '12:00:00'),
(34, 'XYZ Election', '2022-12-08', 'local', NULL, '0', 'Ponneri (SC)', 'kar', '217c24e202453e7323c30ae13071a573.jpg', '09:00:00', '12:00:00'),
(66, 'qwerty', '2022-12-08', 'local', NULL, '2', 'Ponneri (SC)', 'thiru', '1bb82936e0668ccea33c3891cf27b566.png', '09:00:00', '12:00:00'),
(67, 'qwerty', '2022-12-08', 'local', NULL, '2', 'Ponneri (SC)', 'raja', '7042cee028fcc7ded4b04abdceb1e25e.jpg', '09:00:00', '12:00:00'),
(68, 'qwerty', '2022-12-10', 'local', NULL, '2', 'Ponneri (SC)', 'thiru', '681bb4ce18d7414a82a66488e6f1a4db.png', '09:00:00', '12:00:00'),
(69, 'qwerty', '2022-12-10', 'local', NULL, '2', 'Ponneri (SC)', 'ramkee', '183d49c9e617d05c83d4851ee428131e.jpg', '09:00:00', '12:00:00'),
(70, 'ytrewq', '2022-12-10', 'local', NULL, '0', 'Ponneri (SC)', 'Select', '679a02ed7550e50d1ac4ecd6ba9df92f.png', '09:00:00', '14:00:00'),
(71, 'ytrewq', '2022-12-10', 'local', NULL, '0', 'Ponneri (SC)', 'ramkee', '4da32a8fba5faa1fcc207b804db9661b.jpg', '09:00:00', '14:00:00'),
(72, 'postelection', '2022-12-15', 'local', NULL, '1', 'Anna Nagar', 'thiru', 'da1dcb55cf21ae802c0a17f85c4b077f.png', '09:00:00', '19:00:00'),
(73, 'postelection', '2022-12-15', 'local', NULL, '1', 'Anna Nagar', 'raja', 'b8d59eb42f7da0348a245541dbc958e8.jpg', '09:00:00', '19:00:00'),
(74, 'postelection', '2022-12-15', 'local', NULL, '2', 'Anna Nagar', 'babu', '10c67c16b4b61ca618a7c7894d3e5501.jpg', '09:00:00', '19:00:00'),
(75, 'dsfdsf', '2022-12-09', 'local', NULL, 'A', 'Ponneri (SC)', 'thiru', '0c776be045f5f8fce4553b5f9f3de10a.png', '06:00:00', '12:00:00');

-- --------------------------------------------------------

--
-- Table structure for table `userinfo`
--

CREATE TABLE `userinfo` (
  `ID` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(50) NOT NULL,
  `mobile` varchar(12) NOT NULL,
  `address` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `voterinfo`
--

CREATE TABLE `voterinfo` (
  `ID` int(11) NOT NULL,
  `vimage` varchar(100) NOT NULL,
  `idproof` varchar(100) NOT NULL,
  `vaadhar` varchar(255) NOT NULL,
  `vname` varchar(50) NOT NULL,
  `password` varchar(100) NOT NULL,
  `email` varchar(150) NOT NULL,
  `vid` varchar(12) NOT NULL,
  `dob` varchar(12) NOT NULL,
  `area` varchar(255) DEFAULT NULL,
  `status` varchar(100) NOT NULL,
  `baddress` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `voterinfo`
--

INSERT INTO `voterinfo` (`ID`, `vimage`, `idproof`, `vaadhar`, `vname`, `password`, `email`, `vid`, `dob`, `area`, `status`, `baddress`) VALUES
(1, '22ccc31136d064b446e34e0c2af3c03a.png', '', '111111111111', 'thiru', 'thiru', '', '1111111111', '1996-05-04', 'Villivakkam', 'Accepted', ''),
(2, 'b66afae65160993fd1f373068f12a9bc.png', '', '666666666666', 'ramkee', 'ramkee', '', '8888888888', '1996-05-04', 'Villivakkam', 'Accepted', ''),
(3, 'd981ea7ca8d3dfd248ead348670e4e47.png', '', '333333333333', 'maran', 'maran', '', '3333333333', '1996-05-04', 'Villivakkam', 'Accepted', ''),
(4, 'd3a705017888c77ed6a7e2f95da7a930.png', '', '444444444444', 'babu', 'babu', '', '4444444444', '1996-05-04', 'Villivakkam', 'Accepted', ''),
(5, 'eccc4d35c3445b75ab0ddfd757abccd2.jpeg', '', '121212121212', 'thiru', 'thiru', '', '1212121212', '1987-06-13', 'Villivakkam', 'Accepted', ''),
(9, '1c7f45709b35a5e0e28d1a00f9cfd651.jpg', '', '090909090909', 'dfgd', 'dfgd', '', '1234321234', '1995-02-11', 'Harbour ', 'Rejected', ''),
(10, '009f20442cc7754101738535f690e15e.jpg', '', '343434543454', 'sun', 'sun', '', '3243234543', '1997-10-24', 'Villivakkam', 'Accepted', ''),
(12, '602768f87470667b477a42286d6ff639.png', '', '123412341234', 'raj', 'raj', '', '0000000000', '2001-03-01', 'Virugampakkam', 'Accepted', ''),
(14, '7e5a2dd94006796347c6b23fa5f0736d.png', '', '345665433456', 'kar', 'kar', '', '7777777777', '2000-02-11', 'Mylapore', 'Accepted', ''),
(15, '22c57335ebc597c6bbd08a1b0e961143.png', '', '123455432123', 'karthick', 'karthi', '', '4545454445', '2001-03-01', 'Gummidipoondi', 'Accepted', ''),
(18, '3f5329f88b6843efc8564c2e5146019b.png', '', '123455432112', 'sudha', 'sudha', '', '1234567801', '2000-01-05', 'Anna Nagar', 'Accepted', '0xB0859495A670cC03104586484fCE95D7673f60e2'),
(21, '639856afc2185.png', '', '123456789321', 'qwerty', 'qwerty', 'qwerty@gmail.com', '9876543120', '1997-01-02', 'Ponneri', 'Pending', '0xB0859495A670cC03104586484fCE95D7673f60e2'),
(23, '6398625a288d0.png', '', '321321321321', 'abc', 'abc', 'abc@gmail.com', '3213213210', '1991-01-12', 'Poonamallee', 'Pending', '0xB0859495A670cC03104586484fCE95D7673f60e2'),
(32, '63986afe78e1c.png', '', '123456654321', 'test', 'test', 'test@gmail.com', '1234554321', '2000-12-12', 'Madavaram', 'Pending', '0xB0859495A670cC03104586484fCE95D7673f60e2'),
(41, '63987042ee614.png', '', '123456654327', '12qw', 'wqew', 'sadas', '1234554328', '2000-12-12', 'Kolathur ', 'Pending', '0xB0859495A670cC03104586484fCE95D7673f60e2'),
(102, '6399bfcfd6a68.png', '', '678905432112', 'qwerty', '12345', 'qwerty@gmail.com', '6789054321', '2000-12-12', 'Perambur', 'Pending', '0xB0859495A670cC03104586484fCE95D7673f60e2'),
(103, '6399c03b9141d.png', '', '678905432190', 'erewr', 'ewr', 'erer@gmail.com', '9898989898', '2000-12-12', 'Perambur', 'Pending', '0xB0859495A670cC03104586484fCE95D7673f60e2');

-- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

--
-- Table structure for table `votes`
--

CREATE TABLE `votes` (
  `Id` int(11) NOT NULL,
  `voter` varchar(255) DEFAULT NULL,
  `candidate` varchar(255) DEFAULT NULL,
  `time` varchar(255) DEFAULT NULL,
  `election` varchar(255) DEFAULT NULL,
  `etype` varchar(255) DEFAULT NULL,
  `esubtype` varchar(255) DEFAULT NULL,
  `txhash` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `votes`
--

INSERT INTO `votes` (`Id`, `voter`, `candidate`, `time`, `election`, `etype`, `esubtype`, `txhash`) VALUES
(1, '111111111111', '3', '2019-07-23 15:24:34', 'by-election', 'state', 'Villivakkam', ''),
(10, '333333333333', '3', '2019-07-25 10:55:21', 'by-election', 'state', 'Villivakkam', ''),
(11, '444444444444', '2', '2019-07-27 17:17:21', 'by-election', 'state', 'Villivakkam', ''),
(14, '345665433456', '4', '2022-03-18 04:28:48', 'sss', 'central', 'CHENNAI SOUTH', ''),
(73, '', '27', '2022-12-09 16:57:38', 'postelection', 'local', 'Ponneri (SC)', '0xd870e2ad74c848de9ce2dc8ac2defceff9fb0033f11a09d4850c9ce887b60603'),
(74, '', '27', '2022-12-09 17:04:23', 'postelection', 'local', 'Ponneri (SC)', '0xa0b23ed2c298eb9fc24ed45b4d4da8c35cc46f4243f0d5caaae033bab74ed16f'),
(75, '454545454545', '27', '2022-12-09 17:07:06', 'postelection', 'local', 'Ponneri (SC)', '0x38d7445cb03f2da2adf397756e2cb61e349cc84fc9269acb87d7dc59f260112c');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admininfo`
--
ALTER TABLE `admininfo`
  ADD PRIMARY KEY (`ID`),
  ADD UNIQUE KEY `Email` (`email`);

--
-- Indexes for table `constituency`
--
ALTER TABLE `constituency`
  ADD PRIMARY KEY (`Id`);

--
-- Indexes for table `electioninfo`
--
ALTER TABLE `electioninfo`
  ADD PRIMARY KEY (`ID`);

--
-- Indexes for table `userinfo`
--
ALTER TABLE `userinfo`
  ADD PRIMARY KEY (`ID`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `voterinfo`
--
ALTER TABLE `voterinfo`
  ADD PRIMARY KEY (`ID`),
  ADD UNIQUE KEY `vaadhar` (`vaadhar`),
  ADD UNIQUE KEY `vid` (`vid`);

--
-- Indexes for table `votes`
--
ALTER TABLE `votes`
  ADD PRIMARY KEY (`Id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admininfo`
--
ALTER TABLE `admininfo`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `constituency`
--
ALTER TABLE `constituency`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=37;

--
-- AUTO_INCREMENT for table `electioninfo`
--
ALTER TABLE `electioninfo`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=76;

--
-- AUTO_INCREMENT for table `userinfo`
--
ALTER TABLE `userinfo`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `voterinfo`
--
ALTER TABLE `voterinfo`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=104;

--
-- AUTO_INCREMENT for table `votes`
--
ALTER TABLE `votes`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=77;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
