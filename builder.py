import os
import subprocess
import shutil
import sys
import uuid
import time

from console import print_step, print_success, print_error

OUTPUT_DIR = "output"

DEPENDENCIES = ["console.py", "evasion.py", "utils.py"]


def ensure_output():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def create_temp_dir():
    temp_dir = f"_build_{uuid.uuid4().hex[:8]}"
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir


def copy_dependencies(temp_dir):
    for dep in DEPENDENCIES:
        if os.path.exists(dep):
            shutil.copy(dep, os.path.join(temp_dir, dep))


def clean_build_artifacts(temp_dir):
    for p in ["build", "__pycache__", "dist"]:
        path = os.path.join(temp_dir, p)
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)


def build_pyinstaller(source_file, output_filename, hide_console=True):

    start = time.time()

    cmd = [
        sys.executable,
        "-OO",
        "-m",
        "PyInstaller",
        "--onefile",
        "--clean",
        "--strip",
        "--noconfirm",
        "--log-level",
        "ERROR",
        "--disable-windowed-traceback",
        "--name",
        output_filename,
        source_file,
    ]

    if hide_console:
        cmd.append("--noconsole")

    print_step("Running PyInstaller...")

    with open(os.devnull, "w") as devnull:
        subprocess.run(cmd, stdout=devnull, stderr=devnull, check=True)

    exe_path = os.path.join("dist", f"{output_filename}.exe")

    if os.path.exists(exe_path):
        duration = round(time.time() - start, 2)
        print_success(f"Done ({duration}s)")
        return exe_path

    return None


def build_nuitka(source_file, output_filename, hide_console=True):

    start = time.time()

    cmd = [
        sys.executable,
        "-OO",
        "-m",
        "nuitka",
        "--onefile",
        "--follow-imports",
        "--assume-yes-for-downloads",
        "--remove-output",
        "--output-filename=" + output_filename + ".exe",
        "--jobs=4",
        source_file,
    ]

    if hide_console:
        cmd.append("--windows-disable-console")

    print_step("Running Nuitka...")

    with open(os.devnull, "w") as devnull:
        subprocess.run(cmd, stdout=devnull, stderr=devnull, check=True)

    exe_path = os.path.abspath(output_filename + ".exe")

    if os.path.exists(exe_path):
        duration = round(time.time() - start, 2)
        print_success(f"Done ({duration}s)")
        return exe_path

    return None


def compile_exe(
    source_code, output_filename, method, hide_console=True, compile_binary=True
):

    ensure_output()
    temp_dir = create_temp_dir()

    try:
        source_file = os.path.join(temp_dir, "loader.py")

        with open(source_file, "w", encoding="utf-8") as f:
            f.write(source_code)

        copy_dependencies(temp_dir)

        if not compile_binary:
            dst = os.path.join(OUTPUT_DIR, f"{output_filename}.py")
            shutil.move(source_file, dst)
            print_success(f"Source generated: {dst}")
            return dst

        cwd = os.getcwd()
        os.chdir(temp_dir)

        exe_path = None

        if method == "pyinstaller":
            exe_path = build_pyinstaller("loader.py", output_filename, hide_console)

        elif method == "nuitka":
            exe_path = build_nuitka("loader.py", output_filename, hide_console)

        else:
            raise ValueError("Invalid builder")

        os.chdir(cwd)

        if exe_path and os.path.exists(os.path.join(temp_dir, exe_path)):
            final_path = os.path.join(OUTPUT_DIR, f"{output_filename}.exe")
            shutil.move(os.path.join(temp_dir, exe_path), final_path)
            return final_path

        print_error("Build failed")
        return None

    except subprocess.CalledProcessError:
        print_error("Compilation error")
        return None

    finally:

        clean_build_artifacts(temp_dir)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
