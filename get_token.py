import requests
import re
import os

def main():
    # Try reading from .env to see if there is UIPATH_ORG
    org_env = ""
    env_path = ".env"
    if os.path.exists(env_path):
        try:
            with open(env_path, "r") as f:
                for line in f:
                    if line.startswith("UIPATH_ORG="):
                        org_env = line.split("=", 1)[1].strip()
                        break
        except Exception:
            pass

    print("=== UiPath Access Token Generator ===")
    print("Which UiPath environment are you targeting?")
    
    if org_env:
        if "hackathon" in org_env.lower() or "staging" in org_env.lower():
            env_default = "1"
            print(f"1) Staging / UiPath Labs (staging.uipath.com) [Recommended based on .env org: {org_env}]")
            print("2) Production Automation Cloud (cloud.uipath.com)")
        else:
            env_default = "2"
            print("1) Staging / UiPath Labs (staging.uipath.com)")
            print(f"2) Production Automation Cloud (cloud.uipath.com) [Recommended based on .env org: {org_env}]")
    else:
        env_default = "1"
        print("1) Staging / UiPath Labs (staging.uipath.com) [Default for Hackathon]")
        print("2) Production Automation Cloud (cloud.uipath.com)")

    env_choice = input(f"Select environment (1 or 2, default {env_default}): ").strip()
    if not env_choice:
        env_choice = env_default

    base_url = "https://staging.uipath.com" if env_choice == "1" else "https://cloud.uipath.com"
    url = f"{base_url}/identity_/connect/token"
    
    print("\nWhich authentication method are you using?")
    print("1) Method A: User Key / Refresh Token (from Tenants -> API Access)")
    print("2) Method B: External Application Client Credentials (from Admin -> External Applications)")
    
    choice = input("Select option (1 or 2): ").strip()
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    if choice == "2":
        print("\nPlease retrieve your App ID (Client ID) and App Secret from External Applications.")
        client_id = input("Enter App ID (Client ID): ").strip()
        client_secret = input("Enter App Secret: ").strip()
        
        if not client_id or not client_secret:
            print("Error: Both Client ID and Client Secret are required.")
            return
            
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret
        }
    else:
        print("\nPlease retrieve your Client ID and User Key from Tenants -> API Access.")
        client_id = input("Enter your Client ID: ").strip()
        user_key = input("Enter your User Key (Refresh Token): ").strip()

        if not client_id or not user_key:
            print("Error: Both Client ID and User Key are required.")
            return

        data = {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "refresh_token": user_key
        }

    try:
        print(f"\nRequesting access token from {base_url}...")
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            token = response.json().get("access_token")
            if token:
                print("Successfully retrieved access token!")
                
                env_path = ".env"
                if not os.path.exists(env_path):
                    if os.path.exists(".env.example"):
                        with open(".env.example", "r") as f:
                            content = f.read()
                    else:
                        content = "UIPATH_ACCESS_TOKEN="
                else:
                    with open(env_path, "r") as f:
                        content = f.read()
                
                # Replace or append the token
                if "UIPATH_ACCESS_TOKEN=" in content:
                    new_content = re.sub(r"UIPATH_ACCESS_TOKEN=.*", f"UIPATH_ACCESS_TOKEN={token}", content)
                else:
                    new_content = content.rstrip() + f"\nUIPATH_ACCESS_TOKEN={token}\n"
                    
                with open(env_path, "w") as f:
                    f.write(new_content)
                    
                print("Updated .env file with the new UIPATH_ACCESS_TOKEN.")
            else:
                print("Error: access_token not found in response.")
                print(response.json())
        else:
            print(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
