CREATE MIGRATION m1ylpdkwna5yo5g7i6mrklk5wpae7b7f5yrquexqqutvy7yodc6gka
    ONTO m1mj3foqfaxoobfnpyfi4udrkr5edxkcy44w3wspghunzxlbdreipq
{
  ALTER TYPE default::Sponsor {
      CREATE PROPERTY contributed_to_repos: array<std::str> {
          SET default := (<array<std::str>>[]);
      };
      ALTER PROPERTY is_contributor {
          RESET default;
          USING ((std::len(.contributed_to_repos) > 0));
      };
  };
};
