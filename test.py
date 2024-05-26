import discordoauth2
from flask import Flask, request, redirect

client = discordoauth2.Client(ID, secret="SECRET",
redirect="http://127.0.0.1:8080/oauth2", bot_token=None)
app = Flask(__name__)

@app.route('/')
def main():
  return redirect(client.generate_uri(scope=["identify", "connections", "guilds", "role_connections.write"]))

@app.route("/oauth2")
def oauth2():
   code = request.args.get("code")

   access = client.exchange_code(code)

   identify = access.fetch_identify()
   connections = access.fetch_connections()
   guilds = access.fetch_guilds()

   return f"""{identify}<br><br>{connections}<br><br>{guilds}"""

app.run("0.0.0.0", 8080)