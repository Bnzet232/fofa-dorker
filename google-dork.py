#!/usr/bin/env python3
# Google Dorking Tool FIXED
# Created by: bnzet

import requests
from bs4 import BeautifulSoup
import argparse
import time
import random
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote_plus, urlparse

# ===== CONFIG =====
MAX_RESULTS = 30
DELAY = 3
TIMEOUT = 20
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
]

class GoogleDorker:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        })

    def manual_google_search(self, dork, num_results=MAX_RESULTS):
        """Manual Google search dengan parsing HTML"""
        results = []
        try:
            encoded_dork = quote_plus(dork)
            url = f"https://www.google.com/search?q={encoded_dork}&num={num_results}"
            
            print(f"\033[1;33m[+] Searching: {dork}\033[0m")
            
            response = self.session.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Beberapa pattern untuk menemukan hasil
            selectors = [
                'div.g a[href*="/url?q="]',
                'a[href*="/url?q="]',
                '.rc a',
                '.r a'
            ]
            
            for selector in selectors:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href')
                    if href and '/url?q=' in href:
                        actual_url = href.split('/url?q=')[1].split('&')[0]
                        actual_url = requests.utils.unquote(actual_url)
                        
                        if 'google.com' not in actual_url and actual_url not in results:
                            results.append(actual_url)
                            print(f"\033[1;32m[+] Found: {actual_url[:80]}...\033[0m")
            
            return results
            
        except Exception as e:
            print(f"\033[1;31m[!] Search error: {str(e)}\033[0m")
            return results

    def alternative_search_method(self, dork):
        """Alternative method menggunakan different approach"""
        try:
            encoded_dork = quote_plus(dork)
            url = f"https://www.google.com/search?q={encoded_dork}&num=10"
            
            headers = {
                'User-Agent': random.choice(USER_AGENTS),
                'Referer': 'https://www.google.com/'
            }
            
            response = requests.get(url, headers=headers, timeout=TIMEOUT)
            
            # Regex pattern untuk mencari URLs
            pattern = r'https?://[^\s"<>]+'
            urls = re.findall(pattern, response.text)
            
            filtered_urls = []
            for url in urls:
                if ('google.com' not in url and 
                    '/search?' not in url and 
                    url.startswith('http') and
                    url not in filtered_urls):
                    filtered_urls.append(url)
                    print(f"\033[1;34m[+] Alternative found: {url[:80]}...\033[0m")
            
            return filtered_urls[:10]
                    
        except Exception as e:
            print(f"\033[1;31m[!] Alternative search error: {str(e)}\033[0m")
            return []

    def save_results(self, results, dork, filename):
        """Save results dengan error handling"""
        try:
            # Pastikan directory exists
            if filename and os.path.dirname(filename):
                os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'a', encoding='utf-8') as f:
                for result in results:
                    data = {
                        'dork': dork,
                        'url': result,
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    f.write(json.dumps(data) + '\n')
                    
            print(f"\033[1;32m[✓] Results saved to: {filename}\033[0m")
            
        except Exception as e:
            print(f"\033[1;31m[!] Error saving results: {str(e)}\033[0m")
            # Fallback: save to default file
            try:
                with open('google_dork_results.txt', 'a', encoding='utf-8') as f:
                    for result in results:
                        data = {
                            'dork': dork,
                            'url': result,
                            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                        }
                        f.write(json.dumps(data) + '\n')
                print(f"\033[1;32m[✓] Results saved to default file: google_dork_results.txt\033[0m")
            except:
                print(f"\033[1;31m[!] Failed to save results to any file\033[0m")

    def process_dork(self, dork, output_file="google_dork_results.txt"):
        """Process dork dengan multiple methods"""
        print(f"\n\033[1;36m[═] Processing: {dork}\033[0m")
        
        all_results = []
        
        # Method 1: Manual Google search
        print("\033[1;33m[→] Trying manual Google search...\033[0m")
        results1 = self.manual_google_search(dork)
        all_results.extend(results1)
        
        time.sleep(DELAY)
        
        # Method 2: Alternative search
        if not results1:
            print("\033[1;33m[→] Trying alternative method...\033[0m")
            results2 = self.alternative_search_method(dork)
            all_results.extend(results2)
        
        # Remove duplicates
        all_results = list(set(all_results))
        
        # Save results
        if all_results:
            self.save_results(all_results, dork, output_file)
            print(f"\033[1;32m[✓] Found {len(all_results)} unique results\033[0m")
        else:
            print("\033[1;31m[✗] No results found\033[0m")
            
        return all_results

def show_banner():
    print("""
\033[1;36m
 ██████╗  ██████╗  ██████╗ ██╗     ███████╗    ██████╗  ██████╗ ██████╗ ██╗  ██╗
██╔════╝ ██╔═══██╗██╔═══██╗██║     ██╔════╝    ██╔══██╗██╔═══██╗██╔══██╗██║ ██╔╝
██║  ███╗██║   ██║██║   ██║██║     █████╗      ██║  ██║██║   ██║██████╔╝█████╔╝ 
██║   ██║██║   ██║██║   ██║██║     ██╔══╝      ██║  ██║██║   ██║██╔══██╗██╔═██╗ 
╚██████╔╝╚██████╔╝╚██████╔╝███████╗███████╗    ██████╔╝╚██████╔╝██║  ██║██║  ██╗
 ╚═════╝  ╚═════╝  ╚═════╝ ╚══════╝╚══════╝    ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
\033[0m
\033[1;32mGoogle Dorking Tool FIXED | Created by: bnzet\033[0m
\033[1;33mGithub: https://github.com/bnzet\033[0m
\033[1;31m[!] For authorized security research only\033[0m
""")

def main():
    parser = argparse.ArgumentParser(description='Google Dorking Tool - FIXED VERSION')
    parser.add_argument('-d', '--dork', help='Google dork query')
    parser.add_argument('-f', '--file', help='File dengan multiple dorks')
    parser.add_argument('-o', '--output', default='google_dork_results.txt', help='Output file')
    
    args = parser.parse_args()
    
    show_banner()
    
    if not args.dork and not args.file:
        print("\033[1;31m[!] Please provide either -d for dork or -f for file\033[0m")
        print("\033[1;33m[?] Example: python3 google-dork.py -d 'site:github.com'\033[0m")
        return
    
    dorker = GoogleDorker()
    
    if args.dork:
        dorker.process_dork(args.dork, args.output)
    elif args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                dorks = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            print(f"\033[1;33m[+] Loaded {len(dorks)} dorks from file\033[0m")
            
            for i, dork in enumerate(dorks, 1):
                print(f"\033[1;35m[═] Dork {i}/{len(dorks)}\033[0m")
                dorker.process_dork(dork, args.output)
                
                # Delay antara dorks
                if i < len(dorks):
                    delay = random.randint(3, 7)
                    print(f"\033[1;33m[⏳] Waiting {delay} seconds...\033[0m")
                    time.sleep(delay)
                    
        except FileNotFoundError:
            print(f"\033[1;31m[!] File not found: {args.file}\033[0m")
        except Exception as e:
            print(f"\033[1;31m[!] Error reading file: {str(e)}\033[0m")

if __name__ == '__main__':
    main()
