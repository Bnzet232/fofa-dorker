#!/usr/bin/env python3
# Google Dorking Tool
# Created by: bnzet

import requests
from bs4 import BeautifulSoup
import argparse
import time
import random
import json
import os
import re
from urllib.parse import urlparse, quote_plus
from concurrent.futures import ThreadPoolExecutor

# ===== CONFIG =====
MAX_RESULTS = 50  # Reduced to avoid blocking
DELAY = 3  # Increased delay to avoid blocking
TIMEOUT = 15
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
]
RESULTS_FILE = "google_dork_results.txt"
GOOGLE_SEARCH_URL = "https://www.google.com/search"

# ===== ASCII ART =====
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
\033[1;32mGoogle Dorking Tool | Created by: bnzet\033[0m
\033[1;33mGithub: https://github.com/bnzet/google-dorker\033[0m
\033[1;31m[!] For authorized security research only\033[0m
\033[1;31m[!] Use responsibly and respect robots.txt\033[0m
""")

# ===== GOOGLE DORKING CLASS =====
class GoogleDorker:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': random.choice(USER_AGENTS)})
        self.results = []

    def get_random_user_agent(self):
        return random.choice(USER_AGENTS)

    def google_search(self, dork, num_results=MAX_RESULTS, start=0):
        """Perform Google search manually by scraping results"""
        try:
            print(f"\033[1;33m[+] Searching for: {dork}\033[0m")
            
            params = {
                'q': dork,
                'num': min(100, num_results),
                'start': start,
                'hl': 'en',
                'filter': '0'
            }
            
            headers = {
                'User-Agent': self.get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = self.session.get(
                GOOGLE_SEARCH_URL,
                params=params,
                headers=headers,
                timeout=TIMEOUT
            )
            
            if response.status_code != 200:
                print(f"\033[1;31m[!] Google returned status code: {response.status_code}\033[0m")
                return []
            
            return self.parse_google_results(response.text)
            
        except Exception as e:
            print(f"\033[1;31m[!] Search error: {str(e)}\033[0m")
            return []

    def parse_google_results(self, html_content):
        """Parse Google search results from HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []
        
        # Find search result links
        for g in soup.find_all('div', class_='g'):
            link = g.find('a')
            if link and link.get('href'):
                url = link.get('href')
                if url.startswith('/url?q='):
                    url = url.split('/url?q=')[1].split('&')[0]
                    url = requests.utils.unquote(url)
                
                # Filter out Google URLs and validate
                if (url.startswith('http') and 
                    not urlparse(url).netloc.endswith('google.com')):
                    results.append(url)
        
        return results

    def process_dork(self, dork, max_results=MAX_RESULTS, output_file=RESULTS_FILE):
        """Process a single dork query"""
        print(f"\n\033[1;36m[+] Processing dork: {dork}\033[0m")
        
        try:
            all_results = []
            results_per_page = 10
            pages_needed = (max_results + results_per_page - 1) // results_per_page
            
            for page in range(pages_needed):
                start = page * results_per_page
                results = self.google_search(dork, results_per_page, start)
                
                if not results:
                    print("\033[1;33m[!] No results found or blocked by Google\033[0m")
                    break
                
                for result in results:
                    if len(all_results) >= max_results:
                        break
                    all_results.append(result)
                
                print(f"\033[1;32m[+] Found {len(results)} results on page {page + 1}\033[0m")
                
                # Add delay to avoid blocking
                time.sleep(random.uniform(DELAY, DELAY + 2))
                
                if len(all_results) >= max_results:
                    break
            
            if all_results:
                formatted_results = []
                for i, url in enumerate(all_results, 1):
                    formatted_result = self.format_result(url, dork, i)
                    formatted_results.append(formatted_result)
                    self.print_result_info(formatted_result)
                
                self.save_results(formatted_results, output_file)
                print(f"\033[1;32m[+] Saved {len(formatted_results)} results to {output_file}\033[0m")
            else:
                print("\033[1;33m[!] No results found for this dork\033[0m")
                
        except Exception as e:
            print(f"\033[1;31m[!] Error processing dork: {str(e)}\033[0m")

    def format_result(self, url, dork, index):
        """Format the search result with additional information"""
        parsed_url = urlparse(url)
        
        return {
            'dork': dork,
            'url': url,
            'domain': parsed_url.netloc,
            'path': parsed_url.path,
            'query': parsed_url.query,
            'rank': index,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

    def print_result_info(self, result):
        """Print information about a search result"""
        print(f"\033[1;34m[{result['rank']}] {result['domain']} - {result['url'][:80]}...\033[0m")

    def save_results(self, results, filename):
        """Save results to file in JSON format"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        mode = 'a' if os.path.exists(filename) else 'w'
        with open(filename, mode, encoding='utf-8') as f:
            for result in results:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')

    def validate_dork(self, dork):
        """Basic dork validation"""
        if not dork or len(dork.strip()) < 3:
            return False
        return True

# ===== MAIN FUNCTION =====
def main():
    parser = argparse.ArgumentParser(description='Google Dorking Tool')
    parser.add_argument('-d', '--dork', help='Google dork query')
    parser.add_argument('-f', '--file', help='File containing multiple dorks (one per line)')
    parser.add_argument('-o', '--output', default=RESULTS_FILE, help='Output file path')
    parser.add_argument('-m', '--max-results', type=int, default=MAX_RESULTS, help='Maximum results per dork')
    parser.add_argument('--delay', type=float, default=DELAY, help='Delay between requests')
    
    args = parser.parse_args()
    show_banner()
    
    if not args.dork and not args.file:
        print("\033[1;31m[!] Please provide either a dork (-d) or a file with dorks (-f)\033[0m")
        return
    
    # Initialize Google dorker
    dorker = GoogleDorker()
    
    # Collect dorks
    dorks = []
    if args.dork:
        if dorker.validate_dork(args.dork):
            dorks.append(args.dork)
        else:
            print("\033[1;31m[!] Invalid dork query\033[0m")
            return
    
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                dorks.extend([line.strip() for line in f if line.strip() and not line.startswith('#')])
        except Exception as e:
            print(f"\033[1;31m[!] Error reading file: {str(e)}\033[0m")
            return
    
    print(f"\033[1;33m[+] Loaded {len(dorks)} dork queries\033[0m")
    print(f"\033[1;33m[+] Maximum results per dork: {args.max_results}\033[0m")
    
    # Process dorks
    for dork in dorks:
        dorker.process_dork(dork, args.max_results, args.output)
        if len(dorks) > 1:
            time.sleep(args.delay * 2)  # Longer delay between different dorks

# ===== INSTALLATION INSTRUCTIONS =====
def show_installation():
    print("""
\033[1;32m=== Installation Instructions ===\033[0m

1. Install required packages:
   pip install requests beautifulsoup4

2. Run the tool:
   python3 google_dorker.py -d 'site:github.com password'

3. For multiple dorks, create a file:
   echo 'site:github.com password' > dorks.txt
   echo 'filetype:pdf confidential' >> dorks.txt
   python3 google_dorker.py -f dorks.txt
""")

if __name__ == '__main__':
    # Show installation instructions if no arguments
    if len(os.sys.argv) == 1:
        show_banner()
        show_installation()
    else:
        main()
