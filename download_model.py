import os
import sys
import time
import requests

url = "https://huggingface.co/llmfan46/gemma-4-E4B-it-ultra-uncensored-heretic-GGUF/resolve/main/gemma-4-E4B-it-ultra-uncensored-heretic-Q4_K_M.gguf"
dest = "G:\\Shared\\models\\gemma-4-E4B-it-ultra-uncensored-heretic-Q4_K_M.gguf"
min_bytes = 4000000000

def download():
    # If the file already exists and is valid, skip
    if os.path.exists(dest) and os.path.getsize(dest) > min_bytes:
        print("Model already fully downloaded!")
        return True

    print(f"Downloading from {url}")
    print(f"Destination: {dest}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    temp_size = 0
    if os.path.exists(dest):
        temp_size = os.path.getsize(dest)
        # If the file is reasonably large, try to resume
        if temp_size > 1024 * 1024:
            headers['Range'] = f'bytes={temp_size}-'
            print(f"Resuming download from byte {temp_size}...")
        else:
            temp_size = 0
            
    mode = 'ab' if temp_size > 0 else 'wb'
    
    try:
        r = requests.get(url, headers=headers, stream=True, timeout=20)
        
        # Check status codes
        if temp_size > 0 and r.status_code == 416:  # Range Not Satisfiable
            print("Range not satisfiable. Restarting download from scratch...")
            r = requests.get(url, stream=True, timeout=20)
            mode = 'wb'
            temp_size = 0
        elif temp_size > 0 and r.status_code != 206:
            print(f"Server returned status {r.status_code} (no range support). Restarting download...")
            r = requests.get(url, stream=True, timeout=20)
            mode = 'wb'
            temp_size = 0
            
        r.raise_for_status()
        
        content_len = int(r.headers.get('content-length', 0))
        total_size = content_len + temp_size
        downloaded = temp_size
        
        start_time = time.time()
        last_print = start_time
        bytes_in_session = 0
        
        print(f"Total size: {total_size} bytes (already downloaded: {temp_size} bytes)")
        
        with open(dest, mode) as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    bytes_in_session += len(chunk)
                    
                    now = time.time()
                    if now - last_print > 3:
                        percent = (downloaded / total_size) * 100 if total_size else 0
                        elapsed = now - start_time
                        speed = bytes_in_session / elapsed / (1024 * 1024) if elapsed > 0 else 0
                        print(f"Progress: {downloaded}/{total_size} bytes ({percent:.2f}%) | Session Speed: {speed:.2f} MB/s", flush=True)
                        last_print = now
                        
        print("Download session finished successfully!")
        return True
    except Exception as e:
        print(f"Download failed/interrupted: {e}")
        return False

if __name__ == "__main__":
    success = False
    for attempt in range(1, 15):
        print(f"\n--- Resumable Download Attempt {attempt} ---")
        success = download()
        if success and os.path.exists(dest) and os.path.getsize(dest) > min_bytes:
            print("Successfully completed download!")
            break
        print("Waiting 5 seconds before retrying...")
        time.sleep(5)



