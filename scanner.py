"""
Modul kamera + OCR untuk scan nomor kartu ATM.
Library: OpenCV, pytesseract
"""

import re
import cv2
import numpy as np
import pytesseract


# ─── Config ───────────────────────────────────────────────────────────────────

# Warna (BGR)
CLR_GREEN  = (0, 230, 100)
CLR_YELLOW = (0, 220, 255)
CLR_WHITE  = (255, 255, 255)
CLR_BLACK  = (0, 0, 0)
CLR_GRAY   = (80, 80, 80)

FONT       = cv2.FONT_HERSHEY_SIMPLEX
OCR_CFG    = r"--oem 3 --psm 11 -c tessedit_char_whitelist=0123456789"


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _draw_overlay(frame: np.ndarray, scan_rect: tuple, status: str,
                  found_no: str | None, saldo_info: str | None, nama_info: str | None):
    """Gambar UI overlay di atas frame kamera."""
    h, w = frame.shape[:2]
    x, y, rw, rh = scan_rect

    # Semi-transparent background strip atas
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 55), CLR_BLACK, -1)
    cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)

    # Judul
    cv2.putText(frame, "ATM SIMULATOR - CEK SALDO", (12, 30),
                FONT, 0.65, CLR_GREEN, 2)
    cv2.putText(frame, "Arahkan kartu ke area scan", (12, 50),
                FONT, 0.45, CLR_YELLOW, 1)

    # Kotak scan area
    cv2.rectangle(frame, (x, y), (x + rw, y + rh), CLR_GREEN, 2)

    # Label di atas kotak
    cv2.rectangle(frame, (x, y - 26), (x + rw, y), CLR_GREEN, -1)
    cv2.putText(frame, "SCAN AREA", (x + 6, y - 7),
                FONT, 0.45, CLR_BLACK, 1)

    # Sudut dekoratif
    corner_len = 20
    corners = [
        (x, y, 1, 1), (x + rw, y, -1, 1),
        (x, y + rh, 1, -1), (x + rw, y + rh, -1, -1),
    ]
    for cx, cy, dx, dy in corners:
        cv2.line(frame, (cx, cy), (cx + dx * corner_len, cy), CLR_YELLOW, 3)
        cv2.line(frame, (cx, cy), (cx, cy + dy * corner_len), CLR_YELLOW, 3)

    # Panel status bawah
    panel_y = h - 90
    overlay2 = frame.copy()
    cv2.rectangle(overlay2, (0, panel_y), (w, h), CLR_BLACK, -1)
    cv2.addWeighted(overlay2, 0.65, frame, 0.35, 0, frame)

    if found_no:
        cv2.putText(frame, f"No. Kartu: {found_no}", (12, panel_y + 22),
                    FONT, 0.55, CLR_GREEN, 2)
        if saldo_info:
            cv2.putText(frame, saldo_info, (12, panel_y + 50),
                        FONT, 0.65, CLR_YELLOW, 2)
        if nama_info:
            cv2.putText(frame, nama_info, (12, panel_y + 75),
                        FONT, 0.45, CLR_WHITE, 1)
    else:
        cv2.putText(frame, status, (12, panel_y + 30),
                    FONT, 0.55, CLR_WHITE, 1)

    cv2.putText(frame, "Tekan Q untuk keluar", (w - 195, h - 8),
                FONT, 0.4, CLR_GRAY, 1)


def _preprocess(roi: np.ndarray) -> np.ndarray:
    """Preprocessing ROI supaya OCR lebih akurat."""
    gray    = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    scaled  = cv2.resize(gray, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)
    blurred = cv2.GaussianBlur(scaled, (3, 3), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh


def _extract_card_number(text: str) -> str | None:
    """Cari sequence angka 10–19 digit dari teks OCR."""
    digits = re.findall(r"\d{10,19}", text.replace(" ", "").replace("\n", ""))
    return digits[0] if digits else None


# ─── Main Scanner ─────────────────────────────────────────────────────────────

def scan_card(atm_instance) -> str | None:
    """
    Buka kamera, scan nomor kartu via OCR, tampilkan saldo di overlay.
    Return: nomor rekening yang terdeteksi & valid, atau None jika dibatalkan.
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Kamera tidak bisa dibuka.")
        return None

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 500)

    found_no   = None
    saldo_info = None
    nama_info  = None
    status     = "Menunggu kartu..."
    hold_count = 0          # frame counter setelah kartu ketemu

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        h, w = frame.shape[:2]

        # Scan area: tengah frame, proporsi kartu kredit
        rw, rh = int(w * 0.65), int(h * 0.35)
        x, y   = (w - rw) // 2, (h - rh) // 2
        scan_rect = (x, y, rw, rh)

        # OCR setiap 10 frame supaya ga berat
        if hold_count == 0 and cv2.waitKey(1) % 256 != ord("q"):
            roi        = frame[y:y + rh, x:x + rw]
            processed  = _preprocess(roi)
            raw_text   = pytesseract.image_to_string(processed, config=OCR_CFG)
            detected   = _extract_card_number(raw_text)

            if detected and atm_instance.account_exists(detected):
                found_no   = detected
                saldo      = atm_instance.get_saldo(detected)
                saldo_info = f"Saldo: Rp{saldo:,.0f}"
                nama_info  = None          # privasi: tidak tampilkan nama
                status     = "Kartu dikenali!"
                hold_count = 90            # tahan 90 frame (~3 detik)
            elif detected:
                status = f"Nomor {detected} tidak terdaftar."
            else:
                status = "Menunggu kartu..."

        _draw_overlay(frame, scan_rect, status, found_no, saldo_info, nama_info)
        cv2.imshow("ATM Simulator - Cek Saldo", frame)

        key = cv2.waitKey(1) & 0xFF

        if hold_count > 0:
            hold_count -= 1
            if hold_count == 0:
                # Reset setelah ditampilkan
                found_no = saldo_info = nama_info = None
                status = "Menunggu kartu..."

        if key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    return found_no     # kembalikan no. rek terakhir yang valid (atau None)
