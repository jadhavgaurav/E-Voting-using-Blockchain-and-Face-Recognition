# E-Voting System using Blockchain and Face Recognition

A secure and transparent e-voting application that leverages Ethereum Blockchain for immutable vote recording and Facial Recognition for robust voter authentication.

## 📌 Overview

This project implements a decentralized voting system designed to eliminate fraud and ensure election integrity. It combines a **PHP web interface** for administration and voting, a **Python-based Face Recognition service** for voter identity verification, and **Ethereum Smart Contracts** to store votes tamper-proof on the blockchain.

## ✨ Features

- **Secure Authentication**: Multimodal authentication using Face Verification (Python/OpenCV) and unique voter credentials.
- **Blockchain Integrity**: All votes are cast as transactions on the Ethereum blockchain, ensuring they cannot be altered or deleted.
- **Admin Dashboard**: comprehensive panel for Election Commission to manage elections, candidates, and view results.
- **User/Voter Panel**: User-friendly interface for voters to view candidates and cast votes securely.
- **Real-time Results**: fetching results directly from the blockchain to ensure accuracy.
- **Decentralized**: Removes the need for a central authority to validate votes after they are cast.

## 🛠️ Technology Stack

### Frontend & Backend (Web)

- **Languages**: PHP, HTML5, CSS3, JavaScript (jQuery).
- **Server**: Apache (via XAMPP).
- **Database**: MySQL (for user metadata and logs).

### Artificial Intelligence (Face Recognition)

- **Language**: Python 3.6+
- **Framework**: Flask (Microservice Architecture).
- **Libraries**: `face_recognition`, `dlib`, `OpenCV`, `scikit-learn`.

### Blockchain

- **Platform**: Ethereum.
- **Development Framework**: Truffle Suite.
- **Local Blockchain**: Ganache (Personal Blockchain for Ethereum development).
- **Smart Contracts**: Solidity (v0.8.0).
- **Client**: Web3.js / Web3.php (if applicable).

## ⚙️ Prerequisites

Ensure you have the following installed on your system:

1.  **XAMPP**: For running the PHP application and MySQL database.
2.  **Node.js & npm**: For installing Truffle and blockchain dependencies.
3.  **Python 3.6 - 3.8**: For running the face recognition API.
    - **Note**: `dlib` installation can be tricky on newer Python versions. Python 3.6 is recommended for compatibility with the provided `.whl` files.
4.  **Ganache**: To run a local Ethereum blockchain.
5.  **Git**: For cloning the repository.

## 🚀 Installation & Setup

### 1. Database Setup

1.  Start **Apache** and **MySQL** in XAMPP Control Panel.
2.  Open browser and go to `http://localhost/phpmyadmin`.
3.  Create a new database named `voting_db` (or check `config.php` / `db` folder for the exact name).
4.  Import the SQL file located in `Source code/db/` or `Source code/An_OnlineVotingQR_Admin/db/` into this database.

### 2. Blockchain Setup

1.  Open **Ganache** and create a new workspace.
2.  Navigate to the `Source code/Blockchain` directory in your terminal.
3.  Install dependencies:
    ```bash
    npm install
    ```
4.  Compile and deploy contracts:
    ```bash
    truffle compile
    truffle migrate --reset
    ```
5.  **Important**: Copy the deployed **Contract Address** from the terminal output. You will need to update this address in the web application's configuration file (usually `config.js` or `app.js` in the User/Admin folders).
6.  Ensure Ganache is running on port `8545` (check `truffle-config.js`).

### 3. Face Recognition API Setup

1.  Navigate to `Source code/An_OnlineVotingQR_User/python/faceknn/`.
2.  Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    _If `requirements.txt` is missing, install manually:_
    ```bash
    pip install flask flask_cors face_recognition opencv-python numpy
    ```
3.  Start the Python Flask server:
    ```bash
    python face_recognition_knn_web.py
    ```
    _This usually runs on `http://127.0.0.1:5000`._

### 4. Web Application Setup

1.  Move the **entire project folder** to your XAMPP `htdocs` directory (e.g., `C:\xampp\htdocs\E-Voting`).
2.  Configure Database Connection:
    - Check `db_config.php` or `connection.php` in both Admin and User folders.
    - Ensure credentials match your MySQL setup (default: User: `root`, Pass: ``).
3.  Configure Blockchain Connection:
    - Update the Smart Contract ABI and Address in the frontend JavaScript files (e.g., `app.js` or `web3_config.js`) if needed.

## 🖥️ Usage

1.  **Start Services**: Ensure XAMPP (Apache/MySQL), Ganache, and the Python Flask Server are running.
2.  **Admin Panel**:
    - Access `http://localhost/E-Voting/Source code/An_OnlineVotingQR_Admin/`.
    - Login to manage elections and authorize voters.
3.  **Voter Registration**:
    - Access `http://localhost/E-Voting/Source code/An_OnlineVotingQR_User/`.
    - Register a new account. The system will capture your face encoding.
4.  **Voting**:
    - Login as a voter.
    - The system will verify your face against the stored encoding.
    - Once verified, verify your ID/QR and cast your vote.
    - Confirm the transaction on the blockchain.

## 🤝 Contributing

Contributions are welcome!

1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.
