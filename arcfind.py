import requests 
import signal 
import sys
import time
import re
import os
import threading

OUTPUT_FILE = "z_hasil.txt"
start_time = None 
stop_spinner = False
url_count = 0 

# KETIKA CTRL+C DITEKAN 
def signal_handler(sig, frame):
    global stop_spinner  # <--- penting, biar bisa ubah variabel global
    stop_spinner = True  # hentikan spinner
    print("\n[+] Command ctrl+c detected...")
    print("[+] Stop Program")
    print(f"[+] Result Save in {OUTPUT_FILE} ({url_count} URLs Saved)")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# FUNGSI SPINNER LOADING ANIMATION 
def spinner():
    while not stop_spinner:
        for c in "/-\\|":
            if stop_spinner:
                break
            sys.stdout.write(f"\r[+] Loading {c} {c} ")
            sys.stdout.flush()
            time.sleep(0.1)
    sys.stdout.write("\r")  # Hapus spinner setelah selesai

# FUNGSI UNTUK VALIDASI DOMAIN 
def validate_domain(domain):
    # Hapus protokol kalau ada
    domain = domain.strip().lower()
    domain = re.sub(r'^https?://','',domain)
    domain = domain.strip('/')

    # Cek Format TLD 
    if not re.search(r"\.[a-z]{2,}$", domain):
        return None 
    return domain

def main():
    global start_time, stop_spinner, url_count

    print("""
    ___              _______           __
   /   |  __________/ ____(_)___  ____/ /
  / /| | / ___/ ___/ /_  / / __ \/ __  / 
 / ___ |/ /  / /__/ __/ / / / / / /_/ /  
/_/  |_/_/   \___/_/   /_/_/ /_/\__,_/ 
          find archive resource""")
    
    target = input("[+] Input Domain: ").strip()
    domain = validate_domain(target) 

    if not domain:
        print("[+] Warning Follow This Format ex:hackerone.com")
        print("[+] Program Stop")
        return
    
    print("[+] Start Running...")
    print(f"[+] Target: {domain}")
    start_time = time.time()

    url = f"https://web.archive.org/cdx/search/cdx?url=*.{domain}/*&collapse=urlkey&output=text&fl=original"

    # Kosongkan file hasil.txt setiap kali program dijalankan
    if not os.path.exists(OUTPUT_FILE): 
        print(f"[+] Warning {OUTPUT_FILE} Not Found! Creating...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f: 
        f.write("")

    # Mulai Spinner di thread terpisah
    stop_spinner = False 
    t = threading.Thread(target=spinner, daemon=True)  # daemon=True biar otomatis mati
    t.start()

    try:
        with requests.get(url, timeout=None, stream=True) as response:
            response.raise_for_status()  
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                for line in response.iter_lines(decode_unicode=True):
                    if line:  
                        url_count += 1
                        f.write(line + "\n")
    except requests.exceptions.RequestException as e:
        stop_spinner = True
        t.join()
        print("[+] Warning Request Error: ", e)
        print("[+] Program Stop")
        return
    
    # Hentikan spinner setelah selesai
    stop_spinner = True
    t.join()

    finish_time = int(time.time() - start_time)
    print(f"[+] Finished in {finish_time} seconds")
    print(f"[+] Total URLs Found: {url_count}")
    print(f"[+] Result Saved in {OUTPUT_FILE} ({url_count} URLs Saved)")

if __name__ == "__main__":
    main()
