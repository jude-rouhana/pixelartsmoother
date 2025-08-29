#!/usr/bin/env python3
"""
Local Development Server for Pixel Art Smoother
This file provides a simple HTTP server for local development and testing.
"""

import os
import json
import base64
from io import BytesIO
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import sys

# Import the existing smoothing functions
try:
    from Project5 import highResUpscale, lowResUpscale, samusGif, feiGif, bartGif
    from PIL import Image
except ImportError as e:
    print(f"Error importing smoothing functions: {e}")
    print("Make sure Project5.py is in the same directory")
    sys.exit(1)

class LocalDevHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests - serve static files"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Serve the main HTML file
        if path == '/' or path == '/index.html':
            self.serve_file('index.html', 'text/html')
        elif path == '/styles.css':
            self.serve_file('styles.css', 'text/css')
        elif path == '/script.js':
            self.serve_file('script.js', 'application/javascript')
        elif path.endswith('.png') or path.endswith('.jpg') or path.endswith('.jpeg') or path.endswith('.gif') or path.endswith('.ttf'):
            # Serve image files
            self.serve_file(path[1:], 'image/' + path.split('.')[-1])
        else:
            self.send_error(404, "File not found")
    
    def do_POST(self):
        """Handle POST requests - process images and create GIFs"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/process-image':
            self.handle_process_image()
        elif path == '/create-gif':
            self.handle_create_gif()
        else:
            self.send_error(404, "Endpoint not found")
    
    def serve_file(self, filename, content_type):
        """Serve a static file"""
        try:
            with open(filename, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, "File not found")
    
    def handle_process_image(self):
        """Handle image processing requests"""
        try:
            # Parse the request
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Parse JSON data
            data = json.loads(post_data.decode('utf-8'))
            image_data = data.get('image')
            
            if not image_data:
                raise ValueError("No image data provided")
            
            # Decode base64 image
            if image_data.startswith('data:image/'):
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
            
            # Convert image to RGB format if needed
            if image.mode != 'RGB':
                print(f"Converting image from {image.mode} to RGB")
                image = image.convert('RGB')
            
            print(f"Processing image: {image.width}x{image.height} pixels")
            
            # Always use high-res upscale
            processed_image = highResUpscale(image)
            
            print(f"Processing complete: {processed_image.width}x{processed_image.height} pixels")
            
            # Convert back to base64
            output_buffer = BytesIO()
            processed_image.save(output_buffer, format='PNG')
            output_data = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
            
            # Send response
            response = {
                'success': True,
                'processedImage': f'data:image/png;base64,{output_data}'
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            print(f"Error processing image: {e}")
            import traceback
            traceback.print_exc()
            response = {
                'success': False,
                'error': str(e)
            }
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def handle_create_gif(self):
        """Handle GIF creation requests"""
        try:
            # Parse the request
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Parse JSON data
            data = json.loads(post_data.decode('utf-8'))
            character = data.get('character')
            
            # Create GIF based on character
            if character == 'samus':
                result = samusGif()
                gif_filename = 'samus.gif'
            elif character == 'fei':
                result = feiGif()
                gif_filename = 'fei.gif'
            elif character == 'bart':
                result = bartGif()
                gif_filename = 'bart.gif'
            else:
                raise ValueError(f"Unknown character: {character}")
            
            # Read the generated GIF file
            if result and os.path.exists(gif_filename):
                with open(gif_filename, 'rb') as f:
                    gif_data = f.read()
                
                # Convert to base64
                gif_base64 = base64.b64encode(gif_data).decode('utf-8')
                
                response = {
                    'success': True,
                    'gifData': f'data:image/gif;base64,{gif_base64}',
                    'filename': gif_filename
                }
            else:
                raise Exception("GIF creation failed")
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            print(f"Error creating GIF: {e}")
            response = {
                'success': False,
                'error': str(e)
            }
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))

def run_local_server(port=8080):
    """Run the local development HTTP server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, LocalDevHandler)
    print(f"Local development server running on http://localhost:{port}")
    print("Press Ctrl+C to stop the server")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.shutdown()

if __name__ == "__main__":
    run_local_server()
