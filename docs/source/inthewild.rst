.. _inthewildref:

SQLFluff in the Wild
====================

Want to find other people who are using SQLFluff in production
use cases? Want to brag about how you're using it? Just want to
show solidarity with the project and provide a testimonial for it?

Just add a section below by raising a PR on Github by
`editing this file ✏️ <https://github.com/sqlfluff/sqlfluff/edit/master/docs/source/inthewild.rst>`_.

- SQLFluff in production `dbt <http://www.getdbt.com/>`_ projects at
  `tails.com <https://tails.com>`_. We use the SQLFluff cli as part
  of our CI pipeline in `codeship <https://codeship.com>`_ to enforce
  certain styles in our SQL codebase (with over 650 models) and keep
  code quality high. Contact `@alanmcruickshank <https://github.com/alanmcruickshank>`_.
- `Netlify <https://www.netlify.com>`_'s data team uses SQLFluff with
  `dbt <http://www.getdbt.com/>`_ to keep code quality in more than 350
  models (and growing). Previously, we had our SQL Guidelines defined in
  a site hosted with Netlify, and now we're enforcing these rules in our
  CI workflow thanks to SQLFluff.
- `Drizly's <https://www.drizly.com>`_ analytics team uses SQLFluff with
  `dbt <http://www.getdbt.com/>`_ for over 700 models as part of our CI checks in github.
  Before SQLFluff, we had SQL best practices outlined in a google doc and had to manually 
  enforce through PR comments. We're now able to enforce much of our style guide automatically through SQLFluff.
