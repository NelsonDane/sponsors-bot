module default {
    type Sponsor {
        required gh_id: int32 {
            delegated constraint exclusive;
        }
        required gh_username: str {
            delegated constraint exclusive;
        }
        gh_url := "https://github.com/" ++ .gh_username;
        discord_id: int64 {
            delegated constraint exclusive;
            default := 0;
        }
        discord_name: str;
        discord_code: str {
            delegated constraint exclusive;
        }
        contributed_to_repos: array<str> {
            default := <array<str>>[];
        }
        is_contributor:= len(.contributed_to_repos) > 0;
        is_currently_sponsoring: bool {
            default := false;
        }
    }
}
