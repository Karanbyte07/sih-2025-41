#!/usr/bin/env python3
import requests
import time
import json

def test_end_to_end():
    """Test the complete end-to-end pipeline"""
    
    print("🧪 Starting end-to-end test...")
    
    # Step 1: Test API endpoint
    sample_data = {
        "image_id": f"e2e-test-{int(time.time())}",
        "image_data": "iVBORw0KGgoAAAANSUhEUgAAAGAAAAA8CAYAAAD2a2KkAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAGVSURBVHhe7dJBCsNADADBi/T/d7ZDIgo+sRQEkl3b2Y//AY6gQBYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRa8A3oDk/oBEJt3AAAAAElFTkSuQmCC"
    }
    
    print(f"📤 Sending request for image_id: {sample_data['image_id']}")
    
    try:
        # Submit to API
        response = requests.post("http://localhost:8000/api/ingest/otolith", 
                               json=sample_data, 
                               timeout=10)
        
        print(f"📡 API Response: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ API Success: {response.json()}")
        else:
            print(f"❌ API Error: {response.text}")
            return False
            
        # Wait for processing
        print("⏳ Waiting 10 seconds for processing...")
        time.sleep(10)
        
        # Check dashboard
        dashboard_response = requests.get("http://localhost:8000/api/dashboard/data")
        print(f"📊 Dashboard Response: {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 200:
            data = dashboard_response.json()
            print(f"📈 Records in database: {len(data)}")
            
            # Look for our record
            found = False
            for record in data:
                if record.get('image_id') == sample_data['image_id']:
                    print(f"🎯 Found our record: {record}")
                    found = True
                    break
            
            if found:
                print("✅ END-TO-END TEST PASSED!")
                return True
            else:
                print("❌ Our record not found in dashboard")
                if data:
                    print("Available records:")
                    for record in data:
                        print(f"  - {record.get('image_id', 'Unknown')}")
                return False
        else:
            print(f"❌ Dashboard error: {dashboard_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_frontend_simulation():
    """Simulate what the frontend does"""
    
    print("🖥️ Simulating frontend behavior...")
    
    # This is exactly what the frontend sends
    frontend_data = {
        "image_data": "iVBORw0KGgoAAAANSUhEUgAAAGAAAAA8CAYAAAD2a2KkAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAGVSURBVHhe7dJBCsNADADBi/T/d7ZDIgo+sRQEkl3b2Y//AY6gQBYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRa8A3oDk/oBEJt3AAAAAElFTkSuQmCC",
        "image_id": f"sample-{int(time.time() * 1000)}",  # Frontend uses milliseconds
        "latitude": 12.45,
        "longitude": 75.23
    }
    
    return test_request(frontend_data)

def test_request(data):
    """Test a specific request"""
    try:
        print(f"📤 Testing with: {data['image_id']}")
        response = requests.post("http://localhost:8000/api/ingest/otolith", 
                               json=data, timeout=10)
        print(f"📡 Response: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Running comprehensive tests...")
    
    # Test 1: Basic API functionality
    print("\n" + "="*50)
    print("TEST 1: Frontend Simulation")
    print("="*50)
    frontend_success = test_frontend_simulation()
    
    # Test 2: End-to-end pipeline
    print("\n" + "="*50)
    print("TEST 2: End-to-End Pipeline")
    print("="*50)
    e2e_success = test_end_to_end()
    
    print("\n" + "="*50)
    print("FINAL RESULTS")
    print("="*50)
    print(f"Frontend simulation: {'✅ PASS' if frontend_success else '❌ FAIL'}")
    print(f"End-to-end pipeline: {'✅ PASS' if e2e_success else '❌ FAIL'}")
    
    if frontend_success and e2e_success:
        print("🎉 ALL TESTS PASSED - System is working!")
    else:
        print("⚠️ Some tests failed - Check logs for issues")