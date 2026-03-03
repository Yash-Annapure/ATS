import asyncio
import aiohttp
import pandas as pd
import os
import random
from collections import defaultdict
from dotenv import load_dotenv, find_dotenv

# Load environment variables (API Token)
load_dotenv(find_dotenv())

# Configuration
TARGET_COUNT = 1000  # Number of profiles to collect

class GitHubCollector:
    """
    Async GitHub User Collector.
    Fetches user profiles and their repository statistics concurrently.
    """
    def __init__(self, target_count=TARGET_COUNT, output_file="../Profile_Data/Github_Profiles.csv"):
        self.target_count = target_count
        self.output_file = output_file
        self.token = os.environ.get('GITHUB_TOKEN')
        self.api_url = "https://api.github.com"
        
        if self.token:
            print("GITHUB_TOKEN loaded successfully.")
        else:
            print("Warning: No GITHUB_TOKEN found. Rate limits will be strict (60/hour).")

    async def _get(self, session, endpoint, params=None):
        """
        Helper method to perform async GET requests.
        Handles headers and basic error reporting.
        """
        headers = {"Authorization": f"token {self.token}"} if self.token else {}
        try:
            async with session.get(f"{self.api_url}/{endpoint}", params=params, headers=headers) as resp:
                if resp.status == 200:
                    return await resp.json()
                elif resp.status == 403:
                    # Rate limit hit or forbidden
                    print(f" Rate limit or Forbidden (403) on {endpoint}")
                else:
                    print(f" Request to {endpoint} failed: {resp.status}")
        except Exception as e:
            print(f" Error requesting {endpoint}: {e}")
        return None

    async def get_users(self, session):
        """
        Fetches a list of unique usernames using the GitHub Search API.
        Iterates through pages of results to gather enough users.
        """
        print(f"Finding {self.target_count} users to fetch via API...")
        users = set()
        
        # Diverse queries to ensure we find enough users
        # Dynamic query based on environment variables
        min_followers = os.environ.get('MIN_GITHUB_FOLLOWERS', '50')
        print(f"ℹ Using MIN_GITHUB_FOLLOWERS: {min_followers}")
        
        queries = [
            f"followers:>{min_followers} sort:joined-desc", 
            f"followers:{min_followers}..10000 language:javascript",
            f"followers:{min_followers}..10000 language:python",
            f"followers:{min_followers}..10000 language:java",
            f"followers:{min_followers}..10000 language:rust",
            f"followers:{min_followers}..10000 language:go",
            f"followers:{min_followers}..10000 language:cpp",
            f"followers:>{min_followers} location:Remote",
            f"followers:>{min_followers} location:USA",
            f"followers:>{min_followers} location:India",
            f"followers:>{min_followers} location:Europe",
        ]
        random.shuffle(queries)
        
        query_idx = 0
        while len(users) < self.target_count and query_idx < len(queries):
            query = queries[query_idx]
            print(f" Searching for: '{query}'")
            
            # GitHub Search API allows up to 1000 results (10 pages of 100)
            for page in range(1, 11): 
                if len(users) >= self.target_count:
                    break
                
                print(f"    - Fetching page {page}...")
                params = {"q": query, "per_page": 100, "page": page}
                data = await self._get(session, "search/users", params)
                
                if not data or 'items' not in data:
                    break # Stop if no data or error
                
                items = data.get('items', [])
                if not items:
                    break # Stop if page is empty
                    
                initial_count = len(users)
                for item in items:
                    users.add(item['login'])
                
                new_added = len(users) - initial_count
                print(f"      + Found {new_added} new users (Total: {len(users)})")
                
                await asyncio.sleep(1) # Be nice to the API
                
            query_idx += 1

        print(f"Found total {len(users)} unique users.")
        return list(users)[:self.target_count]

    async def process_user(self, session, user):
        """
        Fetches detailed profile and repository stats for a single user.
        """
        # 1. Fetch Profile Data
        profile = await self._get(session, f"users/{user}")
        if not profile: 
            return None

        # 2. Fetch Repository Stats
        stats = {
            "stars": 0, 
            "forks": 0, 
            "langs": defaultdict(int), 
            "topics": []
        }
        
        # We fetch up to 100 recently pushed repos
        repos = await self._get(session, f"users/{user}/repos", {"per_page": 100, "sort": "pushed"}) or []

        for r in repos:
            stats["stars"] += r.get('stargazers_count', 0)
            stats["forks"] += r.get('forks_count', 0)
            
            if (lang := r.get('language')): 
                stats["langs"][lang] += 1
            
            stats["topics"].extend(r.get('topics', []))

        # 3. Aggregate Stats
        # Get top 5 languages by frequency
        top_langs = sorted(stats["langs"].items(), key=lambda x: x[1], reverse=True)[:5]
        top_langs_str = "; ".join([l[0] for l in top_langs])
        
        # Get unique topics
        common_topics = list(set(stats["topics"]))[:10]
        common_topics_str = "; ".join(common_topics)

        # 4. Return Combined Data (Bio/URL/Twitter removed as requested)
        return {
            "username": profile.get("login"),
            "name": profile.get("name"),
            "email": profile.get("email"),
            "location": profile.get("location"),
            "public_repos": profile.get("public_repos"),
            "followers": profile.get("followers"),
            "following": profile.get("following"),
            "total_stars": stats["stars"],
            "total_forks": stats["forks"],
            "top_languages": top_langs_str,
            "common_topics": common_topics_str
        }

    async def collect_async(self):
        """
        Main orchestration coroutine.
        1. Creates a session.
        2. Gets list of users.
        3. Processes users concurrently.
        4. Saves data to CSV.
        """
        async with aiohttp.ClientSession() as session:
            # Step 1: Find users
            usernames = await self.get_users(session)
            
            if not usernames:
                print(" No users found. Exiting.")
                return

            print(f"\n Collecting full details for {len(usernames)} users...")
            
            # Step 2: Create tasks for concurrent execution
            # We limit concurrency preventing overwhelming the client/server
            # (Though simple gather is often fine for batch jobs of this size)
            tasks = [self.process_user(session, user) for user in usernames]
            
            # Track progress roughly
            results = []
            total = len(tasks)
            # Use chunks or simple gather. gather is fastest but all-or-nothing for memory.
            # We will use gather for simplicity as 1000 tasks is manageable.
            
            gathered_results = await asyncio.gather(*tasks)
            results = [r for r in gathered_results if r]

        # Step 3: Save results
        if results:
            os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
            df = pd.DataFrame(results)
            
            # Save to CSV
            df.to_csv(self.output_file, index=False, encoding='utf-8-sig')
            
            print(f"\n SUCCESS! Saved {len(df)} profiles to {self.output_file}")
            print("\n Sample Data Preview:")
            print(df[["username", "name", "total_stars", "top_languages"]].head().to_string())
        else:
            print(" Failed to collect any profile data.")

    def collect(self):
        """
        Synchronous entry point.
        Sets up the event loop policy for Windows if needed.
        """
        if os.name == 'nt':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(self.collect_async())

if __name__ == "__main__":
    # Create the collector and run
    collector = GitHubCollector(target_count=TARGET_COUNT)
    collector.collect()
