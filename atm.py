"""
Core ATM logic.
Struktur Data: Stack (riwayat transaksi), Dictionary (data rekening)
"""

import json
from datetime import datetime
from pathlib import Path

DATA_FILE = Path(__file__).parent / "accounts.json"


# ─── Stack Implementation ─────────────────────────────────────────────────────

class Stack:
    def __init__(self):
        self._data: list = []

    def push(self, item):       self._data.append(item)
    def pop(self):              return self._data.pop() if self._data else None
    def peek(self):             return self._data[-1] if self._data else None
    def is_empty(self) -> bool: return len(self._data) == 0
    def size(self) -> int:      return len(self._data)
    def to_list(self) -> list:  return list(reversed(self._data))   # terbaru di atas


# ─── ATM Core ─────────────────────────────────────────────────────────────────

class ATM:
    def __init__(self):
        self.accounts: dict     = self._load_accounts()     # Dictionary utama
        self.history:  Stack    = Stack()                   # Stack riwayat
        self.logged_in: str | None = None                   # nomor rekening aktif

    # ── Persistence ──────────────────────────────────────────────────────────

    def _load_accounts(self) -> dict:
        with open(DATA_FILE, encoding="utf-8") as f:
            return json.load(f)

    def _save_accounts(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.accounts, f, indent=4, ensure_ascii=False)

    # ── Auth ─────────────────────────────────────────────────────────────────

    def login(self, no_rek: str, pin: str) -> tuple[bool, str]:
        if no_rek not in self.accounts:
            return False, "Nomor rekening tidak ditemukan."
        if self.accounts[no_rek]["pin"] != pin:
            return False, "PIN salah."
        self.logged_in = no_rek
        self._record(f"LOGIN berhasil — rekening {no_rek}")
        return True, "Login berhasil."

    def logout(self):
        self._record(f"LOGOUT — rekening {self.logged_in}")
        self.logged_in = None

    # ── Account Info ─────────────────────────────────────────────────────────

    def get_saldo(self, no_rek: str | None = None) -> int | None:
        key = no_rek or self.logged_in
        return self.accounts.get(key, {}).get("saldo")

    def get_nama(self, no_rek: str | None = None) -> str | None:
        key = no_rek or self.logged_in
        return self.accounts.get(key, {}).get("nama")

    def account_exists(self, no_rek: str) -> bool:
        return no_rek in self.accounts

    # ── Transactions ─────────────────────────────────────────────────────────

    def tarik(self, jumlah: int) -> tuple[bool, str]:
        if not self.logged_in:
            return False, "Belum login."
        if jumlah <= 0:
            return False, "Jumlah harus lebih dari 0."
        if jumlah % 50_000 != 0:
            return False, "Jumlah harus kelipatan Rp50.000."
        saldo = self.accounts[self.logged_in]["saldo"]
        if jumlah > saldo:
            return False, "Saldo tidak mencukupi."
        self.accounts[self.logged_in]["saldo"] -= jumlah
        self._save_accounts()
        self._record(f"TARIK  Rp{jumlah:,.0f}  | Sisa: Rp{self.accounts[self.logged_in]['saldo']:,.0f}")
        return True, f"Berhasil tarik Rp{jumlah:,.0f}."

    def setor(self, jumlah: int) -> tuple[bool, str]:
        if not self.logged_in:
            return False, "Belum login."
        if jumlah <= 0:
            return False, "Jumlah harus lebih dari 0."
        self.accounts[self.logged_in]["saldo"] += jumlah
        self._save_accounts()
        self._record(f"SETOR  Rp{jumlah:,.0f}  | Saldo: Rp{self.accounts[self.logged_in]['saldo']:,.0f}")
        return True, f"Berhasil setor Rp{jumlah:,.0f}."

    # ── History (Stack) ───────────────────────────────────────────────────────

    def _record(self, keterangan: str):
        waktu = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self.history.push({"waktu": waktu, "keterangan": keterangan})

    def get_history(self) -> list[dict]:
        return self.history.to_list()
