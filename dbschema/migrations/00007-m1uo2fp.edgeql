CREATE MIGRATION m1uo2fp6ncr6j37zwii7sdawm2sp6vuggug7iy7jsfqrr54dt3le5a
    ONTO m1upcwehutg2wleeziqwfop3pfgyl45wiyz3vtshv2k7fcvdq3hb2q
{
  ALTER TYPE default::Sponsor {
      ALTER PROPERTY discord_code {
          CREATE DELEGATED CONSTRAINT std::exclusive;
      };
      ALTER PROPERTY discord_id {
          CREATE DELEGATED CONSTRAINT std::exclusive;
          SET TYPE std::int32 USING (<std::int32>.discord_id);
      };
  };
};
