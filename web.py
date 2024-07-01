import discordoauth2
from flask import Flask, request, redirect
from db import EdgeDB
from icmplib.exceptions import NameLookupError
from icmplib import ping
from config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI

client_oauth2 = discordoauth2.Client(
        id=CLIENT_ID,
        secret=CLIENT_SECRET,
        redirect=REDIRECT_URI,
        bot_token=None
    )
app = Flask(__name__)

def check_db():
    try:
        # Try to ping Docker db
        host = ping('web', count=3, interval=0.2, timeout=1, privileged=True)
        if host.is_alive:
            return 'web'
    except NameLookupError:
        return '127.0.0.1'

def generate_uri():
    return client_oauth2.generate_uri(scope=["identify", "connections", "role_connections.write"])

@app.route('/')
def main():
    return redirect(generate_uri())

@app.route("/oauth2")
def oauth2():
    # Get code from redirect
    code = request.args.get("code", None)
    if code is None:
        return "Error: No code provided from redirect"
    # Exchange code for access token
    try:
        access = client_oauth2.exchange_code(code)
    except Exception as e:
        if "invalid/don't match" in str(e):
            return "Please run /verify again instead of refreshing the page."
        return str(e)
    # Get user info
    identify = access.fetch_identify()
    connections = access.fetch_connections()
    db = EdgeDB()
    for connection in connections:
        if connection["type"] == "github":
            # GitHub connection found
            gh_username = connection["name"]
            gh_id = connection["id"]
            if not db.get_sponsor_by_gh_id(gh_id):
                db.create_sponsor(
                    gh_id=gh_id,
                    gh_username=gh_username,
                    discord_id=identify["id"],
                    discord_name=identify["username"],
                    discord_code=code,
                )
            else:
                db.update_sponsor_discord_id(
                    gh_id=gh_id,
                    discord_id=identify["id"],
                )
                db.update_sponsor_discord_name(
                    gh_id=gh_id,
                    discord_name=identify["username"],
                )
                db.update_sponsor_discord_code(
                    gh_id=gh_id,
                    discord_code=code,
                )
            return "Connection Success! Now go back to Discord and run /verify one more time."
    # No GitHub connection found
    return "GitHub connection not found. Please connect your GitHub account."

if __name__ == "__main__":
    ip = check_db()
    print(f"Database IP: {ip}")
    app.run(ip, 8080)
