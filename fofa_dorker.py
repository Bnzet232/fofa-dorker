#!/usr/bin/env python3
# FOFA Dorking Tool
# Created by: bnzet

import requests
import json
import argparse
from concurrent.futures import ThreadPoolExecutor
import time
import os

# ===== CONFIG =====
FOFA_API_URL = "https://fofa.info/api/v1/search/all"
MAX_RESULTS = 1000  # Maximum results to fetch per request
DELAY = 2  # Delay between requests to avoid rate limiting
TIMEOUT = 15  # Request timeout in seconds
RESULTS_FILE = "fofa_results.txt"

# ===== ASCII ART =====
def show_banner():
    print("""
\033[1;36m
███████╗ ██████╗ ███████╗ █████╗     ██████╗  ██████╗ ██████╗ ██╗  ██╗
██╔════╝██╔═══██╗██╔════╝██╔══██╗    ██╔══██╗██╔═══██╗██╔══██╗██║ ██╔╝
█████╗  ██║   ██║█████╗  ███████║    ██║  ██║██║   ██║██████╔╝█████╔╝ 
██╔══╝  ██║   ██║██╔══╝  ██╔══██║    ██║  ██║██║   ██║██╔══██╗██╔═██╗ 
██║     ╚██████╔╝██║     ██║  ██║    ██████╔╝╚██████╔╝██║  ██║██║  ██╗
╚═╝      ╚═════╝ ╚═╝     ╚═╝  ╚═╝    ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
\033[0m
\033[1;32mFOFA Dorking Tool | Created by: bnzet\033[0m
\033[1;33mGithub: https://github.com/bnzet/fofa-dorker\033[0m
\033[1;31m[!] For authorized security research only\033[0m
""")

# ===== FOFA API FUNCTIONS =====
class FofaClient:
    def __init__(self, email, key):
        self.email = email
        self.key = key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def search(self, dork, page=1, fields="ip,port,host,title,server,country"):
        params = {
            'qbase64': base64_encode(dork),
            'email': self.email,
            'key': self.key,
            'page': page,
            'size': MAX_RESULTS,
            'fields': fields
        }
        
        try:
            response = self.session.get(FOFA_API_URL, params=params, timeout=TIMEOUT)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"\033[1;31m[!] Error: {str(e)}\033[0m")
            return None

def base64_encode(string):
    import base64
    return base64.b64encode(string.encode('utf-8')).decode('utf-8')

# ===== RESULT PROCESSING =====
def save_results(results, filename=RESULTS_FILE):
    if not results:
        return
    
    # Create results directory if not exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'a', encoding='utf-8') as f:
        for result in results:
            f.write(json.dumps(result, ensure_ascii=False) + '\n')
    
    print(f"\033[1;32m[+] Saved {len(results)} results to {filename}\033[0m")

def format_result(result, fields):
    formatted = {}
    values = result.split(',')
    for i, field in enumerate(fields.split(',')):
        if i < len(values):
            formatted[field.strip()] = values[i].strip()
    return formatted

# ===== MAIN FUNCTION =====
def main():
    parser = argparse.ArgumentParser(description='FOFA Dorking Tool')
    parser.add_argument('-e', '--email', required=True, help='FOFA email')
    parser.add_argument('-k', '--key', required=True, help='FOFA API key')
    parser.add_argument('-d', '--dork', help='FOFA dork query')
    parser.add_argument('-f', '--file', help='File containing multiple dorks (one per line)')
    parser.add_argument('-o', '--output', default=RESULTS_FILE, help='Output file path')
    parser.add_argument('-p', '--pages', type=int, default=1, help='Number of pages to fetch')
    parser.add_argument('-t', '--threads', type=int, default=3, help='Number of threads')
    parser.add_argument('--fields', default='ip,port,host,title,server,country',
                       help='Fields to retrieve (comma separated)')
    
    args = parser.parse_args()
    show_banner()
    
    if not args.dork and not args.file:
        print("\033[1;31m[!] Please provide either a dork (-d) or a file with dorks (-f)\033[0m")
        return
    
    client = FofaClient(args.email, args.key)
    dorks = []
    
    if args.dork:
        dorks.append(args.dork)
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                dorks.extend([line.strip() for line in f if line.strip()])
        except Exception as e:
            print(f"\033[1;31m[!] Error reading file: {str(e)}\033[0m")
            return
    
    print(f"\033[1;33m[+] Loaded {len(dorks)} dork queries\033[0m")
    
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        for dork in dorks:
            print(f"\n\033[1;36m[+] Processing dork: {dork}\033[0m")
            
            for page in range(1, args.pages + 1):
                print(f"\033[1;33m[+] Fetching page {page}\033[0m")
                result = client.search(dork, page=page, fields=args.fields)
                
                if not result or 'error' in result:
                    print(f"\033[1;31m[!] Error in response: {result.get('errmsg', 'Unknown error')}\033[0m")
                    break
                
                if not result.get('results'):
                    print("\033[1;33m[!] No results found\033[0m")
                    break
                
                # Format and save results
                formatted_results = []
                for item in result['results']:
                    formatted = format_result(item, args.fields)
                    formatted['dork'] = dork
                    formatted_results.append(formatted)
                
                save_results(formatted_results, args.output)
                
                # Respect rate limits
                if page < args.pages:
                    time.sleep(DELAY)

if __name__ == '__main__':
    main()
