#!/usr/bin/env python3
"""
Web Backend for Pixel Art Smoother
This file provides a serverless function for Vercel deployment.
"""

import os
import json
import base64
from io import BytesIO
from urllib.parse import urlparse, parse_qs
import sys

# Import the existing smoothing functions
try:
    from Project5 import highResUpscale, lowResUpscale, samusGif, feiGif, bartGif
    from PIL import Image
except ImportError as e:
    print(f"Error importing smoothing functions: {e}")
    print("Make sure Project5.py is in the same directory")
    sys.exit(1)

def handle_request(event, context):
    """Main handler for Vercel serverless function"""
    method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    headers = event.get('headers', {})
    body = event.get('body', '')
    
    # Handle CORS
    cors_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
    
    # Handle preflight requests
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': ''
        }
    
    if method == 'GET':
        return handle_get_request(path, headers, cors_headers)
    elif method == 'POST':
        return handle_post_request(path, body, headers, cors_headers)
    else:
        return {
            'statusCode': 405,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Method not allowed'})
        }

def handle_get_request(path, headers, cors_headers):
    """Handle GET requests"""
    # Serve static files or redirect to index.html
    if path == '/' or path == '/index.html':
        return {
            'statusCode': 200,
            'headers': {**cors_headers, 'Content-Type': 'text/html'},
            'body': get_static_file('index.html')
        }
    elif path == '/styles.css':
        return {
            'statusCode': 200,
            'headers': {**cors_headers, 'Content-Type': 'text/css'},
            'body': get_static_file('styles.css')
        }
    elif path == '/script.js':
        return {
            'statusCode': 200,
            'headers': {**cors_headers, 'Content-Type': 'application/javascript'},
            'body': get_static_file('script.js')
        }
    elif path.endswith('.png') or path.endswith('.jpg') or path.endswith('.jpeg') or path.endswith('.gif') or path.endswith('.ttf'):
        # For static assets, redirect to the actual file
        return {
            'statusCode': 302,
            'headers': {**cors_headers, 'Location': path},
            'body': ''
        }
    else:
        return {
            'statusCode': 404,
            'headers': cors_headers,
            'body': json.dumps({'error': 'File not found'})
        }

def handle_post_request(path, body, headers, cors_headers):
    """Handle POST requests"""
    if path == '/api/process-image':
        return handle_process_image(body, cors_headers)
    elif path == '/api/create-gif':
        return handle_create_gif(body, cors_headers)
    else:
        return {
            'statusCode': 404,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Endpoint not found'})
        }

def get_static_file(filename):
    """Get static file content"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"File {filename} not found"

def handle_process_image(body, cors_headers):
    """Handle image processing requests"""
    try:
        # Parse JSON data
        data = json.loads(body)
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
        
        return {
            'statusCode': 200,
            'headers': {**cors_headers, 'Content-Type': 'application/json'},
            'body': json.dumps(response)
        }
        
    except Exception as e:
        print(f"Error processing image: {e}")
        import traceback
        traceback.print_exc()
        response = {
            'success': False,
            'error': str(e)
        }
        
        return {
            'statusCode': 500,
            'headers': {**cors_headers, 'Content-Type': 'application/json'},
            'body': json.dumps(response)
        }

def handle_create_gif(body, cors_headers):
    """Handle GIF creation requests"""
    try:
        # Parse JSON data
        data = json.loads(body)
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
        
        return {
            'statusCode': 200,
            'headers': {**cors_headers, 'Content-Type': 'application/json'},
            'body': json.dumps(response)
        }
        
    except Exception as e:
        print(f"Error creating GIF: {e}")
        response = {
            'success': False,
            'error': str(e)
        }
        
        return {
            'statusCode': 500,
            'headers': {**cors_headers, 'Content-Type': 'application/json'},
            'body': json.dumps(response)
        }

# For local development
if __name__ == "__main__":
    from http.server import HTTPServer, BaseHTTPRequestHandler
    
    class PixelArtSmootherHandler(BaseHTTPRequestHandler):
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
                
                # Decode base64 image
                if image_data.startswith('data:image/'):
                    image_data = image_data.split(',')[1]
                
                image_bytes = base64.b64decode(image_data)
                image = Image.open(BytesIO(image_bytes))
                
                # Always use high-res upscale
                processed_image = highResUpscale(image)
                
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

    def run_server(port=8000):
        """Run the HTTP server"""
        server_address = ('', port)
        httpd = HTTPServer(server_address, PixelArtSmootherHandler)
        print(f"Server running on http://localhost:{port}")
        print("Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.shutdown()

    run_server()
