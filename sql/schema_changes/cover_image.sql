BEGIN;

alter table posts add column cover_image varchar not null default '';

COMMIT;
