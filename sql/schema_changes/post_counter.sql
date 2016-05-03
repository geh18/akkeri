BEGIN;

alter table posts add column views integer default 0;

COMMIT;
