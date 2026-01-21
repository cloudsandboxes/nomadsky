import sys
from azure.identity import InteractiveBrowserCredential
from azure.mgmt.compute import ComputeManagementClient
import sys
import json

# Get arguments
source = sys.argv[1]
destination = sys.argv[2]
vmname = sys.argv[3]



sys.path.append(r"C:/projects/nomadsky/code/microsoft-connections")



# Extract specific value from previous files
shared_data_json = sys.argv[4]  # 4th argument
shared_data = json.loads(shared_data_json)
vm_resource_id = shared_data.get('resource_id', '')

try:
    subscription_id = vm_resource_id
except IndexError:
        raise Exception(f" Invalid resource ID format: '{vm_resource_id}' ")
        
# Authenticate interactively
tenant_id = "78ba35ee-470e-4a16-ba92-ad53510ad7f6"
#credential = InteractiveBrowserCredential(tenant_id=tenant_id)


      sys.path.append(r"C:/projects/nomadsky/code/microsoft-connections")
      import config
      importdisktype = config.importdisktype
      if (importdisktype == exportdisktype):
            result = {
             'message': f"the diskfile type is already '{config.importdisktype}' so no need to transform type!",
             }
            print(json.dumps(result))
      else:
            result = {
             'message': f"the import diskfile type is different '{config.importdisktype}' to the export type '{exportfiletype}' so need to transform!",
             }
            print(json.dumps(result))
      
      
elif destination == 'aws':
   a='empty'
   #     # AWS boto3 code to find VM
   # etc.


#from helpers import my_function
#result = my_function(5)


#add logic



result = {
   'message': f"VM '{vmname}' has been uploaded successfully to '{destination}'!",
   'resource_id': vm_resource_id
    }
print(json.dumps(result))





