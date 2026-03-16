import sys

INDENT = "    "


def print_status(msg):
    print(f"[*] {msg}")


def print_step(msg):
    print(f"{INDENT}[*] {msg}")


def print_success(msg):
    print(f"[+] {msg}")


def print_warning(msg):
    print(f"[!] {msg}")


def print_error(msg):
    print(f"[-] {msg}")


def print_hex(addr):
    return f"0x{addr:016x}" if addr else "NULL"
