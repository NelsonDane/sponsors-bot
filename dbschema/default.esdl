module default {
    type Sponsor {
        required gh_id: str {
            delegated constraint exclusive;
        }
        gh_username: str;
        gh_url: str;
        discord_id: str;
        discord_name: str;
        is_contributor: bool {
            default := false;
        }
    }
}
