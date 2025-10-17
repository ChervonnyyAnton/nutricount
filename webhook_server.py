#!/usr/bin/env python3
"""
GitHub Webhook Server for Nutrition Tracker
Receives webhook notifications from GitHub and triggers updates
"""

import os
import json
import hmac
import hashlib
import subprocess
import logging
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Configuration
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'your-webhook-secret')
UPDATE_SCRIPT = '/home/pi/simple_update.sh'
LOG_FILE = '/home/pi/logs/webhook.log'

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def verify_github_signature(payload, signature):
    """Verify GitHub webhook signature"""
    if not signature:
        return False
    
    # Remove 'sha256=' prefix
    if signature.startswith('sha256='):
        signature = signature[7:]
    
    # Calculate expected signature
    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

def trigger_update():
    """Trigger application update"""
    try:
        logging.info("🔄 Triggering application update...")
        
        # Run update script
        result = subprocess.run(
            [UPDATE_SCRIPT],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode == 0:
            logging.info("✅ Update completed successfully")
            return True
        else:
            logging.error(f"❌ Update failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logging.error("❌ Update timed out")
        return False
    except Exception as e:
        logging.error(f"❌ Update error: {e}")
        return False

@app.route('/webhook', methods=['POST'])
def github_webhook():
    """Handle GitHub webhook"""
    try:
        # Get payload and signature
        payload = request.get_data()
        signature = request.headers.get('X-Hub-Signature-256')
        
        # Verify signature
        if not verify_github_signature(payload, signature):
            logging.warning("❌ Invalid webhook signature")
            return jsonify({'error': 'Invalid signature'}), 401
        
        # Parse payload
        data = json.loads(payload)
        
        # Check webhook event type
        event_type = request.headers.get('X-GitHub-Event')
        
        if event_type == 'workflow_run':
            # Handle workflow completion
            workflow_data = data
            workflow_name = workflow_data.get('workflow', {}).get('name', '')
            workflow_conclusion = workflow_data.get('workflow_run', {}).get('conclusion', '')
            workflow_status = workflow_data.get('workflow_run', {}).get('status', '')
            
            logging.info(f"📋 Workflow '{workflow_name}' status: {workflow_status}, conclusion: {workflow_conclusion}")
            
            # Only deploy if workflow completed successfully
            if (workflow_status == 'completed' and 
                workflow_conclusion == 'success' and 
                workflow_name == 'CI/CD Pipeline'):
                
                logging.info("✅ CI/CD pipeline passed successfully, triggering deployment")
                
                # Trigger update
                if trigger_update():
                    return jsonify({'status': 'success', 'message': 'Deployment triggered after successful CI/CD'})
                else:
                    return jsonify({'status': 'error', 'message': 'Deployment failed'}), 500
            else:
                logging.info(f"ℹ️ Workflow not ready for deployment: {workflow_status}/{workflow_conclusion}")
                return jsonify({'status': 'ignored', 'message': f'Workflow not ready: {workflow_status}/{workflow_conclusion}'})
        
        elif event_type == 'push':
            # Handle direct push (fallback for manual deployment)
            if (data.get('ref') == 'refs/heads/main'):
                logging.info(f"📥 Received push notification for commit: {data.get('head_commit', {}).get('id', 'unknown')}")
                logging.warning("⚠️ Direct push detected - consider using CI/CD pipeline instead")
                
                # Ask for confirmation for direct push
                return jsonify({
                    'status': 'manual_deployment', 
                    'message': 'Direct push detected. Use CI/CD pipeline for automatic deployment.',
                    'confirmation_required': True
                })
            else:
                logging.info("ℹ️ Ignoring non-main branch push")
                return jsonify({'status': 'ignored', 'message': 'Not a main branch push'})
        
        else:
            logging.info(f"ℹ️ Ignoring event type: {event_type}")
            return jsonify({'status': 'ignored', 'message': f'Event type {event_type} not supported'})
            
    except Exception as e:
        logging.error(f"❌ Webhook error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/deploy', methods=['POST'])
def manual_deploy():
    """Manual deployment endpoint"""
    try:
        # Get payload and signature
        payload = request.get_data()
        signature = request.headers.get('X-Hub-Signature-256')
        
        # Verify signature
        if not verify_github_signature(payload, signature):
            logging.warning("❌ Invalid signature for manual deploy")
            return jsonify({'error': 'Invalid signature'}), 401
        
        # Parse payload
        data = json.loads(payload)
        
        # Check if it's a push to main branch
        if data.get('ref') == 'refs/heads/main':
            logging.info(f"🚀 Manual deployment triggered for commit: {data.get('head_commit', {}).get('id', 'unknown')}")
            
            # Trigger update
            if trigger_update():
                return jsonify({'status': 'success', 'message': 'Manual deployment completed'})
            else:
                return jsonify({'status': 'error', 'message': 'Manual deployment failed'}), 500
        else:
            return jsonify({'status': 'ignored', 'message': 'Not a main branch push'})
            
    except Exception as e:
        logging.error(f"❌ Manual deploy error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'nutrition-tracker-webhook'
    })

@app.route('/status', methods=['GET'])
def status():
    """Status endpoint"""
    try:
        # Check if application is running
        result = subprocess.run(
            ['/usr/bin/systemctl', 'is-active', 'nutrition-tracker'],
            capture_output=True,
            text=True
        )
        
        app_status = 'running' if result.returncode == 0 else 'stopped'
        
        return jsonify({
            'webhook_status': 'running',
            'app_status': app_status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'webhook_status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

if __name__ == '__main__':
    # Create log directory
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    logging.info("🚀 Starting GitHub webhook server...")
    app.run(host='0.0.0.0', port=8080, debug=False)
