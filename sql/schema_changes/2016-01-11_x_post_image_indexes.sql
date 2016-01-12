-- This ensures that the combination of (post_id, image_order)
-- is unique in the x_post_image table. The main reason that this
-- is important is that there should be at most one featured image
-- (with image_order==1) for each post.

BEGIN;

create unique index on x_post_image (post_id, image_order);
create index ix_xpi_post on x_post_image (post_id);

COMMIT;
