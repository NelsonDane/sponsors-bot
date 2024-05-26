CREATE MIGRATION m1bm5evufxtbmflwdupf6tunmnxcc2eq6wge27lxtt6m5dkpsf6ibq
    ONTO m1wcxdgnd4ifdkmozsp7uebx4a4ekrhsh6ylagtllppeyok3xvcigq
{
  ALTER TYPE default::Sponsor {
      ALTER PROPERTY gh_id {
          SET TYPE std::int32 USING (<std::int32>.gh_id);
      };
  };
};
