import edgedb

class EdgeDB:
    def __init__(self):
        self.client = edgedb.create_client()

    def create_sponsor(self, gh_id, gh_url, discord_id='', gh_username='',  discord_name='', is_contributor=False):
        if self.get_sponsor_by_gh_id(gh_id):
            return
        if gh_username is None or gh_username == "":
            gh_username = gh_url.split("/")[-1]
        self.client.execute('''
            INSERT Sponsor {
                gh_id := <str>$gh_id,
                discord_id := <str>$discord_id,
                gh_username := <str>$gh_username,
                gh_url := <str>$gh_url,
                discord_name := <str>$discord_name,
                is_contributor := <bool>$is_contributor
            };
        ''', gh_id=gh_id, discord_id=discord_id, gh_username=gh_username, gh_url=gh_url, is_contributor=is_contributor, discord_name=discord_name)

    def get_sponsor_by_gh_id(self, gh_id):
        return self.client.query_single('''
            SELECT DISTINCT Sponsor {
                gh_id,
                gh_username,
                gh_url,
                is_contributor,
                discord_name
            }
            FILTER .gh_id = <str>$gh_id
            LIMIT 1;
        ''', gh_id=gh_id)

    def get_sponsor_by_discord_id(self, discord_id):
        return self.client.query_single('''
            SELECT Sponsor {
                gh_id,
                gh_username,
                gh_url,
                is_contributor,
                discord_name
            }
            FILTER .discord_id = <str>$discord_id
            LIMIT 1;
        ''', discord_id=discord_id)
    
    def update_sponsor_gh_username(self, gh_id, gh_username):
        sponsor = self.get_sponsor_by_gh_id(gh_id)
        if not sponsor:
            return
        if gh_username is None or gh_username == "":
            gh_username = sponsor.gh_url.split("/")[-1]
        self.client.execute('''
            UPDATE Sponsor
            FILTER .gh_id = <str>$gh_id
            SET {
                gh_username := <str>$gh_username
            };
        ''', gh_id=gh_id, gh_username=gh_username)

    def update_sponsor_gh_url(self, gh_id, gh_url):
        if not self.get_sponsor_by_gh_id(gh_id):
            return
        self.client.execute('''
            UPDATE Sponsor
            FILTER .gh_id = <str>$gh_id
            SET {
                gh_url := <str>$gh_url
            };
        ''', gh_id=gh_id, gh_url=gh_url)

    def update_sponsor_discord_id(self, gh_id, discord_id):
        if not self.get_sponsor_by_gh_id(gh_id):
            return
        self.client.execute('''
            UPDATE Sponsor
            FILTER .gh_id = <str>$gh_id
            SET {
                discord_id := <str>$discord_id
            };
        ''', gh_id=gh_id, discord_id=discord_id)

    def update_sponsor_discord_name(self, gh_id, discord_name):
        if not self.get_sponsor_by_gh_id(gh_id):
            return
        self.client.execute('''
            UPDATE Sponsor
            FILTER .gh_id = <str>$gh_id
            SET {
                discord_name := <str>$discord_name
            };
        ''', gh_id=gh_id, discord_name=discord_name)

    def update_sponsor_is_contributor(self, gh_id, is_contributor):
        if not self.get_sponsor_by_gh_id(gh_id):
            return
        self.client.execute('''
            UPDATE Sponsor
            FILTER .gh_id = <str>$gh_id
            SET {
                is_contributor := <bool>$is_contributor
            };
        ''', gh_id=gh_id, is_contributor=is_contributor)
