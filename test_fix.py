import requests
import base64
import json
import time

def test_otolith_processing():
    """Test that the otolith processing pipeline works end-to-end"""
    
    # Create a simple test image (small PNG)
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAGhxI7nYwAAAABJRU5ErkJggg=="
    
    # Test data
    test_data = {
        "image_id": f"test-{int(time.time())}",
        "image_data": test_image_b64
    }
    
    print(f"Testing with image_id: {test_data['image_id']}")
    print(f"Image data length: {len(test_data['image_data'])}")
    
    # Submit to API
    try:
        response = requests.post("http://localhost:8000/api/ingest/otolith", 
                               json=test_data, 
                               timeout=10)
        print(f"API Response Status: {response.status_code}")
        print(f"API Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ API accepted the request")
            
            # Wait a moment for processing
            print("Waiting 5 seconds for processing...")
            time.sleep(5)
            
            # Check dashboard data
            dashboard_response = requests.get("http://localhost:8000/api/dashboard/data")
            print(f"Dashboard Response Status: {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 200:
                data = dashboard_response.json()
                print(f"Dashboard data count: {len(data)}")
                
                # Look for our test image
                test_record = None
                for record in data:
                    if record.get('image_id') == test_data['image_id']:
                        test_record = record
                        break
                
                if test_record:
                    print("✅ Test record found in database!")
                    print(f"Record: {test_record}")
                    return True
                else:
                    print("❌ Test record not found in database")
                    print(f"Available records: {[r.get('image_id') for r in data]}")
                    return False
            else:
                print(f"❌ Dashboard API failed: {dashboard_response.text}")
                return False
        else:
            print(f"❌ API rejected the request: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    print("Testing otolith processing pipeline...")
    success = test_otolith_processing()
    print(f"\nTest result: {'PASSED' if success else 'FAILED'}")