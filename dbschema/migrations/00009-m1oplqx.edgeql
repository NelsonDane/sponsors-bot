CREATE MIGRATION m1oplqxaysweqke6e2eubgbs6afumsw7jm7lstehadtxh6kvaplega
    ONTO m1hc5c3zrhhuhxzrc45jj24oxfthwtdaoijjz6smmo7ussjn5uaeuq
{
  ALTER TYPE default::Sponsor {
      ALTER PROPERTY discord_id {
          SET default := 0;
      };
      ALTER PROPERTY gh_username {
          SET REQUIRED USING (<std::str>{});
      };
      ALTER PROPERTY gh_url {
          USING (('https://github.com/' ++ .gh_username));
      };
  };
};
