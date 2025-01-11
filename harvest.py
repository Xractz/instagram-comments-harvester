import os
import re
import csv
import time
from datetime import datetime
import argparse

import requests
from dotenv import load_dotenv, set_key

SUCCESS = '\033[92m'
ERROR = '\033[91m'
WARNING = '\033[93m'
INFO = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

class Harvest:
  def __init__(self):
    self.session_id = None
    self.url = None
    self.api_url = "https://www.instagram.com/api/v1"
    self.total_comments = 0
    self.username = None
    self.media_id = None
    self.limit = 100

  def set_session_id(self, session_id):
    self.session_id = session_id

  def set_url(self, url):
    if not re.match(r'https?://(?:www\.)?instagram\.com/p/[\w-]+/?', url):
        raise ValueError(f"{ERROR}⚠️ Invalid Instagram post URL format{RESET}")
    self.url = url
  
  def set_limit(self, limit):
    if not isinstance(limit, int) or limit < 1:
      raise ValueError(f"{ERROR}⚠️ Limit must be a positive number{RESET}")
    self.limit = limit

  def fetch_url(self, url, params=None):
    headers = {
      "accept": "application/json, text/plain, */*",
      "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 250.0.0.17.109 (iPhone14,5; iOS 16_0; en_US; en-US; scale=3.00; 1170x2532; 165586599)"
    }
    cookies = {"sessionid": self.session_id}
    
    try:
      response = requests.get(url, headers=headers, cookies=cookies, params=params, allow_redirects=True)
      return response
    except requests.RequestException as e:
      print(f"{ERROR}🚫 Error while fetching data: {e}{RESET}")
      return None

  def is_session_id_valid(self):
    if not self.session_id or not isinstance(self.session_id, str):
        print(f"{ERROR}⚠️ Invalid session ID format{RESET}")
        return False

    url = f"{self.api_url}/accounts/current_user/"
    response = self.fetch_url(url)

    if response is None:
      print(f"{ERROR}❌ Failed to fetch data. Please check your session ID.{RESET}")
      return False

    if response.status_code == 200:
      print(f"{SUCCESS}✅ Session ID is valid.{RESET}")
      return True
    elif response.status_code == 403:
      print(f"{ERROR}🚫 Access forbidden. Session ID is invalid or restricted.{RESET}")
      return False
    elif response.status_code == 429:
      print(f"{WARNING}⏳ Too many requests. Instagram has rate-limited this session ID.{RESET}")
      return False
    else:
      print(f"{ERROR}❌ Session ID is invalid. Status code: {response.status_code}{RESET}")
      return False

  def extract_media_id(self, url):
    try:
      response = self.fetch_url(url)
      return re.search(r'"media_id":"(\d+)"', response.text).group(1)
    except AttributeError:
      print(f"{ERROR}❌ Error: Media ID not found.{RESET}")
      return None
  
  def fetch_all_comments(self, url):
    if self.media_id is None:
      self.media_id = self.extract_media_id(url)
    
    post_id = re.search(r'/p/([^/]+)/', url).group(1)
    url = f"{self.api_url}/media/{self.media_id}/comments/"
    has_more = True
    min_id = None
    next_max_id = None
    page = 1
    
    try:
      initial_response = self.fetch_url(url)
      data = initial_response.json()
      self.username = data.get("caption", {}).get("user", {}).get("username", "unknown")
      self.total_comments = data.get("comment_count", 0)
    except:
      self.username = "unknown"
    
    if self.limit > self.total_comments:
      self.limit = self.total_comments
      print(f"{INFO}📊 Total comments available: {self.total_comments} with replies{RESET}")
    
    os.makedirs("results/", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"results/{self.username}_{post_id}_comments_{timestamp}.csv"
    
    fieldnames = ['comment_id', 'media_id', 'username', 'full_name', 'comment_text', 'created_at', 'likes_count']
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
      writer = csv.DictWriter(f, fieldnames=fieldnames)
      writer.writeheader()
    
    total_comments = 0
    
    print(f"{INFO}🔄 Starting comment collection...{RESET}")
    
    while has_more and total_comments < self.limit:
      params = {
        "can_support_threading": "true",
        "permalink_enabled": "false"
      }
      
      if min_id:
        params["min_id"] = min_id
      if next_max_id:
        params["max_id"] = next_max_id
      
      response = self.fetch_url(url, params)

      if response is None:
        print(f"{ERROR}❌ Failed to fetch comments.{RESET}")
        break

      data = response.json()
      comments = data.get("comments", [])
      
      with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        for comment in comments:
          comment_data = {
            'comment_id': comment.get('pk', ''),
            'media_id': self.media_id,
            'username': comment.get('user', {}).get('username', ''),
            'full_name': comment.get('user', {}).get('full_name', ''),
            'comment_text': comment.get('text', ''),
            'created_at': comment.get('created_at_utc', ''),
            'likes_count': comment.get('comment_like_count', 0),
          }
          writer.writerow(comment_data)
          total_comments += 1
          
          print(f"{INFO}📝 Page: {page}, Comments: {total_comments}/{self.limit}{RESET}            ", end="\r")
          time.sleep(0.1)
      
          if total_comments >= self.limit:
            break

      if total_comments >= self.limit:
        print(f"\n{SUCCESS}✅ Reached comment limit of {self.limit}{RESET}")
        break

      has_more = (
        data.get("has_more_headload_comments", False) or 
        data.get("has_more_comments", False) or
        data.get("next_max_id") is not None
      )
      
      min_id = data.get("next_min_id")
      next_max_id = data.get("next_max_id")
      
      page += 1
      delay = 5 # Delay 5 second for rate limiting
      for i in range(delay * 10):
        remaining = delay - (i * 0.1)
        print(f"{WARNING}⏳ Fetching next page in {remaining:.1f}s            {RESET}", end="\r")
        time.sleep(0.1)

    print(f"\n{SUCCESS}💾 Data saved to {filename}{RESET}")
    print(f"{SUCCESS}📊 Total comments collected: {total_comments}{RESET}")

def main():
  parser = argparse.ArgumentParser(
    description=f'{BOLD}Instagram Comments Harvester - Scrape comments from Instagram posts{RESET}',
    formatter_class=argparse.RawTextHelpFormatter
  )
  
  parser.add_argument('-u', '--url', 
    help='Instagram post URL to scrape comments from'
  )
  
  parser.add_argument('-l', '--limit',
    help='Maximum number of comments to collect (default: 100)',
    type=int,
    default=100
  )
  
  parser.add_argument('-s', '--sessionid',
    help='Instagram session ID (will be saved to .env file for future use)',
    type=str
  )
  
  examples = f'''
{BOLD}Examples:{RESET}
  # First time setup - Save session ID to .env file:
  python script.py -s "your_session_id_here"
  
  # After setting up session ID, you can scrape comments:
  python script.py -u https://www.instagram.com/p/XXXX           # Scrape 100 comments (default)
  python script.py -u https://www.instagram.com/p/XXXX -l 500   # Scrape 500 comments
  
  # Or use a different session ID without saving to .env:
  python script.py -u https://www.instagram.com/p/XXXX -s "another_session_id" -l 500

{BOLD}File Naming Format:{RESET}
  The output file will be saved in the 'results' folder with the following format:
  {INFO}[username]{RESET}_{WARNING}[post_id]{RESET}_comments_{SUCCESS}[timestamp]{RESET}.csv
  
  Example:
  results/{INFO}johndoe{RESET}_{WARNING}Cw9Xtz{RESET}_comments_{SUCCESS}20240110_153022{RESET}.csv{RESET}
  └─ {INFO}username{RESET}: Instagram username of the post owner
  └─ {WARNING}post_id{RESET}: Unique identifier from the post URL
  └─ {SUCCESS}timestamp{RESET}: Date and time of scraping (YYYYMMDD_HHMMSS)
  
{BOLD}Note:{RESET}
  - You must either set up session ID first using -s flag or provide it with each command
  - Session ID is required for authentication with Instagram
  - When using -s, the session ID will be saved to .env file for future use
  - All scraped data will be automatically saved in the {INFO}'results'{RESET} folder
  '''
  
  parser.epilog = examples
  args = parser.parse_args()

  if args.sessionid:
    if not os.path.exists('.env'):
      with open('.env', 'w') as f:
        pass
    
    set_key('.env', 'session_id', args.sessionid)
    print(f"{SUCCESS}✅ Session ID has been saved to .env file{RESET}")
    
    if not args.url:
      return
  
  if not args.url:
    parser.print_help()
    return
    
  if not args.sessionid:
    load_dotenv()
    session_id = os.getenv('session_id')
    if not session_id:
      print(f"{ERROR}❌ Error: Session ID not found. Please set it first using -s flag.{RESET}")
      print(f"{INFO}💡 Example: python script.py -s 'your_session_id_here'{RESET}")
      return
  else:
    session_id = args.sessionid

  harvest = Harvest()
  harvest.set_session_id(session_id)
  harvest.set_limit(args.limit)

  if not harvest.is_session_id_valid():
    print(f"{ERROR}❌ Session ID is invalid. Please update the session_id in your .env file.{RESET}")
    return

  try:
    print(f"\n{INFO}🔍 Scraping comments from: {args.url}{RESET}")
    print(f"{INFO}❓ This tool will fetch comments from an Instagram post {BOLD}without{RESET} {INFO}replies comments.{RESET}")
    print(f"{INFO}⏳ This might take a while depending on the number of comments...{RESET}")
    harvest.fetch_all_comments(args.url)
    print(f"\n{SUCCESS}🎉 Scraping completed successfully!{RESET}")
          
  except Exception as e:
    print(f"\n{ERROR}❌ An error occurred: {str(e)}{RESET}")
    print(f"{WARNING}⚠️  Please try again or check your URL/session ID.{RESET}")

if __name__ == "__main__":
  main()