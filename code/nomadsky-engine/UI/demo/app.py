import webview
import subprocess

class Api:
    def migrate_vm(self, source, destination, vmname):
        # Run your migration script with form parameters
        script = 'C:/projects/nomadsky/code/nomadsky-engine/scripts/migrate.py'
        result = subprocess.run(
            ['python', script, source, destination, vmname],
            capture_output=True,
            text=True
        )
        return {'done': True, 'output': result.stdout}

# HTML with form
html = '''
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial; padding: 20px; }
        label { display: block; margin-top: 10px; }
        select, input { width: 200px; padding: 5px; margin-top: 5px; }
        button { margin-top: 20px; padding: 10px 20px; }
        #result { margin-top: 20px; font-weight: bold; }
    </style>
</head>
<body>
    <h1>VM Migration</h1>
    
    <label>Source Platform</label>
    <select id="source">
        <option value="azure">Azure</option>
        <option value="aws">AWS</option>
        <option value="gcp">GCP</option>
    </select>
    
    <label>Destination Platform</label>
    <select id="destination">
        <option value="aws">AWS</option>
        <option value="azure">Azure</option>
        <option value="gcp">GCP</option>
    </select>
    
    <label>VM Name</label>
    <input type="text" id="vmname" value="production-server-1">
    
    <br>
    <button onclick="migrate()">Migrate VM</button>
    <div id="result"></div>

    <script>
        async function migrate() {
            const source = document.getElementById('source').value;
            const destination = document.getElementById('destination').value;
            const vmname = document.getElementById('vmname').value;
            
            document.getElementById('result').textContent = 'Running migration...';
            
            const result = await pywebview.api.migrate_vm(source, destination, vmname);
            
            if (result.done) {
                document.getElementById('result').textContent = 'Finished! ' + result.output;
            }
        }
    </script>
</body>
</html>
'''

api = Api()
webview.create_window('VM Migration Tool', html=html, js_api=api, width=400, height=500)
webview.start()
