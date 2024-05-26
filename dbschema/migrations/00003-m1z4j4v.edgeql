CREATE MIGRATION m1z4j4vb2xicspsa44wju4e73s35gahhwsv4kfes5mfy3k26fnsiqq
    ONTO m1pj46rh6h7ryzj5qxwg2kj72tgjzj5amb4llyh7mzrpuoezvuxwtq
{
  ALTER TYPE default::Sponsor {
      ALTER PROPERTY gh_id {
          CREATE DELEGATED CONSTRAINT std::exclusive;
      };
  };
};
