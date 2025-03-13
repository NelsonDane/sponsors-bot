import psycopg2
from config import DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME
from collections import namedtuple

Sponsor = namedtuple('Sponsor', [
    'gh_id', 'gh_username', 'gh_url', 'discord_id', 'discord_name',
    'discord_code', 'contributed_to_repos', 'is_contributor', 'is_currently_sponsoring'
])

class PostgresDB:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=DB_NAME,
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
        )
        self.cursor = self.conn.cursor()

    def create_sponsor(self, gh_id, gh_username, discord_id=None, discord_name=None, discord_code=None, contributed_to_repos=None, is_currently_sponsoring=False):
        if self.get_sponsor_by_gh_id(gh_id):
            return
        if contributed_to_repos is None:
            contributed_to_repos = []
        self.cursor.execute('''
            INSERT INTO Sponsor (
                gh_id, discord_id, gh_username, discord_name, discord_code,
                contributed_to_repos, is_currently_sponsoring
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (gh_id, discord_id, gh_username, discord_name, discord_code, contributed_to_repos, is_currently_sponsoring))
        self.conn.commit()

    def get_sponsor_by_gh_id(self, gh_id):
        self.cursor.execute('''
            SELECT * FROM Sponsor WHERE gh_id = %s LIMIT 1
        ''', (gh_id,))
        result = self.cursor.fetchone()
        if result:
            return Sponsor(*result)
        return None

    def get_sponsor_by_gh_username(self, gh_username):
        self.cursor.execute('''
            SELECT * FROM Sponsor WHERE LOWER(gh_username) = LOWER(%s) LIMIT 1
        ''', (gh_username,))
        result = self.cursor.fetchone()
        if result:
            return Sponsor(*result)
        return None

    def get_sponsor_by_discord_id(self, discord_id):
        self.cursor.execute('''
            SELECT * FROM Sponsor WHERE discord_id = %s LIMIT 1
        ''', (discord_id,))
        result = self.cursor.fetchone()
        if result:
            return Sponsor(*result)
        return None

    def update_sponsor_gh_username(self, gh_id, gh_username):
        if not self.get_sponsor_by_gh_id(gh_id):
            return
        self.cursor.execute('''
            UPDATE Sponsor SET gh_username = %s WHERE gh_id = %s
        ''', (gh_username, gh_id))
        self.conn.commit()

    def update_sponsor_discord_id(self, gh_id, discord_id):
        if not self.get_sponsor_by_gh_id(gh_id):
            return
        self.cursor.execute('''
            UPDATE Sponsor SET discord_id = %s WHERE gh_id = %s
        ''', (discord_id, gh_id))
        self.conn.commit()

    def update_sponsor_discord_name(self, gh_id, discord_name):
        if not self.get_sponsor_by_gh_id(gh_id):
            return
        self.cursor.execute('''
            UPDATE Sponsor SET discord_name = %s WHERE gh_id = %s
        ''', (discord_name, gh_id))
        self.conn.commit()

    def update_sponsor_discord_code(self, gh_id, discord_code):
        if not self.get_sponsor_by_gh_id(gh_id):
            return
        self.cursor.execute('''
            UPDATE Sponsor SET discord_code = %s WHERE gh_id = %s
        ''', (discord_code, gh_id))
        self.conn.commit()

    def update_sponsor_contributed_to_repos(self, gh_id, contributed_to_repos):
        if not self.get_sponsor_by_gh_id(gh_id):
            return
        self.cursor.execute('''
            UPDATE Sponsor SET contributed_to_repos = %s WHERE gh_id = %s
        ''', (contributed_to_repos, gh_id))
        self.conn.commit()

    def update_sponsor_is_currently_sponsoring(self, gh_id, is_currently_sponsoring):
        if not self.get_sponsor_by_gh_id(gh_id):
            return
        self.cursor.execute('''
            UPDATE Sponsor SET is_currently_sponsoring = %s WHERE gh_id = %s
        ''', (is_currently_sponsoring, gh_id))
        self.conn.commit()

    def get_sponsors(self):
        self.cursor.execute('SELECT * FROM Sponsor')
        results = self.cursor.fetchall()
        return [Sponsor(*result) for result in results]
