CREATE MIGRATION m1hc5c3zrhhuhxzrc45jj24oxfthwtdaoijjz6smmo7ussjn5uaeuq
    ONTO m1uo2fp6ncr6j37zwii7sdawm2sp6vuggug7iy7jsfqrr54dt3le5a
{
  ALTER TYPE default::Sponsor {
      ALTER PROPERTY gh_username {
          CREATE DELEGATED CONSTRAINT std::exclusive;
      };
      ALTER PROPERTY gh_url {
          USING (('https://github.com/' ++ default::Sponsor.gh_username));
      };
  };
};
