/*
	According to https://www.sqlite.org/lang_comment.html, it is valid for a C-style comment to end
	at the "end-of-input", without being closed explicitly. This document is a valid SQLite file,
	but gives a parsing error in SQLFluff.
