def stop_vm(nova, vm_name):
    # Find VM by name
    servers = nova.servers.list(search_opts={'name': vm_name})
    if not servers:
        return False, "VM not found"
    
    server = servers[0]
    server.stop()  # Graceful shutdown
    return True, f"VM {vm_name} stopping"
