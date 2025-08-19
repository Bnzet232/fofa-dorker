#!/usr/bin/env python3
# Google Dorking Tool
# Created by: bnzet

import requests
from googlesearch import search
import argparse
import time
import random
import json
import os
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

# ===== CONFIG =====
MAX_RESULTS = 100
DELAY = 2  # Delay between requests to avoid blocking
TIMEOUT = 15
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
]
RESULTS_FILE = "google_dork_results.txt"

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

    def google_search(self, dork, num_results=MAX_RESULTS, lang="en", country="us"):
        """Perform Google search using the dork"""
        try:
            print(f"\033[1;33m[+] Searching for: {dork}\033[0m")
            
            # Perform the search
            search_results = list(search(
                dork,
                num_results=num_results,
                lang=lang,
                country=country,
                user_agent=self.get_random_user_agent(),
                timeout=TIMEOUT
            ))
            
            return search_results
            
        except Exception as e:
            print(f"\033[1;31m[!] Search error: {str(e)}\033[0m")
            return []

    def process_dork(self, dork, max_results=MAX_RESULTS, output_file=RESULTS_FILE):
        """Process a single dork query"""
        print(f"\n\033[1;36m[+] Processing dork: {dork}\033[0m")
        
        try:
            results = self.google_search(dork, num_results=max_results)
            
            if not results:
                print("\033[1;33m[!] No results found\033[0m")
                return
            
            formatted_results = []
            for i, url in enumerate(results, 1):
                formatted_result = self.format_result(url, dork, i)
                formatted_results.append(formatted_result)
                
                # Print result info
                self.print_result_info(formatted_result)
                
                # Add delay between processing results
                if i < len(results):
                    time.sleep(random.uniform(0.5, 1.5))
            
            # Save results
            if formatted_results:
                self.save_results(formatted_results, output_file)
                print(f"\033[1;32m[+] Saved {len(formatted_results)} results to {output_file}\033[0m")
            else:
                print("\033[1;33m[!] No valid results to save\033[0m")
                
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
    parser.add_argument('-t', '--threads', type=int, default=1, help='Number of threads (use cautiously)')
    parser.add_argument('--lang', default='en', help='Search language (e.g., en, id, es)')
    parser.add_argument('--country', default='us', help='Search country (e.g., us, id, uk)')
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
    if len(dorks) == 1:
        dorker.process_dork(dorks[0], args.max_results, args.output)
    else:
        print(f"\033[1;33m[+] Processing {len(dorks)} dorks with {args.threads} threads\033[0m")
        
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            for dork in dorks:
                executor.submit(dorker.process_dork, dork, args.max_results, args.output)
                time.sleep(args.delay)  # Stagger requests

# ===== EXAMPLE DORK FILE CONTENT =====
def create_example_dork_file():
    example_content = """# Google Dorks Examples
# File: dorks.txt
# Usage: python3 google_dorker.py -f dorks.txt

# Basic dorks
site:github.com password
filetype:pdf confidential
intitle:"index of" "parent directory"

# Login pages
inurl:login.php
inurl:admin intitle:login
inurl:wp-admin

# Sensitive files
filetype:sql "INSERT INTO" password
filetype:env DB_PASSWORD
filetype:log "error" "password"

# Vulnerable systems
inurl:phpmyadmin intitle:phpmyadmin
inurl:shell.php?cmd=
inurl:config.php.bak

# Specific technologies
inurl:wordpress wp-content
inurl:joomla component
inurl:drupal intext:"Powered by"
"""
    
    with open('example_dorks.txt', 'w', encoding='utf-8') as f:
        f.write(example_content)
    print("\033[1;32m[+] Created example_dorks.txt with sample dorks\033[0m")

if __name__ == '__main__':
    # Uncomment the next line to create an example dork file
    # create_example_dork_file()
    
    main()
