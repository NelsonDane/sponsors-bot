CREATE MIGRATION m1wcxdgnd4ifdkmozsp7uebx4a4ekrhsh6ylagtllppeyok3xvcigq
    ONTO m1z4j4vb2xicspsa44wju4e73s35gahhwsv4kfes5mfy3k26fnsiqq
{
  ALTER TYPE default::Sponsor {
      ALTER PROPERTY gh_name {
          RENAME TO gh_username;
      };
  };
};
