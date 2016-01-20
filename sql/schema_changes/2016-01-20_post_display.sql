BEGIN;

ALTER TABLE posts ADD post_display_id int references post_display(id) on update cascade on delete set null;

create table post_display (
    id serial not null primary key,
    display varchar,
	post_id int references posts (id) on update cascade on delete cascade;
);



COMMIT;
