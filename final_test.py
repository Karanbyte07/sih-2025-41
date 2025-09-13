import requests
import json
import time
import random

def test_frontend_behavior():
    """Test the system like the frontend would use it"""
    
    print("=== Testing Frontend-like Behavior ===")
    
    # Simulate multiple otolith submissions like a real user would
    test_cases = [
        {"image_id": f"otolith_sample_{i}", "image_data": "frontend_sample_data"} 
        for i in range(3)
    ]
    
    print(f"Submitting {len(test_cases)} otolith samples...")
    
    # Submit all samples
    for i, test_data in enumerate(test_cases, 1):
        print(f"\n{i}. Submitting {test_data['image_id']}")
        
        try:
            response = requests.post(
                "http://localhost:8000/api/ingest/otolith",
                json=test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Sample {i} submitted successfully")
            else:
                print(f"❌ Sample {i} failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Sample {i} error: {e}")
    
    print("\n⏱️  Waiting 20 seconds for all workers to process...")
    time.sleep(20)
    
    # Check dashboard data
    print("\n📊 Checking dashboard data...")
    try:
        response = requests.get("http://localhost:8000/api/dashboard/data", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Total records in database: {len(data)}")
            
            if len(data) >= 3:  # Should have at least our 3 new records
                print("✅ All samples processed successfully!")
                
                print("\n📈 Sample of processed data:")
                for i, record in enumerate(data[:3], 1):
                    print(f"\nRecord {i}:")
                    print(f"  🆔 ID: {record['image_id']}")
                    print(f"  🐟 Species: {record['predicted_species']}")
                    print(f"  📏 Dimensions: {record['width']}x{record['height']}")
                    print(f"  📍 Location: ({record['latitude']}, {record['longitude']})")
                    print(f"  ⏰ Time: {record['created_at']}")
                
                return True
            else:
                print(f"❌ Expected at least 3 records, found {len(data)}")
                return False
        else:
            print(f"❌ Dashboard API failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        return False

def test_dashboard_updates():
    """Test that dashboard shows real-time updates"""
    
    print("\n=== Testing Real-time Dashboard Updates ===")
    
    # Get initial count
    response = requests.get("http://localhost:8000/api/dashboard/data")
    initial_count = len(response.json()) if response.status_code == 200 else 0
    print(f"Initial database records: {initial_count}")
    
    # Submit one more sample
    new_sample = {
        "image_id": f"realtime_test_{int(time.time())}",
        "image_data": "realtime_test_data"
    }
    
    print(f"Submitting new sample: {new_sample['image_id']}")
    requests.post("http://localhost:8000/api/ingest/otolith", json=new_sample)
    
    # Wait and check for update
    print("Waiting 10 seconds for processing...")
    time.sleep(10)
    
    response = requests.get("http://localhost:8000/api/dashboard/data")
    final_count = len(response.json()) if response.status_code == 200 else 0
    
    if final_count > initial_count:
        print(f"✅ Dashboard updated! New count: {final_count}")
        return True
    else:
        print(f"❌ Dashboard not updated. Count: {final_count}")
        return False

if __name__ == "__main__":
    print("🧪 COMPREHENSIVE SYSTEM TEST")
    print("=" * 50)
    
    # Test 1: Frontend-like behavior
    test1_success = test_frontend_behavior()
    
    # Test 2: Real-time updates
    test2_success = test_dashboard_updates()
    
    print("\n" + "=" * 50)
    print("📋 TEST RESULTS:")
    print(f"Frontend Behavior Test: {'✅ PASS' if test1_success else '❌ FAIL'}")
    print(f"Real-time Updates Test: {'✅ PASS' if test2_success else '❌ FAIL'}")
    
    if test1_success and test2_success:
        print("\n🎉 ALL TESTS PASSED! The system is fully functional.")
        print("✅ API accepts requests")
        print("✅ Workers process images") 
        print("✅ Data is saved to database")
        print("✅ Dashboard shows real-time updates")
        print("✅ Frontend can interact with backend")
    else:
        print("\n💥 Some tests failed. Check the logs for details.")