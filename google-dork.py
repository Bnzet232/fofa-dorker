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
MAX_RESULTS = 30  # Reduce untuk avoid blocking
DELAY = 3  # Increase delay
TIMEOUT = 20
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
]

class GoogleDorker:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def manual_google_search(self, dork, num_results=MAX_RESULTS):
        """Manual Google search dengan parsing HTML"""
        results = []
        try:
            # Encode dork untuk URL
            encoded_dork = quote_plus(dork)
            url = f"https://www.google.com/search?q={encoded_dork}&num={num_results}"
            
            print(f"\033[1;33m[+] Searching: {dork}\033[0m")
            print(f"\033[1;33m[+] URL: {url}\033[0m")
            
            response = self.session.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            
            # Parse HTML untuk hasil
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Cari semua link hasil
            for g in soup.find_all('div', class_='g'):
                link = g.find('a')
                if link and link.get('href'):
                    href = link.get('href')
                    if href.startswith('/url?q='):
                        # Extract actual URL
                        actual_url = href.split('/url?q=')[1].split('&')[0]
                        actual_url = requests.utils.unquote(actual_url)
                        
                        # Skip Google URLs
                        if 'google.com' not in actual_url:
                            results.append(actual_url)
                            print(f"\033[1;32m[+] Found: {actual_url}\033[0m")
            
            return results
            
        except Exception as e:
            print(f"\033[1;31m[!] Search error: {str(e)}\033[0m")
            return results

    def alternative_search_method(self, dork):
        """Alternative method menggunakan different approach"""
        try:
            # Gunakan different Google domain
            domains = [
                "https://www.google.com",
                "https://www.google.co.id", 
                "https://www.google.com.hk"
            ]
            
            for domain in domains:
                try:
                    encoded_dork = quote_plus(dork)
                    url = f"{domain}/search?q={encoded_dork}&num=10"
                    
                    headers = {
                        'User-Agent': random.choice(USER_AGENTS),
                        'Referer': domain
                    }
                    
                    response = requests.get(url, headers=headers, timeout=TIMEOUT)
                    
                    # Simple regex untuk find URLs
                    pattern = r'https?://[^\s"<>]+'
                    urls = re.findall(pattern, response.text)
                    
                    # Filter hanya external URLs
                    filtered_urls = []
                    for url in urls:
                        if 'google.com' not in url and '/search?' not in url:
                            if url not in filtered_urls:
                                filtered_urls.append(url)
                                print(f"\033[1;34m[+] Alternative found: {url}\033[0m")
                    
                    if filtered_urls:
                        return filtered_urls[:10]  # Limit results
                        
                except:
                    continue
                    
        except Exception as e:
            print(f"\033[1;31m[!] Alternative search error: {str(e)}\033[0m")
        
        return []

    def process_dork(self, dork, output_file="results.txt"):
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
        
        # Save results
        if all_results:
            self.save_results(all_results, dork, output_file)
            print(f"\033[1;32m[✓] Found {len(all_results)} results\033[0m")
        else:
            print("\033[1;31m[✗] No results found\033[0m")
            
        return all_results

    def save_results(self, results, dork, filename):
        """Save results"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'a', encoding='utf-8') as f:
            for result in results:
                data = {
                    'dork': dork,
                    'url': result,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                f.write(json.dumps(data) + '\n')

def main():
    parser = argparse.ArgumentParser(description='Google Dorking Tool - FIXED')
    parser.add_argument('-d', '--dork', help='Google dork query')
    parser.add_argument('-f', '--file', help='File dengan multiple dorks')
    parser.add_argument('-o', '--output', default='google_results.txt', help='Output file')
    
    args = parser.parse_args()
    
    print("\033[1;36m" + "="*60)
    print("           GOOGLE DORKING TOOL - FIXED VERSION")
    print("           Created by: bnzet")
    print("="*60 + "\033[0m")
    
    dorker = GoogleDorker()
    
    if args.dork:
        dorker.process_dork(args.dork, args.output)
    elif args.file:
        with open(args.file, 'r') as f:
            dorks = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        for dork in dorks:
            dorker.process_dork(dork, args.output)
            time.sleep(random.randint(2, 5))  # Random delay

if __name__ == '__main__':
    main()
