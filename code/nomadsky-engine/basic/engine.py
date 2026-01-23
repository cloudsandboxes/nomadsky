import os
import subprocess
import sys
import json

source_platform = config["source_platform"].lower()
destination_platform = config["destination_platform"].lower()
os_disk_path = config["os_disk_path"]
output_format = config["output_format"].lower()
vars_dict = config.get("variables", {})

# -------------------------------
# 1) INSTALL REQUIRED PYTHON PACKAGES
# -------------------------------
print("Installing required Python packages...")

script_path = f'C:/projects/nomadsky/code/nomadsky-engine/UI/app.py'  
    try:
        result = subprocess.run(
            ['python', script_path],
            capture_output=True,
            text=True,
            check=True
        )
        
        return jsonify({
            'success': True,
            'output': result.stdout
        })
    except subprocess.CalledProcessError as e:
        return jsonify({
            'success': False,
            'error': e.stderr
        }), 500

# -------------------------------
# 2) DOWNLOAD AND INSTALL QEMU
# -------------------------------
# Only download if not present
qemu_path = r"C:\Program Files\qemu\qemu-img.exe" if os.name == "nt" else "/usr/bin/qemu-img"
if not os.path.exists(qemu_path):
    print("Downloading and installing QEMU...")
    if os.name == "nt":
        # Windows download link example (adjust version)
        qemu_installer = "https://qemu.weilnetz.de/w64/qemu-w64-setup-2023-07-26.exe"
        subprocess.run(["curl", "-L", "-o", "qemu-setup.exe", qemu_installer], check=True)
        subprocess.run(["start", "/wait", "qemu-setup.exe", "/S"], check=True)
    else:
        # Linux
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        subprocess.run(["sudo", "apt-get", "install", "-y", "qemu-utils"], check=True)
print("QEMU installed.")
