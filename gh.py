import requests
import os
from dotenv import load_dotenv
from db import EdgeDB

load_dotenv()
GH_REPO = os.getenv("GH_REPO")
GH_TOKEN = os.getenv("GH_TOKEN")
GH_TIER_ID = os.getenv("GH_TIER_ID")

def get_sponsors():
    headers = {"Authorization": f"token {GH_TOKEN}"}
    query = """
        query SponsorQuery {
            viewer {
                sponsors(first: 100, tierId: "%s") {
                    edges {
                        node {
                            ... on User {
                                databaseId
                                url
                            }
                        }
                    }
                }
            }
        }
    """
    query = query % GH_TIER_ID
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    if request.status_code != 200:
        raise Exception(f"Query failed to run by returning code {request.status_code}. {request.text}")
    return request.json()["data"]["viewer"]["sponsors"]["edges"]

def update_sponsors(db: EdgeDB):
    users = db.get_sponsors()
    gh_sponsors = get_sponsors()
    for user in users:
        if not any(sponsor["node"]["databaseId"] == user.gh_id for sponsor in gh_sponsors):
            db.update_sponsor_is_currently_sponsoring(user.gh_id, False)
    for sponsor in gh_sponsors:
        sponsor = sponsor["node"]
        if db.get_sponsor_by_gh_id(sponsor["databaseId"]):
            db.update_sponsor_is_currently_sponsoring(sponsor["databaseId"], True)
            db.update_sponsor_gh_username(sponsor["databaseId"], sponsor["url"].split("/")[-1])
        else:
            db.create_sponsor(
                gh_id=sponsor["databaseId"],
                gh_username=sponsor["url"].split("/")[-1],
                is_currently_sponsoring=True
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
        if db.get_sponsor_by_gh_id(contributor["id"]):
            db.update_sponsor_is_contributor(contributor["id"], True)
        else:
            db.create_sponsor(
                gh_id=contributor["id"],
                gh_username=contributor["login"],
                is_contributor=True
            )
    print("Contributors list updated")