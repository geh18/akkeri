BEGIN;

alter table posts alter column title set default '';
alter table posts alter column slug set default '';
alter table posts alter column cover_image set default '';

alter table posts alter column title drop not null;
alter table posts alter column slug drop not null;
alter table posts alter column cover_image drop not null;

COMMIT;
