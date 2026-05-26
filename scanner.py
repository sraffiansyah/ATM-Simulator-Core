"""
Modul kamera + OCR untuk scan nomor kartu ATM.
Library: OpenCV, pytesseract
Nomor kartu: 16 digit (tanpa spasi)
"""

import re
import cv2
import numpy as np
import pytesseract


# ─── Config ───────────────────────────────────────────────────────────────────

CLR_GREEN  = (0, 230, 100)
CLR_YELLOW = (0, 220, 255)
CLR_WHITE  = (255, 255, 255)
CLR_BLACK  = (0, 0, 0)

FONT    = cv2.FONT_HERSHEY_SIMPLEX
OCR_CFG = r"--oem 3 --psm 11 -c tessedit_char_whitelist=0123456789"


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _draw_overlay(frame: np.ndarray, scan_rect: tuple, status: str,
                    found_kartu: str | None, saldo_info: str | None):
    h, w = frame.shape[:2]
    x, y, rw, rh = scan_rect

    # Strip atas
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 58), CLR_BLACK, -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
    cv2.putText(frame, "ATM SIMULATOR - CEK SALDO", (12, 32),
                FONT, 0.65, CLR_GREEN, 2)
    cv2.putText(frame, "Arahkan kartu ke area scan  |  Tekan Q untuk keluar", (12, 52),
                FONT, 0.4, CLR_YELLOW, 1)

    # Kotak scan
    cv2.rectangle(frame, (x, y), (x + rw, y + rh), CLR_GREEN, 2)
    cv2.rectangle(frame, (x, y - 28), (x + rw, y), CLR_GREEN, -1)
    cv2.putText(frame, "SCAN AREA — 16 DIGIT", (x + 6, y - 8),
                FONT, 0.42, CLR_BLACK, 1)

    # Sudut dekoratif
    for cx, cy, dx, dy in [(x,y,1,1),(x+rw,y,-1,1),(x,y+rh,1,-1),(x+rw,y+rh,-1,-1)]:
        cv2.line(frame, (cx, cy), (cx + dx*22, cy), CLR_YELLOW, 3)
        cv2.line(frame, (cx, cy), (cx, cy + dy*22), CLR_YELLOW, 3)

    # Panel bawah
    panel_y = h - 85
    overlay2 = frame.copy()
    cv2.rectangle(overlay2, (0, panel_y), (w, h), CLR_BLACK, -1)
    cv2.addWeighted(overlay2, 0.65, frame, 0.35, 0, frame)

    if found_kartu:
        # Tampilkan format XXXX XXXX XXXX XXXX
        fmt = " ".join(found_kartu[i:i+4] for i in range(0, len(found_kartu), 4))
        cv2.putText(frame, f"No. Kartu : {fmt}", (12, panel_y + 24),
                    FONT, 0.52, CLR_GREEN, 2)
        if saldo_info:
            cv2.putText(frame, saldo_info, (12, panel_y + 58),
                        FONT, 0.7, CLR_YELLOW, 2)
    else:
        cv2.putText(frame, status, (12, panel_y + 38),
                    FONT, 0.55, CLR_WHITE, 1)


def _preprocess(roi: np.ndarray) -> np.ndarray:
    gray   = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    scaled = cv2.resize(gray, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)
    blur   = cv2.GaussianBlur(scaled, (3, 3), 0)
    _, th  = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return th


def _extract_card_number(text: str) -> str | None:
    """
    Cari 16 digit berurutan dari hasil OCR.
    Hapus spasi dulu — kartu di layar ada spasi tiap 4 digit.
    """
    # Hapus semua non-digit, lalu cari sequence 16 digit
    digits_only = re.sub(r"\D", "", text)
    match = re.search(r"\d{16}", digits_only)
    return match.group() if match else None


# ─── Main Scanner ─────────────────────────────────────────────────────────────

def scan_card(atm_instance) -> str | None:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Kamera tidak bisa dibuka.")
        return None

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 500)

    found_kartu = None
    saldo_info  = None
    status      = "Menunggu kartu..."
    hold_count  = 0
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        h, w      = frame.shape[:2]
        rw, rh    = int(w * 0.70), int(h * 0.32)
        x, y      = (w - rw) // 2, (h - rh) // 2
        scan_rect = (x, y, rw, rh)

        frame_count += 1

        if hold_count == 0 and frame_count % 10 == 0:
            roi       = frame[y:y + rh, x:x + rw]
            processed = _preprocess(roi)
            raw_text  = pytesseract.image_to_string(processed, config=OCR_CFG)
            detected  = _extract_card_number(raw_text)

            if detected and atm_instance.card_exists(detected):
                no_rek      = atm_instance.find_by_card(detected)
                saldo       = atm_instance.get_saldo(no_rek)
                found_kartu = detected
                saldo_info  = f"Saldo : Rp{saldo:,.0f}".replace(",", ".")
                status      = "Kartu dikenali!"
                hold_count  = 90
            elif detected:
                status = f"Kartu {detected[:4]} **** **** tidak terdaftar."
            else:
                status = "Menunggu kartu..."

        _draw_overlay(frame, scan_rect, status, found_kartu, saldo_info)
        cv2.imshow("ATM Simulator - Cek Saldo", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        if hold_count > 0:
            hold_count -= 1
            if hold_count == 0:
                found_kartu = saldo_info = None
                status = "Menunggu kartu..."

    cap.release()
    cv2.destroyAllWindows()
    return found_kartu
