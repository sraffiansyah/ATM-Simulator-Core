"""
Core ATM logic.
Struktur Data: Stack (riwayat transaksi), Dictionary (data rekening)
History transaksi disimpan ke JSON supaya persist setelah program ditutup.
"""

import json
from datetime import datetime
from pathlib import Path

DATA_FILE = Path(__file__).parent / "accounts.json"


# ─── Stack Implementation ─────────────────────────────────────────────────────

class Stack:
    def __init__(self, initial: list | None = None):
        self._data: list = list(initial) if initial else []

    def push(self, item):       self._data.append(item)
    def pop(self):              return self._data.pop() if self._data else None
    def peek(self):             return self._data[-1] if self._data else None
    def is_empty(self) -> bool: return len(self._data) == 0
    def size(self) -> int:      return len(self._data)
    def to_list(self) -> list:  return list(reversed(self._data))   # terbaru di atas


# ─── ATM Core ─────────────────────────────────────────────────────────────────

class ATM:
    def __init__(self):
        self.accounts: dict        = self._load_accounts()
        self.logged_in: str | None = None
        # Stack di-init dari history JSON milik akun yang sedang login
        # (di-load ulang saat login)
        self.history: Stack        = Stack()

    # ── Persistence ──────────────────────────────────────────────────────────

    def _load_accounts(self) -> dict:
        with open(DATA_FILE, encoding="utf-8") as f:
            return json.load(f)

    def _save_accounts(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.accounts, f, indent=4, ensure_ascii=False)

    # ── Helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _normalize_card(no_kartu: str) -> str:
        return no_kartu.replace(" ", "").replace("-", "").strip()

    # ── Lookup ───────────────────────────────────────────────────────────────

    def find_by_card(self, no_kartu: str) -> str | None:
        target = self._normalize_card(no_kartu)
        for no_rek, data in self.accounts.items():
            if self._normalize_card(data.get("no_kartu", "")) == target:
                return no_rek
        return None

    def account_exists(self, no_rek: str) -> bool:
        return no_rek in self.accounts

    def card_exists(self, no_kartu: str) -> bool:
        return self.find_by_card(no_kartu) is not None

    # ── Auth ─────────────────────────────────────────────────────────────────

    def login(self, no_rek: str, pin: str) -> tuple[bool, str]:
        if no_rek not in self.accounts:
            return False, "Nomor rekening tidak ditemukan."
        if self.accounts[no_rek]["pin"] != pin:
            return False, "PIN salah."
        self.logged_in = no_rek
        # Load history dari JSON ke Stack (urutan lama → baru, push satu-satu)
        saved = self.accounts[no_rek].get("history", [])
        self.history = Stack(saved)     # _data = urutan lama→baru, to_list() balik jadi baru→lama
        self._record(f"LOGIN berhasil — rekening {no_rek}")
        return True, "Login berhasil."

    def logout(self):
        self._record(f"LOGOUT — rekening {self.logged_in}")
        self.logged_in = None
        self.history   = Stack()        # reset stack di memori

    # ── Account Info ─────────────────────────────────────────────────────────

    def get_saldo(self, no_rek: str | None = None) -> int | None:
        key = no_rek or self.logged_in
        return self.accounts.get(key, {}).get("saldo")

    def get_nama(self, no_rek: str | None = None) -> str | None:
        key = no_rek or self.logged_in
        return self.accounts.get(key, {}).get("nama")

    def get_no_kartu(self, no_rek: str | None = None) -> str | None:
        key = no_rek or self.logged_in
        raw = self._normalize_card(self.accounts.get(key, {}).get("no_kartu", ""))
        return " ".join(raw[i:i+4] for i in range(0, len(raw), 4)) if raw else None

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
        self._record(f"TARIK  Rp{jumlah:,.0f}  | Sisa: Rp{self.accounts[self.logged_in]['saldo']:,.0f}")
        self._save_accounts()
        return True, f"Berhasil tarik Rp{jumlah:,.0f}."

    def setor(self, jumlah: int) -> tuple[bool, str]:
        if not self.logged_in:
            return False, "Belum login."
        if jumlah <= 0:
            return False, "Jumlah harus lebih dari 0."
        self.accounts[self.logged_in]["saldo"] += jumlah
        self._record(f"SETOR  Rp{jumlah:,.0f}  | Saldo: Rp{self.accounts[self.logged_in]['saldo']:,.0f}")
        self._save_accounts()
        return True, f"Berhasil setor Rp{jumlah:,.0f}."

    # ── History (Stack + JSON) ────────────────────────────────────────────────

    def _record(self, keterangan: str):
        """Push ke Stack dan langsung sync ke JSON."""
        waktu = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        entry = {"waktu": waktu, "keterangan": keterangan}
        self.history.push(entry)
        # Simpan Stack ke JSON (urutan _data = lama→baru, sesuai urutan push)
        if self.logged_in:
            self.accounts[self.logged_in]["history"] = self.history._data
            self._save_accounts()

    def get_history(self) -> list[dict]:
        return self.history.to_list()   # terbaru di atas
