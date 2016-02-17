BEGIN;

alter table images add post_id int references posts(id) on update cascade on delete cascade;

COMMIT;
