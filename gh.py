import requests
from db import PostgresDB
from config import GH_TOKEN, GH_SPONSORS_TIER_ID, GH_REPOS

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
                                ... on Actor {
                                    login
                                }
                            }
                        }
                    }
                }
            }
        }
    """
    query = query % GH_SPONSORS_TIER_ID
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    if request.status_code != 200:
        raise Exception(f"Query failed to run by returning code {request.status_code}. {request.text}")
    return request.json()["data"]["viewer"]["sponsors"]["edges"]

def update_sponsors(db: PostgresDB):
    users = db.get_sponsors()
    gh_sponsors = get_sponsors()
    for user in users:
        if not any(sponsor["node"]["databaseId"] == user.gh_id for sponsor in gh_sponsors):
            if user.is_currently_sponsoring:
                print(f"User {user.gh_username} is no longer sponsoring")
            db.update_sponsor_is_currently_sponsoring(user.gh_id, False)
    for sponsor in gh_sponsors:
        sponsor = sponsor["node"]
        if db.get_sponsor_by_gh_id(sponsor["databaseId"]):
            db.update_sponsor_is_currently_sponsoring(sponsor["databaseId"], True)
            db.update_sponsor_gh_username(sponsor["databaseId"], sponsor["login"])
        else:
            db.create_sponsor(
                gh_id=sponsor["databaseId"],
                gh_username=sponsor["login"],
                is_currently_sponsoring=True
            )
    print("Sponsors list updated")

def get_contributors():
    contributors = []
    for repo in GH_REPOS:
        repo_name = repo["LINK"].replace("https://github.com/", "").replace(".git", "")
        response = requests.get(f"https://api.github.com/repos/{repo_name}/contributors")
        if response.status_code != 200:
            raise Exception(f"Query failed to run by returning code {response.status_code}. {response.text}")
        users = []
        for user in response.json():
            if user["type"] == "User":
                contrib_user = {
                    "id": user["id"],
                    "login": user["login"],
                    "repos": [repo["LINK"]]
                }
                users.append(contrib_user)
        contributors += users
    return users

def update_contributors(db: PostgresDB):
    contributors = get_contributors()
    for contributor in contributors:
        if db.get_sponsor_by_gh_id(contributor["id"]):
            db.update_sponsor_contributed_to_repos(contributor["id"], contributor["repos"])
        else:
            db.create_sponsor(
                gh_id=contributor["id"],
                gh_username=contributor["login"],
                contributed_to_repos=contributor["repos"],
            )
    print("Contributors list updated")