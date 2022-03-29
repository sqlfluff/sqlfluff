LIST FILE "/path/to/file/abc.txt";

LIST FILE '/another/test.txt';

LIST FILE "/path with space/abc.txt";

LIST FILE "/path/to/some/directory";

LIST FILES "/path with space/cde.txt" '/path with space/fgh.txt';

-- NB: Non-quoted paths are not supported in SQLFluff currently
--LIST FILE /tmp/test;
