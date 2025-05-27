import os
import requests
from nba_api.stats.static import teams

output_dir = "api/static/images"
os.makedirs(output_dir, exist_ok=True)

for team in teams.get_teams():
    abbr = team['abbreviation'].lower()
    team_id = team['id']
    # NBA CDN PNG logo
    url = f"https://cdn.nba.com/logos/nba/{team_id}/primary/L/logo.png"
    out_path = os.path.join(output_dir, f"{abbr}.png")
    try:
        r = requests.get(url)
        if r.status_code == 200:
            with open(out_path, "wb") as f:
                f.write(r.content)
            print(f"Downloaded {abbr}.png")
        else:
            print(f"Failed to download {abbr}: {r.status_code}")
    except Exception as e:
        print(f"Error downloading {abbr}: {e}") 