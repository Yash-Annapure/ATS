import os
import asyncio
import aiohttp
import pandas as pd
import time
from dotenv import load_dotenv, find_dotenv

# Load environment variables (API Token)
load_dotenv(find_dotenv())

# Configuration
BASE_URL = "https://leetcode.com/graphql"
TOTAL_USERS_REQUIRED = 3000
CONCURRENCY_LIMIT = 3
MAX_RANK = int(os.environ.get('MAX_LEETCODE_RANK', 1000000))
print(f"ℹ Using MAX_LEETCODE_RANK: {MAX_RANK}")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Content-Type": "application/json",
    "Referer": "https://leetcode.com/"
}

# GraphQL Queries
RANKING_QUERY = """
query globalRanking($page: Int) {
  globalRanking(page: $page) {
    rankingNodes {
      currentRating
      currentGlobalRanking
      dataRegion
      user {
        username
        profile {
          userSlug
        }
      }
    }
  }
}
"""

USER_PROFILE_QUERY = """
query getUserProfile($username: String!) {
  matchedUser(username: $username) {
    username
    profile {
      ranking
      reputation
      userAvatar
    }
    submitStats {
      acSubmissionNum {
        difficulty
        count
      }
    }
  }
}
"""

async def fetch_ranking_page(session, page):
    """Fetch one page of rankings"""
    payload = {
        "query": RANKING_QUERY,
        "variables": {"page": page}
    }

    try:
        async with session.post(BASE_URL, json=payload, headers=HEADERS) as resp:
            if resp.status == 200:
                data = await resp.json()
                nodes = data.get('data', {}).get('globalRanking', {}).get('rankingNodes', [])
                usernames = [node['user']['username'] for node in nodes if node.get('user')]
                return usernames
            else:
                print(f"Error fetching page {page}: Status {resp.status}")
                return []
    except Exception as e:
        print(f"Exception on page {page}: {e}")
        return []

async def fetch_user_profile(session, username, semaphore):
    """Fetch detailed profile for a user"""
    async with semaphore:
        payload = {
            "query": USER_PROFILE_QUERY,
            "variables": {"username": username}
        }

        try:
            async with session.post(BASE_URL, json=payload, headers=HEADERS) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    user = data.get('data', {}).get('matchedUser')

                    if not user:
                        return None

                    stats = user.get('submitStats', {}).get('acSubmissionNum', [])

                    ranking = user.get('profile', {}).get('ranking', 0)
                    
                    # Filtering Logic
                    if ranking > MAX_RANK:
                        return None

                    if len(stats) < 4:
                        return None

                    return {
                        "Username": user['username'],
                        "Ranking": ranking,
                        "Reputation": user.get('profile', {}).get('reputation', 0),
                        "All_Solved": stats[0]['count'],
                        "Easy_Solved": stats[1]['count'],
                        "Medium_Solved": stats[2]['count'],
                        "Hard_Solved": stats[3]['count']
                    }
                else:
                    return None
        except Exception as e:
            return None

        await asyncio.sleep(0.1)

async def main():
    print("="*60)
    print("LEETCODE DATA FETCHER")
    print("="*60)

    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

    async with aiohttp.ClientSession() as session:
        # Step 1: Collect usernames
        print(f"\nStep 1: Collecting {TOTAL_USERS_REQUIRED} usernames...")
        usernames = []
        page = 1

        while len(usernames) < TOTAL_USERS_REQUIRED:
            batch = await fetch_ranking_page(session, page)

            if not batch:
                print(f"\nNo data from page {page}, waiting 2 seconds...")
                await asyncio.sleep(2)
                batch = await fetch_ranking_page(session, page)

                if not batch:
                    print(f"Still no data, stopping at {len(usernames)} users")
                    break

            usernames.extend(batch)
            print(f"Collected {len(usernames)} usernames (page {page})", end="\r")

            page += 1
            await asyncio.sleep(0.5)

        usernames = usernames[:TOTAL_USERS_REQUIRED]
        print(f"\nCollected {len(usernames)} usernames")

        # Step 2: Fetch profiles
        print(f"\nStep 2: Fetching profiles for {len(usernames)} users...")

        tasks = [fetch_user_profile(session, username, semaphore) for username in usernames]

        results = []
        completed = 0

        for coro in asyncio.as_completed(tasks):
            user_data = await coro
            if user_data:
                results.append(user_data)

            completed += 1
            if completed % 25 == 0:
                print(f"Fetched {completed}/{len(usernames)} profiles ({len(results)} valid)", end="\r")

        print(f"\nFetched {len(results)} valid profiles")

        # Step 3: Save to file
        if results:
            df = pd.DataFrame(results)
            output_file = "leetcode_profiles.csv"
            df.to_csv(output_file, index=False)
            print(f"\nSaved {len(results)} profiles to {output_file}")
            print("\nSample data:")
            print(df.head())
        else:
            print("\nNo data collected!")

if __name__ == "__main__":
    asyncio.run(main())