def create_vm_from_image(nova, image_id, vm_name):
    import time
    
    # Get flavor by name
    flavor_name = "s5.small"
    flavor = next((f for f in flavors if f.name == flavor_name), None)
    if not flavor:
        return False, f"Flavor {flavor_name} not found"
    
    # Get network (optional)
    nics = None
    network_name="public"
    if network_name:
        networks = nova.neutron.list_networks()['networks']
        network = next((n for n in networks if n['name'] == network_name), None)
        if network:
            nics = [{'net-id': network['id']}]
    
    # Create server
    server = nova.servers.create(
        name=vm_name,
        image=image_id,
        flavor=flavor.id,
        nics=nics
    )
    
    # Wait for VM to become active (check every 5 seconds, max 10 minutes)
    for _ in range(120):
        srv = nova.servers.get(server.id)
        if srv.status == 'ACTIVE':
            return True, f"VM {vm_name} created (ID: {server.id})"
        elif srv.status == 'ERROR':
            return False, f"VM creation failed"
        time.sleep(5)
    
    return False, f"VM creation timeout"
