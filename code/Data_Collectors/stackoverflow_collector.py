import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv, find_dotenv

# Load environment variables (API Token)
load_dotenv(find_dotenv())

class StackOverflowCollector:
    """Collects top StackOverflow users and enriches them with contribution stats."""
    
    def __init__(self, output_dir="../Profile_Data"):
        self.api = "https://api.stackexchange.com/2.3"
        self.out = output_dir
        if not os.path.exists(self.out): os.makedirs(self.out)

    def _fetch(self, endpoint, params={}):
        """Generic fetch with robust 429 rate-limit handling."""
        params = {**params, "site": "stackoverflow"}
        for attempt in range(3):
            try:
                resp = requests.get(f"{self.api}/{endpoint}", params=params)
                
                # Handle Rate Limits (Backoff)
                if resp.status_code == 429:
                    wait = int(resp.headers.get("Retry-After", 20)) + (attempt * 10)
                    print(f"  [429] Rate limited. Waiting {wait}s...")
                    time.sleep(wait)
                    continue
                
                # Handle Backoff instruction in successful response
                data = resp.json()
                if 'backoff' in data:
                    time.sleep(data['backoff'])
                
                if resp.status_code == 200:
                    return data.get('items', [])
                
                print(f"  [Error] {resp.status_code}: {resp.text[:100]}")
                break
            except Exception as e:
                print(f"  [Exception] {e}")
                time.sleep(1)
        return []

    def get_top_users(self, pages=2):
        """Fetch top users by reputation."""
        print(f"Fetching top users ({pages} pages)...")
        
        min_rep = int(os.environ.get('MIN_STACKOVERFLOW_REPUTATION', 0))
        print(f"ℹ Using MIN_STACKOVERFLOW_REPUTATION: {min_rep}")

        users = []
        for p in range(1, pages + 1):
            # API supports 'min' parameter for reputation sort
            params = {
                "page": p, 
                "pagesize": 100, 
                "order": "desc", 
                "sort": "reputation",
                "min": min_rep
            }
            batch = self._fetch("users", params)
            if not batch: break
            users.extend(batch)
            print(f"  Page {p}: Found {len(batch)} users")
            time.sleep(0.5)
        return users

    def enrich_and_save(self, users):
        """Fetch Q/A stats for users and save to CSV."""
        if not users: return print("No users to enrich.")
        
        print(f"Enriching {len(users)} profiles...")
        rows = []
        
        for i, u in enumerate(users):
            uid = u['user_id']
            # Fetch minimal counts (pagesize=1 reduces load, we just need the count metadata usually)
            # Actually SE API response wrapper often has 'total', but 'items' count is safer for page-limited views
            # To be robust but not spammy:
            qs = self._fetch(f"users/{uid}/questions", {"pagesize": 5, "order":"desc", "sort":"creation"})
            as_ = self._fetch(f"users/{uid}/answers",   {"pagesize": 5, "order":"desc", "sort":"creation"})
            
            rows.append({
                'User_ID': uid,
                'Display_Name': u['display_name'],
                'Account_Id': u.get('account_id'),
                'Reputation': u.get('reputation', 0),
                'Gold_Badges': u.get('badge_counts', {}).get('gold', 0),
                'Silver_Badges': u.get('badge_counts', {}).get('silver', 0),
                'Bronze_Badges': u.get('badge_counts', {}).get('bronze', 0),
                'Location': u.get('location', ''),
                'Website_URL': u.get('website_url', ''),
                'Link': u.get('link', ''),
                'Questions_Count': len(qs), 
                'Answers_Count': len(as_),
                'Total_Question_Views': sum(q.get('view_count', 0) for q in qs)
            })
            if i % 10 == 0: print(f"  Processed {i+1}/{len(users)}")
            time.sleep(0.5) # Safe delay

        path = f"{self.out}/StackOverflow-20K-Formatted.csv"
        pd.DataFrame(rows).to_csv(path, index=False)
        print(f"Done! Saved {len(rows)} profiles to {path}")

    def run(self):
        users = self.get_top_users(pages=10) # 1 page equals 100 results
        self.enrich_and_save(users)

if __name__ == "__main__":
    StackOverflowCollector().run()
