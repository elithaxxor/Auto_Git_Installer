import requests
from bs4 import BeautifulSoup
import subprocess
import os
import concurrent.futures
import time
from urllib.parse import urlparse
import re

url = "https://inventory.raw.pm/tools.html"

def fetch_webpage(url):
    try:
        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Failed to fetch the webpage: {e}")
        return None

def parse_html_for_github_links(html_content):
    """Extract GitHub links directly with regex for better performance"""
    github_pattern = re.compile(r'href=[\'"]?(https?://github\.com/[^\'" >]+)[\'"]?')
    return github_pattern.findall(html_content)

def normalize_github_link(link):
    """Normalize GitHub link ensuring it ends with .git and is a valid repository"""
    # Parse the URL
    parsed_url = urlparse(link)
    path_parts = parsed_url.path.strip('/').split('/')
    
    # Ensure it's a repository link (has at least username/repo format)
    if len(path_parts) >= 2:
        # Extract username and repo name
        username = path_parts[0]
        repo_name = path_parts[1]
        
        # Remove any trailing parts like /blob/master, etc.
        normalized_link = f"https://github.com/{username}/{repo_name}"
        
        # Add .git if it doesn't end with it
        if not normalized_link.endswith('.git'):
            normalized_link += '.git'
            
        return normalized_link
    
    return None  # Not a valid repo link

def clone_repository(link, repo_dir):
    """Clone a single repository"""
    repo_name = link.split('/')[-1].replace('.git', '')
    target_dir = os.path.join(repo_dir, repo_name)
    
    # Skip if already exists
    if os.path.exists(target_dir):
        print(f"Repository {repo_name} already exists, skipping")
        return True
    
    try:
        # Use depth=1 for shallow clone (faster)
        result = subprocess.run(
            ['git', 'clone', '--depth=1', link, target_dir],
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            timeout=120  # Set timeout to avoid hanging
        )
        
        if result.returncode == 0:
            print(f"Successfully cloned {link}")
            return True
        else:
            error = result.stderr.decode('utf-8', errors='replace')
            print(f"Failed to clone {link}: {error}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"Timeout while cloning {link}")
        return False
    except Exception as e:
        print(f"Error cloning {link}: {e}")
        return False

def clone_repositories_parallel(links, repo_dir, max_workers=10):
    """Clone repositories in parallel using ThreadPoolExecutor"""
    os.makedirs(repo_dir, exist_ok=True)
    print(f"Starting to clone {len(links)} GitHub repositories into '{repo_dir}/'...")
    
    successful = 0
    failed = 0
    
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all clone tasks
        future_to_link = {executor.submit(clone_repository, link, repo_dir): link for link in links}
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_link):
            link = future_to_link[future]
            try:
                if future.result():
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"Exception for {link}: {e}")
                failed += 1
    
    elapsed = time.time() - start_time
    print(f"Cloning completed in {elapsed:.2f} seconds")
    print(f"Successfully cloned: {successful}, Failed: {failed}")

def save_links_to_file(links, filename):
    with open(filename, 'w') as file:
        for link in links:
            file.write(link + '\n')
    print(f"Saved {len(links)} links to {filename}")

def main():
    print("Downloading offensive security tools from inventory.raw.pm")
    start_time = time.time()
    
    # Step 1: Fetch and parse the webpage
    html_content = fetch_webpage(url)
    if not html_content:
        print("No HTML content found")
        return
    
    # Step 2: Extract and process GitHub links
    github_links = parse_html_for_github_links(html_content)
    if not github_links:
        print("Warning: No GitHub links found on the page.")
        return
    
    # Step 3: Normalize links
    normalized_links = []
    for link in github_links:
        normalized = normalize_github_link(link)
        if normalized and normalized not in normalized_links:
            normalized_links.append(normalized)
    
    print(f"Found {len(normalized_links)} unique GitHub repositories")
    
    # Step 4: Save to file
    save_links_to_file(normalized_links, 'github_links.txt')
    
    # Step 5: Clone repositories in parallel
    clone_repositories_parallel(normalized_links, 'repos')
    
    total_time = time.time() - start_time
    print(f"Total execution time: {total_time:.2f} seconds")

if __name__ == "__main__":
    main()
