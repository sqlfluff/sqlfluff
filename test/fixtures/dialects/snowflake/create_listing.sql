-- Basic listing with inline manifest
CREATE LISTING my_listing
  AS '---
title: "My Listing"
description: "A data listing"
';

-- External listing with share
CREATE EXTERNAL LISTING IF NOT EXISTS my_listing
  SHARE my_share
  AS '---
title: "My Share Listing"
'
  PUBLISH = TRUE
  REVIEW = TRUE
  COMMENT = 'marketplace listing';

-- Listing from stage manifest
CREATE LISTING my_listing
  APPLICATION PACKAGE my_package
  FROM '@my_stage/manifest.yml';
