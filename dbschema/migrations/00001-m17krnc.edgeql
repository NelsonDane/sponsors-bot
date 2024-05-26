CREATE MIGRATION m17krncdk5ewh6md65gn7ij7ou5xwox7crh6lj7xyios6u46o6dniq
    ONTO initial
{
  CREATE TYPE default::Sponsor {
      CREATE REQUIRED PROPERTY discord_id: std::str;
      CREATE REQUIRED PROPERTY gh_id: std::str;
      CREATE PROPERTY gh_name: std::str;
      CREATE PROPERTY gh_url: std::str;
      CREATE PROPERTY is_contributor: std::bool {
          SET default := false;
      };
  };
};
