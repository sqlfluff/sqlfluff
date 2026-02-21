-- Publish
ALTER LISTING my_listing PUBLISH;

-- Unpublish
ALTER LISTING IF EXISTS my_listing UNPUBLISH;

-- Update manifest
ALTER LISTING my_listing AS '---
title: "Updated Listing"
';

-- Rename
ALTER LISTING my_listing RENAME TO new_listing;

-- Set comment
ALTER LISTING my_listing SET COMMENT = 'updated listing';
