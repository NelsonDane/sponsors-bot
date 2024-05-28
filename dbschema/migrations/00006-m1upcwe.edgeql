CREATE MIGRATION m1upcwehutg2wleeziqwfop3pfgyl45wiyz3vtshv2k7fcvdq3hb2q
    ONTO m1bm5evufxtbmflwdupf6tunmnxcc2eq6wge27lxtt6m5dkpsf6ibq
{
  ALTER TYPE default::Sponsor {
      CREATE PROPERTY discord_code: std::str;
  };
};
