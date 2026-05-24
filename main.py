"""
╔══════════════════════════════════════╗
║        ATM SIMULATOR — main.py       ║
║  Struktur Data: Stack + Dictionary   ║
╚══════════════════════════════════════╝
"""

import os
import sys
from getpass import getpass
from atm import ATM


# ─── UI Helpers ───────────────────────────────────────────────────────────────

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def header(title: str = "ATM SIMULATOR"):
    print("=" * 44)
    print(f"  {title.center(40)}")
    print("=" * 44)

def divider():
    print("-" * 44)

def pause():
    input("\n  Tekan Enter untuk lanjut...")

def fmt_rp(amount: int) -> str:
    return f"Rp{amount:,.0f}".replace(",", ".")


# ─── Menu Screens ─────────────────────────────────────────────────────────────

def menu_utama(atm: ATM):
    """Menu awal sebelum login."""
    while True:
        clear()
        header()
        print("  1. Login Rekening")
        print("  2. Cek Saldo (Scan Kartu)")
        print("  0. Keluar")
        divider()
        pilihan = input("  Pilih: ").strip()

        if pilihan == "1":
            menu_login(atm)
        elif pilihan == "2":
            aksi_scan_saldo(atm)
        elif pilihan == "0":
            clear()
            print("\n  Terima kasih. Sampai jumpa!\n")
            sys.exit(0)
        else:
            print("  [!] Pilihan tidak valid.")
            pause()


def menu_login(atm: ATM):
    """Form login rekening."""
    clear()
    header("LOGIN REKENING")
    no_rek = input("  No. Rekening : ").strip()
    pin    = getpass("  PIN          : ")

    ok, pesan = atm.login(no_rek, pin)
    print(f"\n  {'✓' if ok else '✗'} {pesan}")

    if ok:
        pause()
        menu_dashboard(atm)
    else:
        pause()


def menu_dashboard(atm: ATM):
    """Dashboard setelah login berhasil."""
    while True:
        clear()
        header("DASHBOARD")
        nama  = atm.get_nama()
        saldo = atm.get_saldo()
        print(f"  Nama  : {nama}")
        print(f"  Saldo : {fmt_rp(saldo)}")
        divider()
        print("  1. Tarik Uang")
        print("  2. Setor Uang")
        print("  3. Riwayat Transaksi")
        print("  0. Logout")
        divider()
        pilihan = input("  Pilih: ").strip()

        if pilihan == "1":
            aksi_tarik(atm)
        elif pilihan == "2":
            aksi_setor(atm)
        elif pilihan == "3":
            aksi_riwayat(atm)
        elif pilihan == "0":
            atm.logout()
            print("\n  Logout berhasil.")
            pause()
            break
        else:
            print("  [!] Pilihan tidak valid.")
            pause()
            

# ─── Actions ──────────────────────────────────────────────────────────────────

def aksi_tarik(atm: ATM):
    clear()
    header("TARIK UANG")
    print(f"  Saldo saat ini: {fmt_rp(atm.get_saldo())}")
    print("  (Kelipatan Rp50.000)")
    divider()
    try:
        jumlah = int(input("  Jumlah tarik : Rp").replace(".", "").strip())
    except ValueError:
        print("  [!] Input tidak valid.")
        pause()
        return

    ok, pesan = atm.tarik(jumlah)
    print(f"\n  {'✓' if ok else '✗'} {pesan}")
    if ok:
        print(f"  Saldo sekarang: {fmt_rp(atm.get_saldo())}")
    pause()


def aksi_setor(atm: ATM):
    clear()
    header("SETOR UANG")
    print(f"  Saldo saat ini: {fmt_rp(atm.get_saldo())}")
    divider()
    try:
        jumlah = int(input("  Jumlah setor : Rp").replace(".", "").strip())
    except ValueError:
        print("  [!] Input tidak valid.")
        pause()
        return

    ok, pesan = atm.setor(jumlah)
    print(f"\n  {'✓' if ok else '✗'} {pesan}")
    if ok:
        print(f"  Saldo sekarang: {fmt_rp(atm.get_saldo())}")
    pause()


def aksi_riwayat(atm: ATM):
    clear()
    header("RIWAYAT TRANSAKSI")
    history = atm.get_history()

    if not history:
        print("  Belum ada transaksi.")
    else:
        for i, item in enumerate(history, 1):
            print(f"  {i:>2}. [{item['waktu']}]")
            print(f"      {item['keterangan']}")
            if i < len(history):
                divider()

    pause()


def aksi_scan_saldo(atm: ATM):
    """Buka kamera dan scan kartu untuk cek saldo tanpa login."""
    clear()
    header("CEK SALDO — SCAN KARTU")
    print("  Kamera akan terbuka.")
    print("  Arahkan kartu ATM ke area scan.")
    print("  Saldo akan ditampilkan di layar kamera.")
    print("  Tekan Q di jendela kamera untuk keluar.")
    divider()
    input("  Tekan Enter untuk membuka kamera...")

    # Import di sini supaya app tetap jalan walau OpenCV tidak terinstall
    try:
        from scanner import scan_card
    except ImportError as e:
        print(f"\n  [ERROR] Library tidak lengkap: {e}")
        print("  Jalankan: pip install opencv-python pytesseract")
        pause()
        return

    scan_card(atm)
    pause()


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    atm = ATM()
    menu_utama(atm)
