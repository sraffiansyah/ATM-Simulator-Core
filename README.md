# 🏧 ATM Simulator

[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)](https://atm-generator-by-vyyy.netlify.app)

> 💻 **Console-Based Banking Simulation** | Built with Python, OOP & Computer Vision  
>  **Frontend Companion:** [ATM Card Designer (Web)](https://atm-generator-by-vyyy.netlify.app/)

---

## 🧩 Struktur Data yang Digunakan

| Struktur | Digunakan untuk |
|----------|----------------|
| **Stack** | Riwayat transaksi (push setiap transaksi, tampil dari terbaru) |
| **Dictionary** | Menyimpan & akses data rekening secara O(1) |

---

## ✨ Features

- 🔐 **Secure Login System** – Account authentication with PIN verification
- 💸 **Core Banking Operations** – Withdraw, Deposit, Transfer (with full validation)
- 📜 **Transaction History** – LIFO tracking using a custom Stack implementation
- 📷 **OCR Card Scanner** – Real-time camera capture to read card numbers & fetch balance (OpenCV + Tesseract)
- 💾 **Persistent Storage** – Account data & history saved to JSON between sessions
- 🖥️ **Clean CLI UI** – Structured menus, input validation, and formatted currency output

---

## 🛠️ Tech Stack & Data Structures

| Component | Technology / Pattern |
|-----------|----------------------|
| **Language** | Python 3.8+ |
| **Architecture** | OOP, Modular Design (`ATM`, `Stack` classes) |
| **Data Structures** | `Dictionary` (O(1) account lookup), `Stack` (LIFO transaction history) |
| **Persistence** | JSON file-based storage |
| **Computer Vision** | OpenCV (`cv2`), `pytesseract` (OCR engine) |
| **UI** | Terminal/CLI with formatted tables & input validation |

---

## ⚙️ Installation

### 1. Installation library Python
```bash
pip install -r requirements.txt
```

### 2. Install Tesseract OCR (engine-nya pytesseract)

**Windows:**
- Download installer: https://github.com/UB-Mannheim/tesseract/wiki
- Install, then add the path to the environment variable, for example:
  ```
  C:\Program Files\Tesseract-OCR
  ```

**macOS:**
```bash
brew install tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install tesseract-ocr
```

### 3. Running
```bash
python main.py
```

---

## 👤 Demo Account

| Num. Account | PIN  | Name          | Beginning balance     |
|-------------|------|---------------|----------------|
| 1234567890  | 1234 | Budi Santoso  | Rp5.000.000    |
| 0987654321  | 5678 | Siti Rahayu   | Rp12.500.000   |
| 1122334455  | 9012 | Andi Wijaya   | Rp3.750.000    |

---

## 📷 How to Use the Card Scan Feature

1. Select the menu **"2. Check Balance (Scan Card)"** from the main menu
2. The camera window will open
3. Show the card (or paper with the account number on it) to the camera.
4. Aim at the **green box (SCAN AREA)** in the center of the screen
5. The balance will automatically appear on the camera screen.
6. Press **Q** to close the camera

> 💡 **Tip:** For demo/testing, write the account number with a large marker on a white sheet of paper and show it to the camera. OCR works better in bright lighting.

---

## 🗂️ Add New Account

Edit file `accounts.json`, add new entry:

```json
"9988776655": {
    "name": "Your name",
    "pin": "0000",
    "balance": 1000000
    "card_number": "5816350255816350",
    "history": []
}
```
