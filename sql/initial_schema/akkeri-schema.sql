-- This is the initial schema for the Akkeri flask app.

begin;


create table users (
       id serial not null primary key,
       username varchar not null unique,
       password varchar not null,
       email varchar not null unique,
       fullname varchar not null,
       user_location varchar,
       active boolean not null default true,
       -- The Profile is a special post of type 6 with the user as author.
       -- There can be one for each language. Even if present, it will not
       -- be displayed unless the author's show_profile is true as well.
       show_profile boolean not null default false,
       is_superuser boolean not null default false,
       created timestamp without time zone default now(),
       changed timestamp without time zone default now()
);


create table roles (
       id serial not null primary key,
       label varchar not null unique,
       description varchar
);

-- I. Roles based on type of user
insert into roles (label, description) values ('group_refugee', 'Belongs to Refugee group');
insert into roles (label, description) values ('group_volunteer', 'Belongs to Volunteer group');
insert into roles (label, description) values ('group_oped', 'Belongs to Op-Ed group');
insert into roles (label, description) values ('group_editor', 'Belongs to Editor group');

-- II. Roles based on degree of access:
-- (a) Access for Editors and/or Administrators:
insert into roles (label, description) values ('all_users', 'Can view, add, change and delete Users ');
insert into roles (label, description) values ('all_roles', 'Can view, add, change and delete Roles');
insert into roles (label, description) values ('all_images', 'Can add, change and delete any Image');
insert into roles (label, description) values ('all_attachments', 'Can add, change and delete any Attachment');
insert into roles (label, description) values ('all_posts', 'Can add, change and delete any Post');
-- Wrt Tags, note that all users can add those, but not everybody can designate them
-- as important or restrict them to specific areas.
insert into roles (label, description) values ('all_tags', 'Can change properties of Tags');
insert into roles (label, description) values ('all_featured', 'Can designate posts as Featured');
-- (b) Access for non-editor staff and outsiders:
insert into roles (label, description) values ('own_images', 'Can add, change and delete own Images');
insert into roles (label, description) values ('own_attachments', 'Can add, change and delete own Attachments');
insert into roles (label, description) values ('own_posts', 'Can add, change and delete own Posts');


create table x_user_role (
       id serial not null primary key,
       user_id int not null references users (id) on update cascade on delete cascade,
       role_id int not null references roles (id) on update cascade on delete cascade,
       granted_at timestamp without time zone default now(),
       unique (user_id, role_id)
);


create table post_types (
       id int not null primary key,
       label varchar not null unique,
       name_is varchar,
       name_en varchar
);

insert into post_types values (1, 'journey', 'Ferðasaga flóttamanns', 'A Refugee''s Journey');
insert into post_types values (2, 'volunteer', 'Saga sjálfboðaliða', 'A Volunteer''s Tale');
insert into post_types values (3, 'article', 'Grein', 'Article');
insert into post_types values (4, 'news', 'Frétt', 'News');
insert into post_types values (5, 'page', 'Síða', 'Page');
insert into post_types values (6, 'profile', 'Um höfund', 'Author Profile');


create table languages (
       id int not null primary key,
       code varchar(2),
       name_is varchar,
       name_en varchar
);

insert into languages values (1, 'en', 'Enska', 'English');
insert into languages values (2, 'is', 'Íslenska', 'Icelandic');
insert into languages values (3, 'ar', 'Arabíska', 'Arabic');


create table tags (
       id serial not null primary key,
       name varchar not null unique,
       is_important boolean not null default false,
       for_images boolean not null default true,
       for_attachments boolean not null default true,
       for_posts boolean not null default true,
       created timestamp without time zone default now()
);


create table images (
       id serial not null primary key,
       owner_id int not null references users (id) on update cascade on delete restrict,
       image_path varchar not null unique,
       title varchar,
       credit varchar,
       caption text,
       image_taken timestamp without time zone,
       width int not null default 0,
       height int not null default 0,
       bytes int not null default 0,
       active boolean not null default true,
       available_to_others boolean not null default false,
       added timestamp without time zone default now(),
       changed timestamp without time zone default now()
);

create index ix_image_owner on images (owner_id);
create index ix_image_added on images (added);


create table x_image_tag (
       id serial not null primary key,
       image_id int references images (id) on update cascade on delete cascade,
       tag_id int references tags (id) on update cascade on delete cascade,
       tagged_at timestamp without time zone default now(),
       unique (image_id, tag_id)
);


create table attachments (
       id serial not null primary key,
       owner_id int not null references users (id) on update cascade on delete restrict,
       attachment_path varchar not null unique,
       title varchar,
       credit varchar,
       caption text,
       bytes int not null default 0,
       attachment_date timestamp without time zone,
       preview_image int references images (id) on update cascade on delete set null,
       active boolean not null default true,
       available_to_others boolean not null default false,
       added timestamp without time zone default now(),
       changed timestamp without time zone default now()
);

create index ix_attachment_owner on attachments (owner_id);
create index ix_attachment_added on attachments (added);


create table x_attachment_tag (
       id serial not null primary key,
       attachment_id int references attachments (id) on update cascade on delete cascade,
       tag_id int references tags (id) on update cascade on delete cascade,
       tagged_at timestamp without time zone default now(),
       unique (attachment_id, tag_id)
);


create table posts (
       id serial not null primary key,
       author_id int not null references users (id) on update cascade on delete restrict,
       last_changed_by int references users (id) on update cascade on delete set null,
       author_visible boolean not null default true,
       author_line varchar,
       title varchar not null,
       slug varchar not null unique,
       is_draft boolean not null default false,
       summary text,
       body text,
       post_type_id int references post_types (id) on update cascade on delete set null,
       language_id int references languages (id) on update cascade on delete set null,
       created timestamp without time zone default now(),
       changed timestamp without time zone default now(),
       published timestamp without time zone
);

create index ix_post_author on posts (author_id);
create index ix_post_created on posts (created);
create index ix_post_published on posts (published);


create table x_post_image (
       id serial not null primary key,
       post_id int not null references posts (id) on update cascade on delete cascade,
       image_id int not null references images (id) on update cascade on delete cascade,
       image_order int not null default 1,
       custom_title varchar,
       custom_caption text,
       linked_at timestamp without time zone default now()
);


create table x_post_attachment (
       id serial not null primary key,
       post_id int not null references posts (id) on update cascade on delete cascade,
       attachment_id int not null references attachments (id) on update cascade on delete cascade,
       attachment_order int not null default 1,
       custom_title varchar,
       custom_caption text,
       linked_at timestamp without time zone default now()
);


create table x_post_tag (
       id serial not null primary key,
       post_id int references posts (id) on update cascade on delete cascade,
       tag_id int references tags (id) on update cascade on delete cascade,
       tagged_at timestamp without time zone default now(),
       unique (post_id, tag_id)
);


create table featured (
       id serial not null primary key,
       post_id int not null references posts (id) on update cascade on delete cascade,
       featured_from timestamp without time zone not null default now(),
       featured_to timestamp without time zone not null default now(),
       for_frontpage boolean not null default false,
       for_category_page boolean not null default true,
       added_by int references users (id) on update cascade on delete cascade,
       added_at timestamp without time zone not null default now()
);

create index ix_featured_from on featured (featured_from);
create index ix_featured_to on featured (featured_to);


commit;
