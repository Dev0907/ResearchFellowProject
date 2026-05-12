import requests
import json

def test_analyze():
    url = "http://localhost:8000/api/analyze"
    payload = {
        "idea": "AI-powered sports analytics platform for amateur teams",
        "problem": "Amateur teams lack access to professional-grade data analytics",
        "audience": "Amateur sports clubs and individual athletes",
        "startup_name": "ProLevel"
    }
    
    try:
        print("Sending request to backend...")
        response = requests.post(url, json=payload, timeout=300)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Success!")
            # print(json.dumps(result, indent=2))
            print(f"Report Status: {result.get('status')}")
            if 'report' in result:
                print(f"Startup Name: {result['report'].get('startup_name')}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_analyze()
