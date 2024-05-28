import edgedb

class EdgeDB:
    def __init__(self):
        self.client = edgedb.create_client()

    def create_sponsor(self, gh_id, gh_username, discord_id=0, discord_name='', discord_code='', is_contributor=False):
        if self.get_sponsor_by_gh_id(gh_id):
            return
        self.client.execute('''
            INSERT Sponsor {
                gh_id := <int32>$gh_id,
                discord_id := <int64>$discord_id,
                gh_username := <str>$gh_username,
                discord_name := <str>$discord_name,
                discord_code := <str>$discord_code,
                is_contributor := <bool>$is_contributor
            };
        ''', gh_id=int(gh_id), discord_id=int(discord_id), gh_username=gh_username, is_contributor=is_contributor, discord_name=discord_name, discord_code=discord_code)

    def get_sponsor_by_gh_id(self, gh_id):
        return self.client.query_single('''
            SELECT DISTINCT Sponsor {
                gh_id,
                gh_username,
                is_contributor,
                discord_name,
                discord_id
            }
            FILTER .gh_id = <int32>$gh_id
            LIMIT 1;
        ''', gh_id=int(gh_id))

    def get_sponsor_by_discord_id(self, discord_id):
        return self.client.query_single('''
            SELECT Sponsor {
                gh_id,
                gh_username,
                is_contributor,
                discord_name,
                discord_id
            }
            FILTER .discord_id = <int64>$discord_id
            LIMIT 1;
        ''', discord_id=int(discord_id))
    
    def update_sponsor_gh_username(self, gh_id, gh_username):
        sponsor = self.get_sponsor_by_gh_id(gh_id)
        if not sponsor:
            return
        self.client.execute('''
            UPDATE Sponsor
            FILTER .gh_id = <int32>$gh_id
            SET {
                gh_username := <str>$gh_username
            };
        ''', gh_id=int(gh_id), gh_username=gh_username)

    def update_sponsor_discord_id(self, gh_id, discord_id):
        if not self.get_sponsor_by_gh_id(gh_id):
            return
        self.client.execute('''
            UPDATE Sponsor
            FILTER .gh_id = <int32>$gh_id
            SET {
                discord_id := <int64>$discord_id
            };
        ''', gh_id=int(gh_id), discord_id=int(discord_id))

    def update_sponsor_discord_name(self, gh_id, discord_name):
        if not self.get_sponsor_by_gh_id(gh_id):
            return
        self.client.execute('''
            UPDATE Sponsor
            FILTER .gh_id = <int32>$gh_id
            SET {
                discord_name := <str>$discord_name
            };
        ''', gh_id=int(gh_id), discord_name=discord_name)

    def update_sponsor_discord_code(self, gh_id, discord_code):
        if not self.get_sponsor_by_gh_id(gh_id):
            return
        self.client.execute('''
            UPDATE Sponsor
            FILTER .gh_id = <int32>$gh_id
            SET {
                discord_code := <str>$discord_code
            };
        ''', gh_id=int(gh_id), discord_code=discord_code)

    def update_sponsor_is_contributor(self, gh_id, is_contributor):
        if not self.get_sponsor_by_gh_id(gh_id):
            return
        self.client.execute('''
            UPDATE Sponsor
            FILTER .gh_id = <int32>$gh_id
            SET {
                is_contributor := <bool>$is_contributor
            };
        ''', gh_id=int(gh_id), is_contributor=is_contributor)
