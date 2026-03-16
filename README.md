# Ambush — A Template-Driven AV/EDR Evasion Tool

**Ambush** is a template-driven packer designed to evade AV/EDR detection by packing executables and shellcode into protected Windows binaries. It is intended for **red team operators and penetration testers** who require a flexible method for transforming payloads into standalone executables.

Ambush converts executables or raw shellcode into **compressed, encrypted, and encoded payloads**, embedding them into a generated loader capable of performing **runtime environment checks and NTDLL unhooking to bypass user-mode hooks**. The resulting binary reconstructs and executes the protected payload directly in memory.

The tool automates the workflow of **payload packing, loader generation, and executable compilation**, allowing operators to produce loaders with varying binary structures.

Ambush supports multiple compilation backends:

- PyInstaller  
- Nuitka  
- cx_Freeze  

Each backend produces executables with distinct file layouts, runtime bootstraps, and packaging mechanisms, reducing the reliability of static detection signatures across different builds.

---

# ⚙️ Packing Workflow

```
Executable / Shellcode
        ↓
Compression
        ↓
Encryption
        ↓
Encoding
        ↓
Loader Template Generation
        ↓
Builder Compilation
        ↓
Packed Executable
```

The generated executable contains a runtime loader responsible for:

- reconstructing the protected payload at runtime  
- performing environment checks  
- restoring clean system libraries when required  
- executing the payload directly in memory  

---

# 🔐 Payload Protection Pipeline

### Compression

- zlib  
- bz2  
- lzma  
- gzip  
- none  

### Encryption

- RC4  
- none  

### Encoding

- Base85  
- Base64  
- Base32  
- URL-safe Base64  
- ASCII85  
- Hex / Base16  
- ROT13  
- none  

Combining multiple transformation layers ensures that payloads differ structurally between builds, reducing static fingerprint consistency.

---

# 🏗 Builder Diversity

Ambush intentionally supports multiple compilation frameworks to introduce structural variation in generated binaries.

Supported builders:

- PyInstaller  
- Nuitka  
- cx_Freeze  

Each builder packages the loader and runtime environment differently, resulting in variations such as:

- different PE section layouts  
- different import tables  
- different runtime initialization paths  
- different packaging formats for embedded resources  

Because the binary structure varies between builders, static detection signatures targeting one build pattern may not reliably detect builds produced using a different backend.

---

# 🧪 Environment Checks

Ambush includes runtime checks designed to detect automated analysis environments before executing the payload.

Supported checks include:

- ⏱ execution delay  
- 🧠 CPU core checks  
- 💾 system memory checks  
- ⌛ system uptime checks  
- 📊 running process count checks  

If the environment fails these checks, execution terminates before payload reconstruction occurs.

---

# 🧬 NTDLL Unhooking

Ambush includes optional **NTDLL restoration** to bypass user-mode hooks commonly placed by security products.

A clean copy of **ntdll.dll** is mapped from the system **KnownDlls section** and used to overwrite potentially hooked regions in memory.

---

# 📦 Installation

```
git clone https://github.com/<username>/ambush.git
cd ambush
pip install -r requirements.txt
```

---

# 🚀 Usage

### Pack raw shellcode

```
python main.py --shellcode payload.bin --output beacon
```

### Convert an executable to shellcode and pack

```
python main.py --exe payload.exe --output packed
```

### Enable CPU and RAM checks

```
python main.py --shellcode payload.bin --cpu-check 4 --ram-check 8
```

### Enable NTDLL unhooking

```
python main.py --shellcode payload.bin --unhooking
```

### Use a different builder backend

```
python main.py --shellcode payload.bin --builder nuitka --output loader
```

### Customize payload transformations

```
python main.py --shellcode payload.bin --compression lzma --encryption rc4 --encoding base85
```

### Full example

```
python main.py --exe payload.exe --builder nuitka --compression lzma --encoding base85 --cpu-check 4 --ram-check 8 --up-time 30 --background-processes 50 --time-delay 10 --unhooking --output loader
```

---

# 📂 Output

Generated artifacts are written to:

```
output/
```

Example:

```
output/beacon.exe
```

---

# ⚠️ Disclaimer

This project is intended strictly for **authorized penetration testing, red team engagements, and security research**. Unauthorized use may violate applicable laws and regulations.
