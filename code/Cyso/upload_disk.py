#!/usr/bin/env python3
def uploading_disk(vm_name):
    """
    Cyso.cloud OpenStack VM Access Script
    This script authenticates to Cyso.cloud OpenStack and downloads the image
    """
    
    import os
    import sys
    import webbrowser
    from novaclient import client as nova_client
    from glanceclient import client as glance_client
    from keystoneauth1 import session
    from keystoneauth1.identity import v3
    import getpass
    import json
    sys.path.append(r"C:/projects/nomadsky/code/Cyso")
    import tkinter as tk
    from tkinter import simpledialog
    import time
    import requests
    from requests.exceptions import ConnectionError, ChunkedEncodingError

    # Get arguments
    source = sys.argv[1]
    destination = sys.argv[2]
    vm_name = sys.argv[3].lower()
    import config
    output_path= fr"C:\Temp\osdisk-{vm_name}.qcow2"
    chunk_size = 50 * 1024 * 1024  # 50 MB per chunk

(glance, file_path, image_name, disk_format='qcow2', container_format='bare'):
    
    # Create image metadata
    image = glance.images.create(
        name=image_name,
        disk_format=disk_format,
        container_format=container_format,
        visibility='private'
    )
    
    # Upload in chunks
    chunk_size = 8192
    file_size = os.path.getsize(file_path)
    uploaded = 0
    
    with open(file_path, 'rb') as f:
        glance.images.upload(image.id, f)
    
    # Wait for image to become active (check every 5 seconds, max 30 minutes)
    for _ in range(360):
        img = glance.images.get(image.id)
        if img.status == 'active':
            return True, f"Image {image_name} uploaded (ID: {image.id})"
        elif img.status == 'error':
            return False, f"Upload failed"
        time.sleep(5)
    
    return False, f"Upload timeout"
