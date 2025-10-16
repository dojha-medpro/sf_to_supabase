"""Test script for CloudMailin webhook integration."""
import requests
import base64
import json
from pathlib import Path

# Sample CloudMailin payload with base64-encoded CSV
def create_test_payload():
    """Create a sample CloudMailin JSON payload with CSV attachment."""
    
    # Read sample CSV file
    sample_csv_path = Path('test_contacts_sample.csv')
    
    if not sample_csv_path.exists():
        print(f"❌ Sample file not found: {sample_csv_path}")
        print("Creating a minimal test CSV...")
        sample_csv_content = """Full Name,Contact ID,Email,Phone
John Doe,001,john@example.com,555-1234
Jane Smith,002,jane@example.com,555-5678
"""
        sample_csv_path.write_text(sample_csv_content)
    
    csv_content = sample_csv_path.read_bytes()
    csv_base64 = base64.b64encode(csv_content).decode('utf-8')
    
    payload = {
        "envelope": {
            "to": "etl@mycompany.cloudmailin.net",
            "recipients": ["etl@mycompany.cloudmailin.net"],
            "from": "salesforce@example.com",
            "helo_domain": "example.com",
            "remote_ip": "192.0.2.1",
            "spf": {
                "result": "pass",
                "domain": "example.com"
            },
            "tls": True
        },
        "headers": {
            "subject": "Salesforce Daily Export - Contacts",
            "from": "Salesforce Reports <salesforce@example.com>",
            "to": "ETL Pipeline <etl@mycompany.cloudmailin.net>",
            "date": "Thu, 16 Oct 2025 12:00:00 +0000",
            "message_id": "<test123@example.com>"
        },
        "plain": "Attached is the daily contacts export from Salesforce.",
        "html": "<p>Attached is the daily contacts export from Salesforce.</p>",
        "attachments": [
            {
                "content": csv_base64,
                "file_name": "contacts_daily_export.csv",
                "content_type": "text/csv",
                "size": len(csv_content),
                "disposition": "attachment"
            }
        ]
    }
    
    return payload


def test_webhook_local():
    """Test webhook on local Flask server."""
    
    webhook_url = "http://localhost:5000/webhook/cloudmailin"
    
    print("🧪 Testing CloudMailin Webhook Integration\n")
    print(f"📬 Sending test payload to: {webhook_url}")
    
    payload = create_test_payload()
    
    print(f"📎 Attachments: {len(payload['attachments'])} file(s)")
    print(f"   - {payload['attachments'][0]['file_name']} ({payload['attachments'][0]['size']} bytes)\n")
    
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Body:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            print("\n✅ Webhook test PASSED!")
            print("   → Check /history page to verify the load")
        else:
            print(f"\n❌ Webhook test FAILED with status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Flask server not running")
        print("   → Start the Flask app first: python main.py")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")


def test_webhook_replit():
    """Test webhook on Replit deployment."""
    
    # User needs to replace this with their actual Replit domain
    replit_domain = input("Enter your Replit domain (e.g., abc123.replit.app): ").strip()
    
    if not replit_domain:
        print("❌ No domain provided")
        return
    
    webhook_url = f"https://{replit_domain}/webhook/cloudmailin"
    
    print(f"\n🧪 Testing CloudMailin Webhook on Replit\n")
    print(f"📬 Sending test payload to: {webhook_url}")
    
    payload = create_test_payload()
    
    print(f"📎 Attachments: {len(payload['attachments'])} file(s)")
    print(f"   - {payload['attachments'][0]['file_name']} ({payload['attachments'][0]['size']} bytes)\n")
    
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Body:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            print("\n✅ Webhook test PASSED!")
            print(f"   → Check https://{replit_domain}/history to verify the load")
        else:
            print(f"\n❌ Webhook test FAILED with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")


if __name__ == "__main__":
    print("CloudMailin Webhook Test Suite\n")
    print("1. Test local Flask server (http://localhost:5000)")
    print("2. Test Replit deployment (https://your-domain.replit.app)")
    
    choice = input("\nSelect option (1 or 2): ").strip()
    
    if choice == "1":
        test_webhook_local()
    elif choice == "2":
        test_webhook_replit()
    else:
        print("Invalid choice")
