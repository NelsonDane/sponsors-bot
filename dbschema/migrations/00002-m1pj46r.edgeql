CREATE MIGRATION m1pj46rh6h7ryzj5qxwg2kj72tgjzj5amb4llyh7mzrpuoezvuxwtq
    ONTO m17krncdk5ewh6md65gn7ij7ou5xwox7crh6lj7xyios6u46o6dniq
{
  ALTER TYPE default::Sponsor {
      ALTER PROPERTY discord_id {
          RESET OPTIONALITY;
      };
      CREATE PROPERTY discord_name: std::str;
  };
};
