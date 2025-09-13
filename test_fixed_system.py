import requests
import json
import time

def test_fixed_system():
    """Test the fixed otolith processing system"""
    
    print("=== Testing Fixed Otolith Processing System ===")
    
    # Test data
    test_data = {
        "image_id": f"test_fixed_{int(time.time())}",
        "image_data": "dummy_data_will_use_sample"  # API will use sample images
    }
    
    print(f"1. Testing API with image_id: {test_data['image_id']}")
    
    # Send request to API
    try:
        response = requests.post(
            "http://localhost:8000/api/ingest/otolith",
            json=test_data,
            timeout=10
        )
        
        print(f"API Response Status: {response.status_code}")
        print(f"API Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ API request successful")
        else:
            print("❌ API request failed")
            return False
            
    except Exception as e:
        print(f"❌ API request error: {e}")
        return False
    
    print("\n2. Waiting for worker processing (15 seconds)...")
    time.sleep(15)
    
    # Check database for results
    print("\n3. Checking database for processed data...")
    try:
        response = requests.get(
            "http://localhost:8000/api/dashboard/data",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Database records found: {len(data)}")
            
            if data:
                print("✅ Worker successfully processed images!")
                print("\nLatest record:")
                latest = data[0]
                for key, value in latest.items():
                    print(f"  {key}: {value}")
                return True
            else:
                print("❌ No data found in database")
                return False
        else:
            print(f"❌ Database query failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Database query error: {e}")
        return False

if __name__ == "__main__":
    success = test_fixed_system()
    if success:
        print("\n🎉 SYSTEM WORKING! Workers are processing images and saving data.")
    else:
        print("\n💥 System still has issues. Check container logs for details.")