BEGIN;

alter table posts add column location varchar;

COMMIT;
