import json
import os
import time
from pathlib import Path
from google_play_scraper import Sort, reviews

# Correct Google Play package names
apps = {
    "cbe": "com.combanketh.mobilebanking",
    "boa": "com.boa.boaMobileBanking",
    "dashen": "com.dashen.dashensuperapp"
}

def scrape_reviews(app_name, app_package, total_reviews=500):
    all_reviews = []
    token = None
    last_count = 0  # Track previous review count

    print(f"📲 Scraping {total_reviews} reviews for {app_name.upper()}...")

    while len(all_reviews) < total_reviews:
        print(f"⏳ Fetched {len(all_reviews)} so far...")

        batch, token = reviews(
            app_package,
            lang="en",
            country="et",  # Ethiopia
            sort=Sort.NEWEST,
            count=200,
            continuation_token=token
        )

        for review in batch:
            if isinstance(review.get("at"), (str, type(None))):
                review["at"] = review.get("at")
            else:
                review["at"] = review.get("at").strftime("%Y-%m-%d")

        all_reviews.extend(batch)

        # Break if no new reviews are being added (loop or limit hit)
        if len(all_reviews) == last_count or not batch:
            print("No new reviews fetched. Ending early.")
            break

        last_count = len(all_reviews)

        # Break if there's no continuation token (last page)
        if not token:
            print("Reached last page.")
            break

        time.sleep(1.5)  #Pause to avoid rate-limiting

    # Trim and save
    all_reviews = all_reviews[:total_reviews]
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    out_path = os.path.join("data/raw", f"{app_name}_reviews.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_reviews, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(all_reviews)} reviews to {out_path}")

#Run only Dashen for now, or uncomment others as needed
if __name__ == "__main__":
    # scrape_reviews("cbe", apps["cbe"])
    # scrape_reviews("boa", apps["boa"])
    scrape_reviews("dashen", apps["dashen"])
