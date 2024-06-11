import edgedb

class EdgeDB:
    def __init__(self):
        self.client = edgedb.create_client()

    def create_sponsor(self, gh_id, gh_username, discord_id=0, discord_name='', discord_code='', contributed_to_repos=None, is_currently_sponsoring=False):
        if self.get_sponsor_by_gh_id(gh_id):
            return
        if contributed_to_repos is None:
            contributed_to_repos = []
        self.client.execute('''
            INSERT Sponsor {
                gh_id := <int32>$gh_id,
                discord_id := <int64>$discord_id,
                gh_username := <str>$gh_username,
                discord_name := <str>$discord_name,
                discord_code := <str>$discord_code,
                contributed_to_repos := <array<str>>$contributed_to_repos,
                is_currently_sponsoring := <bool>$is_currently_sponsoring
            };
        ''', gh_id=int(gh_id), discord_id=int(discord_id), gh_username=gh_username, discord_name=discord_name, discord_code=discord_code, contributed_to_repos=contributed_to_repos, is_currently_sponsoring=is_currently_sponsoring)

    def get_sponsor_by_gh_id(self, gh_id):
        return self.client.query_single('''
            SELECT DISTINCT Sponsor {
                gh_id,
                gh_username,
                discord_name,
                discord_id,
                discord_code,
                contributed_to_repos,
                is_contributor,
                is_currently_sponsoring
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
                contributed_to_repos,
                discord_name,
                discord_id,
                discord_code,
                is_currently_sponsoring
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

    def update_sponsor_contributed_to_repos(self, gh_id, contributed_to_repos):
        if not self.get_sponsor_by_gh_id(gh_id):
            return
        self.client.execute('''
            UPDATE Sponsor
            FILTER .gh_id = <int32>$gh_id
            SET {
                contributed_to_repos := <array<str>>$contributed_to_repos
            };
        ''', gh_id=int(gh_id), contributed_to_repos=contributed_to_repos)

    def update_sponsor_is_currently_sponsoring(self, gh_id, is_currently_sponsoring):
        if not self.get_sponsor_by_gh_id(gh_id):
            return
        self.client.execute('''
            UPDATE Sponsor
            FILTER .gh_id = <int32>$gh_id
            SET {
                is_currently_sponsoring := <bool>$is_currently_sponsoring
            };
        ''', gh_id=int(gh_id), is_currently_sponsoring=is_currently_sponsoring)

    def get_sponsors(self):
        return self.client.query('''
            SELECT Sponsor {
                gh_id,
                gh_username,
                is_contributor,
                contributed_to_repos,
                discord_name,
                discord_id,
                discord_code,
                is_currently_sponsoring
            };
        ''')
