#!/usr/bin/env python3
"""
Test script to register and login a demo user
"""

import requests
import json

def test_auth():
    """Test user registration and login"""
    base_url = "http://localhost:8000"
    
    # Register a demo user
    print("Registering demo user...")
    register_data = {
        "user_id": "demo-user",
        "username": "Demo User",
        "email": "demo@example.com",
        "role": "child"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/auth/register",
            headers={"Content-Type": "application/json"},
            data=json.dumps(register_data)
        )
        
        if response.status_code == 200:
            print("✅ Demo user registered successfully")
            token = response.json()["access_token"]
            print(f"Access token: {token[:20]}...")
        else:
            print(f"⚠️ Registration failed with status {response.status_code}")
            print(response.text)
            
            # Try to login instead
            print("\nTrying to login...")
            login_data = {
                "user_id": "demo-user",
                "password": ""
            }
            
            response = requests.post(
                f"{base_url}/api/v1/auth/login",
                headers={"Content-Type": "application/json"},
                data=json.dumps(login_data)
            )
            
            if response.status_code == 200:
                print("✅ Demo user logged in successfully")
                token = response.json()["access_token"]
                print(f"Access token: {token[:20]}...")
                return token
            else:
                print(f"❌ Login failed with status {response.status_code}")
                print(response.text)
                return None
                
        return token
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    test_auth()