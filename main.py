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

    while True:
        clear()
        header("DASHBOARD")
        print(f"  Nama  : {atm.get_nama()}")
        print(f"  Saldo : {fmt_rp(atm.get_saldo())}")
        divider()
        print("  1. Tarik Uang")
        print("  2. Setor Uang")
        print("  3. Transfer")
        print("  4. Riwayat Transaksi")
        print("  0. Logout")
        divider()
        pilihan = input("  Pilih: ").strip()

        match pilihan:
            case "1": aksi_tarik(atm)
            case "2": aksi_setor(atm)
            case "3": aksi_transfer(atm)
            case "4": aksi_riwayat(atm)
            case "0":
                atm.logout()
                print("\n  Logout berhasil.")
                pause()
                break
            case _:
                print("  [!] Pilihan tidak valid.")
                pause()


# ─── Actions ──────────────────────────────────────────────────────────────────

def aksi_tarik(atm: ATM):
    clear()
    header("TARIK UANG")
    print(f"  Saldo saat ini: {fmt_rp(atm.get_saldo())}")
    divider()

    # Pilih pecahan
    print("  Pilih pecahan:")
    print("  1. Rp50.000")
    print("  2. Rp100.000")
    divider()
    pilihan_pecahan = input("  Pilih: ").strip()

    if pilihan_pecahan == "1":
        pecahan = 50_000
    elif pilihan_pecahan == "2":
        pecahan = 100_000
    else:
        print("  [!] Pilihan tidak valid.")
        pause()
        return

    print(f"\n  Pecahan: Rp{pecahan:,.0f} | Masukkan kelipatan Rp{pecahan:,.0f}")
    divider()

    try:
        jumlah = int(input("  Jumlah tarik : Rp").replace(".", "").strip())
    except ValueError:
        print("  [!] Input tidak valid.")
        pause()
        return

    ok, pesan = atm.tarik(jumlah, pecahan)
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


def aksi_transfer(atm: ATM):
    clear()
    header("TRANSFER")
    print(f"  Saldo saat ini: {fmt_rp(atm.get_saldo())}")
    divider()

    no_tujuan = input("  No. Rekening Tujuan : ").strip()

    # Preview nama penerima sebelum konfirmasi
    if not atm.account_exists(no_tujuan):
        print("\n  ✗ Nomor rekening tujuan tidak ditemukan.")
        pause()
        return

    nama_tujuan = atm.get_nama(no_tujuan)
    print(f"  Nama Penerima        : {nama_tujuan}")
    divider()

    try:
        jumlah = int(input("  Jumlah transfer : Rp").replace(".", "").strip())
    except ValueError:
        print("  [!] Input tidak valid.")
        pause()
        return

    # Konfirmasi sebelum transfer
    print(f"\n  ┌─ Konfirmasi Transfer ───────────────┐")
    print(f"  │  Ke     : {nama_tujuan} ({no_tujuan})")
    print(f"  │  Jumlah : {fmt_rp(jumlah)}")
    print(f"  └─────────────────────────────────────┘")
    konfirmasi = input("\n  Lanjutkan? (y/n): ").strip().lower()

    if konfirmasi != "y":
        print("  Transfer dibatalkan.")
        pause()
        return

    ok, pesan = atm.transfer(no_tujuan, jumlah)
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

    clear()
    header("CEK SALDO — SCAN KARTU")
    print("  Kamera akan terbuka.")
    print("  Arahkan kartu ATM ke area scan.")
    print("  Saldo akan ditampilkan di layar kamera.")
    print("  Tekan Q di jendela kamera untuk keluar.")
    divider()
    input("  Tekan Enter untuk membuka kamera...")


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
