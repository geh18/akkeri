BEGIN;

-- NOTE: if you have activated an earlier version of this file,
-- you may need to uncomment the following two lines:
-- alter table posts drop column post_display_id;
-- drop table post_display;


create table post_display (
    id serial not null primary key,
    label varchar not null unique,
    description varchar
);

insert into post_display (label) values ('cover_post');
insert into post_display (label) values ('article_item_1');
insert into post_display (label) values ('article_item_2');

ALTER TABLE posts ADD post_display_id int
  references post_display(id) on update cascade on delete set null;

COMMIT;
