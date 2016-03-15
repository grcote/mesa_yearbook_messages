drop table if exists yb_notes;
create table yb_notes (
  id  integer primary key autoincrement,
  email text  unique,
  teacher text,
  parent text,
  student text,
  message text,
  comments text
);