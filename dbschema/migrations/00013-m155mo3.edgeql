CREATE MIGRATION m155mo3smgqn6n5iyysytvslly5zgamgsz5tslh7apns77of2lyixa
    ONTO m1ylpdkwna5yo5g7i6mrklk5wpae7b7f5yrquexqqutvy7yodc6gka
{
  ALTER TYPE default::Sponsor {
      ALTER PROPERTY gh_id {
          RESET OPTIONALITY;
      };
      ALTER PROPERTY gh_username {
          RESET OPTIONALITY;
      };
  };
};
