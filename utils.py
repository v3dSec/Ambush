import ctypes
import ctypes.wintypes as wintypes
from ctypes import byref, sizeof, POINTER, c_size_t


class PROCESS_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("Reserved1", wintypes.LPVOID),
        ("PebBaseAddress", wintypes.LPVOID),
        ("Reserved2", wintypes.LPVOID * 2),
        ("UniqueProcessId", wintypes.HANDLE),
        ("Reserved3", wintypes.LPVOID),
    ]


class UNICODE_STRING(ctypes.Structure):
    _fields_ = [
        ("Length", wintypes.USHORT),
        ("MaximumLength", wintypes.USHORT),
        ("Buffer", wintypes.LPWSTR),
    ]


class OBJECT_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ("Length", wintypes.ULONG),
        ("RootDirectory", wintypes.HANDLE),
        ("ObjectName", POINTER(UNICODE_STRING)),
        ("Attributes", wintypes.ULONG),
        ("SecurityDescriptor", wintypes.LPVOID),
        ("SecurityQualityOfService", wintypes.LPVOID),
    ]


class LARGE_INTEGER(ctypes.Structure):
    _fields_ = [("LowPart", wintypes.DWORD), ("HighPart", wintypes.LONG)]

    @property
    def QuadPart(self):
        return self.LowPart + (self.HighPart << 32)

    @QuadPart.setter
    def QuadPart(self, value):
        self.LowPart = value & 0xFFFFFFFF
        self.HighPart = (value >> 32) & 0xFFFFFFFF


class CLIENT_ID(ctypes.Structure):
    _fields_ = [("UniqueProcess", wintypes.HANDLE), ("UniqueThread", wintypes.HANDLE)]


PROCESS_ALL_ACCESS = 0x1F0FFF
SECTION_ALL_ACCESS = 0x1F001F
SECTION_MAP_READ = 0x0004
ProcessBasicInformation = 0

PAGE_EXECUTE_READWRITE = 0x40
PAGE_EXECUTE_WRITECOPY = 0x80
PAGE_EXECUTE_READ = 0x20
PAGE_READWRITE = 0x04
PAGE_NOACCESS = 0x01

MEM_RESERVE = 0x00002000
MEM_COMMIT = 0x00001000
MEM_RELEASE = 0x8000

VIEW_SHARE = 0x2
OFFSET_MAPPED_DLL = 4096


NTSTATUS = wintypes.LONG
SIZE_T = c_size_t
ULONG = wintypes.DWORD
ULONG_PTR = c_size_t


kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
ntdll = ctypes.WinDLL("ntdll", use_last_error=True)


ntdll.NtAllocateVirtualMemory.argtypes = [
    wintypes.HANDLE,
    POINTER(wintypes.LPVOID),
    ULONG_PTR,
    POINTER(SIZE_T),
    wintypes.ULONG,
    wintypes.ULONG,
]
ntdll.NtAllocateVirtualMemory.restype = NTSTATUS


ntdll.NtProtectVirtualMemory.argtypes = [
    wintypes.HANDLE,
    POINTER(wintypes.LPVOID),
    POINTER(SIZE_T),
    wintypes.ULONG,
    POINTER(wintypes.ULONG),
]
ntdll.NtProtectVirtualMemory.restype = NTSTATUS


ntdll.RtlCreateUserThread.argtypes = [
    wintypes.HANDLE,
    wintypes.LPVOID,
    wintypes.BOOLEAN,
    wintypes.ULONG,
    SIZE_T,
    SIZE_T,
    wintypes.LPVOID,
    wintypes.LPVOID,
    POINTER(wintypes.HANDLE),
    POINTER(CLIENT_ID),
]
ntdll.RtlCreateUserThread.restype = NTSTATUS


ntdll.NtCreateSection.argtypes = [
    POINTER(wintypes.HANDLE),
    wintypes.DWORD,
    wintypes.LPVOID,
    POINTER(LARGE_INTEGER),
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.LPVOID,
]
ntdll.NtCreateSection.restype = NTSTATUS


ntdll.NtMapViewOfSection.argtypes = [
    wintypes.HANDLE,
    wintypes.HANDLE,
    POINTER(wintypes.LPVOID),
    ULONG,
    SIZE_T,
    POINTER(LARGE_INTEGER),
    POINTER(SIZE_T),
    wintypes.DWORD,
    ULONG,
    ULONG,
]
ntdll.NtMapViewOfSection.restype = NTSTATUS


ntdll.NtUnmapViewOfSection.argtypes = [wintypes.HANDLE, wintypes.LPVOID]
ntdll.NtUnmapViewOfSection.restype = NTSTATUS


ntdll.NtCreateThreadEx.argtypes = [
    POINTER(wintypes.HANDLE),
    wintypes.DWORD,
    wintypes.LPVOID,
    wintypes.HANDLE,
    wintypes.LPVOID,
    wintypes.LPVOID,
    ULONG,
    SIZE_T,
    SIZE_T,
    SIZE_T,
    wintypes.LPVOID,
]
ntdll.NtCreateThreadEx.restype = NTSTATUS


ntdll.NtClose.argtypes = [wintypes.HANDLE]
ntdll.NtClose.restype = NTSTATUS


ntdll.NtQueryInformationProcess.argtypes = [
    wintypes.HANDLE,
    wintypes.ULONG,
    wintypes.HANDLE,
    wintypes.ULONG,
    wintypes.PULONG,
]
ntdll.NtQueryInformationProcess.restype = NTSTATUS


ntdll.NtReadVirtualMemory.argtypes = [
    wintypes.HANDLE,
    wintypes.LPVOID,
    wintypes.LPVOID,
    wintypes.ULONG,
    wintypes.PULONG,
]
ntdll.NtReadVirtualMemory.restype = NTSTATUS


ntdll.NtOpenSection.argtypes = [wintypes.PHANDLE, wintypes.DWORD, wintypes.LPVOID]
ntdll.NtOpenSection.restype = NTSTATUS


kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
kernel32.OpenProcess.restype = wintypes.HANDLE

kernel32.MapViewOfFile.restype = wintypes.LPVOID
kernel32.MapViewOfFile.argtypes = [
    wintypes.HANDLE,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.DWORD,
]

kernel32.VirtualProtect.restype = wintypes.BOOL
kernel32.VirtualProtect.argtypes = [
    wintypes.LPVOID,
    wintypes.DWORD,
    wintypes.DWORD,
    POINTER(wintypes.DWORD),
]

kernel32.CloseHandle.restype = wintypes.BOOL
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.GetCurrentProcess.restype = wintypes.HANDLE


def read_remote_int_ptr(process_handle, mem_address, number_of_bytes):
    """Reads an integer pointer from remote process memory."""
    buffer = ctypes.create_string_buffer(number_of_bytes)
    bytes_read = wintypes.ULONG(0)
    status = ntdll.NtReadVirtualMemory(
        process_handle, mem_address, buffer, number_of_bytes, byref(bytes_read)
    )
    if status != 0:
        return None
    return int.from_bytes(buffer.raw[: bytes_read.value], byteorder="little")


def read_remote_wstr(process_handle, mem_address):
    """Reads a wide string from remote process memory."""
    buffer = ctypes.create_string_buffer(256)
    bytes_read = wintypes.ULONG(0)
    status = ntdll.NtReadVirtualMemory(
        process_handle, mem_address, buffer, 256, byref(bytes_read)
    )
    if status != 0:
        return ""

    read_bytes = buffer.raw[: bytes_read.value]
    index = read_bytes.find(b"\x00\x00")
    if index == -1:
        return ""

    unicode_str = read_bytes[:index].decode("unicode-escape")
    return "".join(char for char in unicode_str if char.isprintable())


def get_local_lib_address(dll_name):
    """Retrieves the base address of a loaded DLL in the current process."""
    process_handle = kernel32.GetCurrentProcess()
    process_information = PROCESS_BASIC_INFORMATION()
    return_length = wintypes.ULONG()

    status = ntdll.NtQueryInformationProcess(
        process_handle,
        ProcessBasicInformation,
        byref(process_information),
        sizeof(process_information),
        byref(return_length),
    )
    if status != 0:
        raise ctypes.WinError(ctypes.get_last_error())

    ldr_offset = 0x18
    ldr_pointer = process_information.PebBaseAddress + ldr_offset
    ldr_address = read_remote_int_ptr(process_handle, ldr_pointer, 8)

    in_init_order_offset = 0x30
    in_init_order_list = ldr_address + in_init_order_offset
    next_flink = read_remote_int_ptr(process_handle, in_init_order_list, 8)

    dll_base = 1337
    flink_dllbase_offset = 0x20
    flink_buffer_offset = 0x50

    while dll_base != 0:
        next_flink = next_flink - 0x10
        dll_base = read_remote_int_ptr(
            process_handle, (next_flink + flink_dllbase_offset), 8
        )

        if dll_base == 0:
            break

        buffer = read_remote_int_ptr(
            process_handle, (next_flink + flink_buffer_offset), 8
        )
        base_dll_name = read_remote_wstr(process_handle, buffer)

        if base_dll_name.lower() == dll_name.lower():
            return dll_base

        next_flink = read_remote_int_ptr(process_handle, (next_flink + 0x10), 8)

    return None


def create_unicode_string(string):
    """Helper to create UNICODE_STRING structure."""
    u_string = UNICODE_STRING()
    u_string.Length = len(string) * 2
    u_string.MaximumLength = u_string.Length + 2
    u_string.Buffer = string
    return u_string
