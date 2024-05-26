import requests
from dotenv import load_dotenv
import os

from db import EdgeDB

load_dotenv()
if not os.getenv("GH_REPO") or not os.getenv("GH_TOKEN"):
    raise Exception("Please set GH_REPO and GH_TOKEN in .env file")
GH_REPO = os.getenv("GH_REPO")
GH_TOKEN = os.getenv("GH_TOKEN")

def get_sponsors():
    headers = {"Authorization": f"token {GH_TOKEN}"}
    query = """
        query SponsorQuery {
            viewer {
                sponsors(first: 100) {
                    edges {
                        node {
                            ... on User {
                                id
                                name
                                url
                                avatarUrl
                            }
                        }
                    }
                }
            }
        }
    """
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    if request.status_code != 200:
        raise Exception(f"Query failed to run by returning code {request.status_code}. {request.text}")
    return request.json()["data"]["viewer"]["sponsors"]["edges"]

def update_sponsors(db: EdgeDB):
    gh_sponsors = get_sponsors()
    for sponsor in gh_sponsors:
        sponsor = sponsor["node"]
        db.create_sponsor(
            gh_id=sponsor["id"],
            gh_username=sponsor["url"].split("/")[-1],
            gh_url=sponsor["url"]
        )
        db.update_sponsor_gh_username(
            gh_id=sponsor["id"],
            gh_username=sponsor["url"].split("/")[-1]
        )
        db.update_sponsor_gh_url(
            gh_id=sponsor["id"],
            gh_url=sponsor["url"]
        )
    print("Sponsors list updated")

def get_contributors():
    response = requests.get(f"https://api.github.com/repos/{GH_REPO}/contributors")
    if response.status_code != 200:
        raise Exception(f"Query failed to run by returning code {response.status_code}. {response.text}")
    users = []
    for user in response.json():
        if user["type"] == "User":
            users.append(user)
    return users

def update_contributors(db: EdgeDB):
    contributors = get_contributors()
    for contributor in contributors:
        gh_id = contributor["node_id"]
        does_exist = db.get_sponsor_by_gh_id(gh_id)
        if does_exist:
            db.update_sponsor_is_contributor(gh_id, True)
        else:
            db.create_sponsor(
                gh_id=gh_id,
                gh_username=contributor["login"],
                gh_url=contributor["html_url"],
                is_contributor=True
            )
    print("Contributors list updated")

def main():
    db = EdgeDB()
    update_sponsors(db)
    update_contributors(db)
    

if __name__ == "__main__":
    main()