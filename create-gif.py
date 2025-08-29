#!/usr/bin/env python3
"""
Vercel serverless function for creating GIFs
"""

import os
import json
import base64
import sys

# Add the parent directory to the path so we can import Project5
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from Project5 import samusGif, feiGif, bartGif
except ImportError as e:
    print(f"Error importing GIF functions: {e}")
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
        return handle_create_gif(body, cors_headers)
    else:
        return {
            'statusCode': 405,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Method not allowed'})
        }

def handle_create_gif(body, cors_headers):
    """Handle GIF creation requests"""
    try:
        # Parse JSON data
        data = json.loads(body)
        character = data.get('character')
        
        if not character:
            raise ValueError("No character specified")
        
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
