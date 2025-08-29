#!/usr/bin/env python3
"""
Vercel serverless function for processing images
"""

import os
import json
import base64
from io import BytesIO
import sys

# Add the current directory to the path so we can import Project5
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from Project5 import highResUpscale
    from PIL import Image
except ImportError as e:
    print(f"Error importing smoothing functions: {e}")
    sys.exit(1)

def handler(event, context):
    """Main handler for Vercel serverless function"""
    method = event.get('httpMethod', 'GET')
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
    
    if method == 'POST':
        return handle_process_image(body, cors_headers)
    else:
        return {
            'statusCode': 405,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Method not allowed'})
        }

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
        