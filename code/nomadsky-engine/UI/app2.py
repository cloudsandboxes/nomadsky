import webview

class API:
    def show_processing_page(self, source, destination, vmname):
        # Store values globally so processing page can access them
        self.source = source
        self.destination = destination
        self.vmname = vmname
        
        # Load the processing page
        window.load_url('C:/projects/nomadsky/code/nomadsky-engine/UI/2)processing-page.html')
    
    def get_values(self):
        return {
            'source': self.source,
            'destination': self.destination,
            'vmname': self.vmname
        }

# Read the form HTML
with open('C:/projects/nomadsky/code/nomadsky-engine/UI/frontend.html', 'r') as f:
    form_html = f.read()

# Create the window
api = API()
window = webview.create_window('VM Migration Tool', html=form_html, js_api=api)
webview.start()
