# SQL for the Akkeri database

This directory contains the SQL needed to create and alter the database schema
for the Akkeri database in PostgreSQL. In the subdir `initial_schema` you will
find a single file, `akkeri-schema.sql` for creating the relevant tables in
a fresh database. It contains definitions for the following tables:

- users: User table.
- roles: The different types of roles that have been defined. Some roles are
  inserted immediately after database creation.
- x_user_role: The roles that have been assigned to each user.
- post_types: The different types of posts that have been defined. Some types
  are inserted immediately after creation.
- languages: The defined languages. Initially populated with English, Icelandic
  and Arabic.
- tags: Tags table.
- images: Images table.
- x_image_tag: Which tags are assigned to each image.
- attachments: Attachments table - i.e. files which are not images.
- x_attachment_tag: Which tags are assigned to each attachment.
- posts: Articles, news, stories, etc.
- x_post_image: Assignment of images to posts.
- x_post_attachment: Assignment of attachments to posts.
- x_post_tag: Which tags are assigned to each post.
- featured: Which posts are featured on the front page and elsewhere.

With a fresh database, you simply do

    psql $MY_DATABASE_NAME < initial_schema/akkeri-schema.sql

Any changes to the initial schema go into the directory `schema_changes`. The
files therein should have the extension `*.sql` and have a file name starting
with the ISO date when the file was created. This ensures that they are
applied in order.
