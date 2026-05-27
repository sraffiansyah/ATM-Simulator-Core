# 🏧 ATM Simulator
> Tugas Project Struktur Data — Python

---

## 🧩 Struktur Data yang Digunakan

| Struktur | Digunakan untuk |
|----------|----------------|
| **Stack** | Riwayat transaksi (push setiap transaksi, tampil dari terbaru) |
| **Dictionary** | Menyimpan & akses data rekening secara O(1) |

---

## ✨ Fitur

- **Login Rekening** — autentikasi nomor rekening + PIN
- **Tarik Uang** — validasi kelipatan Rp50.000 & saldo cukup
- **Setor Uang** — menambah saldo rekening
- **Riwayat Transaksi** — menggunakan Stack, tampil terbaru di atas
- **Cek Saldo via Scan Kartu** — OCR kamera real-time (tanpa login!)

---

## ⚙️ Instalasi

### 1. Install library Python
```bash
pip install -r requirements.txt
```

### 2. Install Tesseract OCR (engine-nya pytesseract)

**Windows:**
- Download installer: https://github.com/UB-Mannheim/tesseract/wiki
- Install, lalu tambahkan path ke environment variable, contoh:
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

### 3. Jalankan
```bash
python main.py
```

---

## 👤 Akun Demo

| No. Rekening | PIN  | Nama          | Saldo Awal     |
|-------------|------|---------------|----------------|
| 1234567890  | 1234 | Budi Santoso  | Rp5.000.000    |
| 0987654321  | 5678 | Siti Rahayu   | Rp12.500.000   |
| 1122334455  | 9012 | Andi Wijaya   | Rp3.750.000    |

---

## 📷 Cara Pakai Fitur Scan Kartu

1. Pilih menu **"2. Cek Saldo (Scan Kartu)"** dari menu utama
2. Jendela kamera akan terbuka
3. Tunjukkan kartu (atau kertas bertuliskan nomor rekening) ke kamera
4. Arahkan ke **kotak hijau (SCAN AREA)** di tengah layar
5. Saldo akan otomatis muncul di layar kamera
6. Tekan **Q** untuk menutup kamera

> 💡 **Tips:** Untuk demo/testing, tulis nomor rekening dengan spidol besar di kertas putih, lalu tunjukkan ke kamera. OCR bekerja lebih baik di pencahayaan terang.

---

## 🗂️ Tambah Akun Baru

Edit file `accounts.json`, tambahkan entri baru:

```json
"9988776655": {
    "nama": "Nama Kamu",
    "pin": "0000",
    "saldo": 1000000
    "no_kartu": "5816350255816350",
    "history": []
}
```
