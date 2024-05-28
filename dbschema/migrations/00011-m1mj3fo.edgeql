CREATE MIGRATION m1mj3foqfaxoobfnpyfi4udrkr5edxkcy44w3wspghunzxlbdreipq
    ONTO m1zx2rdi4rofjvmgltbfld6xr63ccix3ejzjknic6m53vclrjiv2ba
{
  ALTER TYPE default::Sponsor {
      CREATE PROPERTY is_currently_sponsoring: std::bool {
          SET default := false;
      };
  };
};
