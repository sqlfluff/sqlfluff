ADD FILE "/path/to/file/abc.txt";

ADD FILE '/another/test.txt';

ADD FILE "/path with space/abc.txt";

ADD FILE "/path/to/some/directory";

ADD FILES "/path with space/cde.txt" '/path with space/fgh.txt';

-- NB: Non-quoted paths are not supported in SQLFluff currently
--ADD FILE /tmp/test;
