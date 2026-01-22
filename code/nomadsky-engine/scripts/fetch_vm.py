import sys
import subprocess
# fetching VM

# Get arguments
source = sys.argv[1]
destination = sys.argv[2]
vmname = sys.argv[3].lower()

if source == 'azure':
      # Azure SDK code to find VM
      import fetch_vm from fetching_vm  
      result = subprocess.run(
        ['python', 'C:/Projects/nomadsky/code/Microsoft/fetch_vm.py', source, destination, vmname],
        capture_output=True,
        text=True,
        check=True
      )
      output = result.stdout
      print(result.stdout)
      # Get the output
elif source == 'aws':
   a='empty'
   #     # AWS boto3 code to find VM
   # etc.
