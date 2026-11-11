"""
Automated PyInstaller build script for Robo2mation Test Runner.
Run with: python build_exe.py
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def build():
    print("[*] Installing/Verifying PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pyinstaller"])

    dist_dir = ROOT / "dist"
    build_dir = ROOT / "build"
    if dist_dir.exists():
        shutil.rmtree(dist_dir, ignore_errors=True)
    if build_dir.exists():
        shutil.rmtree(build_dir, ignore_errors=True)

    print("[*] Compiling Test Automation Suite into Executable...")

    pyinstaller_cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onedir",                # Using onedir ensures fast startup & easy editing of .env
        "--windowed",              # No ugly black cmd window behind the GUI
        "--name=Robo2mation_Runner",
        "--collect-all=selenium",
        "--collect-all=openpyxl",
        "--collect-all=dotenv",
        f"--add-data={ROOT / 'common.py'}{os.pathsep}.",
        f"--add-data={ROOT / 'dms_helper.py'}{os.pathsep}.",
        f"--add-data={ROOT / 'explorer_helper.py'}{os.pathsep}.",
        f"--add-data={ROOT / 'test_files'}{os.pathsep}test_files",
        str(ROOT / "app_gui.py"),
    ]

    # Include all test case scripts into the bundle
    for tc_file in ROOT.glob("tc*.py"):
        pyinstaller_cmd.insert(pyinstaller_cmd.index(str(ROOT / "app_gui.py")), f"--add-data={tc_file}{os.pathsep}.")

    subprocess.check_call(pyinstaller_cmd)

    target_folder = dist_dir / "Robo2mation_Runner"

    # Copy .env, excel file, and test_files alongside the EXE so client can inspect/edit them
    print("[*] Copying runtime assets (.env, excel, test_files)...")
    for asset in [".env", "Robo2mation_26Q1_Sanity_Test_Case_Doc.xlsx"]:
        src = ROOT / asset
        if src.exists():
            shutil.copy2(src, target_folder / asset)

    test_files_src = ROOT / "test_files"
    if test_files_src.exists():
        shutil.copytree(test_files_src, target_folder / "test_files", dirs_exist_ok=True)

    print("\n" + "=" * 60)
    print(" BUILD SUCCESSFUL!")
    print(f" Executable Folder: {target_folder.resolve()}")
    print(" Double click 'Robo2mation_Runner.exe' to launch the app.")
    print("=" * 60)

if __name__ == "__main__":
    build()