LIST JAR "/path/to/some.jar";

LIST JAR '/some/other.jar';

LIST JAR "/path with space/abc.jar";

LIST JARS "/path with space/def.jar" '/path with space/ghi.jar';

LIST JAR "ivy://group:module:version";

LIST JAR "ivy://group:module:version?transitive=false";

LIST JAR "ivy://group:module:version?transitive=true";

LIST JAR "ivy://group:module:version?exclude=group:module&transitive=true";

-- NB: Non-quoted paths are not supported in SQLFluff currently
--LIST JAR /tmp/test.jar;
