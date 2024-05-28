CREATE MIGRATION m1zx2rdi4rofjvmgltbfld6xr63ccix3ejzjknic6m53vclrjiv2ba
    ONTO m1oplqxaysweqke6e2eubgbs6afumsw7jm7lstehadtxh6kvaplega
{
  ALTER TYPE default::Sponsor {
      ALTER PROPERTY discord_id {
          SET TYPE std::int64;
      };
  };
};
