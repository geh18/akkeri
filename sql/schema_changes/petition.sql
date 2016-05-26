BEGIN;

create table petitions (
    id serial not null primary key,
    created_by int not null references users (id) on update cascade on delete restrict,
    title varchar,
    description text,
    added timestamp without time zone default now(),
    is_active boolean not null default false,
    active_until timestamp without time zone,
    published timestamp without time zone,
    with_facebook boolean not null default true
);

create table petition_signatures (
    id serial not null primary key,
    petition_id int not null references petitions (id) on update cascade on delete restrict,
    fb_id varchar not null unique,
    fb_name varchar not null,
    fb_email varchar,
    fb_image varchar,
    is_anononymous boolean default false,
    added timestamp without time zone default now()
);

commit;
