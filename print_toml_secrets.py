
import json
import os

def to_toml():
    # Try different paths to find credentials
    paths = [
        'credentials/credentials.json',
        '../credentials/credentials.json',
        'g:/내 드라이브/g_dev/#yebom/credentials/credentials.json'
    ]
    
    creds = None
    for p in paths:
        if os.path.exists(p):
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    creds = json.load(f)
                break
            except:
                pass
                
    if not creds:
        print("Error: Could not find credentials.json file to convert.")
        return

    print("# 아래 내용을 전부 복사해서 Streamlit Secrets에 붙여넣으세요.")
    print("# [Copy from below here]")
    print("")
    print("[gcp_service_account]")
    for k, v in creds.items():
        if isinstance(v, str):
            # JSON escape for newlines is \n, which is valid in TOML strings too if quoted
            # But python's repr() adds quotes and handles escaping nicely
            # However, we want key = "value"
            # json.dumps(v) will produce "string with \n" including quotes
            print(f'{k} = {json.dumps(v)}')
        else:
            print(f'{k} = {json.dumps(v)}')
            
    print("")
    print("# [Copy until here]")

if __name__ == "__main__":
    to_toml()
