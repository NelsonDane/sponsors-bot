import os
import discordoauth2
from flask import Flask, request, redirect
from dotenv import load_dotenv
from db import EdgeDB

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")


client_oauth2 = discordoauth2.Client(
        id=CLIENT_ID,
        secret=CLIENT_SECRET,
        redirect=REDIRECT_URI,
        bot_token=None
    )
app = Flask(__name__)

def generate_uri():
    return client_oauth2.generate_uri(scope=["identify", "connections", "role_connections.write"])

@app.route('/')
def main():
    return redirect(generate_uri())

@app.route("/oauth2")
def oauth2():
    code = request.args.get("code")

    access = client_oauth2.exchange_code(code)

    identify = access.fetch_identify()
    connections = access.fetch_connections()
    for connection in connections:
        if connection["type"] == "github":
            gh_username = connection["name"]
            gh_id = connection["id"]
            db = EdgeDB()
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
    return "Success! You can now close this tab."

if __name__ == "__main__":
    app.run("127.0.0.1", 8080)