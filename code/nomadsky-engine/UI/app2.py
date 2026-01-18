import webview
import subprocess

class Api:
    def __init__(self, window):
        self.window = window
    
    def show_processing_page(self, source, destination, vmname):
        # Load HTML from file
        with open('C:/projects/nomadsky/code/nomadsky-engine/UI/2)processing-page.html', 'r') as f:
            processing_html = f.read()
        
        # Replace placeholders with actual values
        processing_html = processing_html.replace('{{source}}', source)
        processing_html = processing_html.replace('{{destination}}', destination)
        processing_html = processing_html.replace('{{vmname}}', vmname)
        
        self.window.load_html(processing_html)
    
    def migrate_vm(self, source, destination, vmname):
        # Run your migration script
        script = 'C:/projects/nomadsky/code/nomadsky/scripts/migrate.py'
        result = subprocess.run(
            ['python', script, source, destination, vmname],
            capture_output=True,
            text=True
        )
        return {'done': True, 'output': result.stdout}

# Load form HTML from file
with open('C:/projects/nomadsky/code/nomadsky-engine/UI/frontend.html', 'r') as f:
    form_html = f.read()

# Create API and window
api = Api(None)
window = webview.create_window('VM Migration Tool', html=form_html, width=500, height=600, js_api=api)
api.window = window
webview.start(debug=True)


