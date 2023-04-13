ADD JAR "/path/to/some.jar";

ADD JAR '/some/other.jar';

ADD JAR "/path with space/abc.jar";

ADD JARS "/path with space/def.jar" '/path with space/ghi.jar';

ADD JAR "ivy://group:module:version";

ADD JAR "ivy://group:module:version?transitive=false";

ADD JAR "ivy://group:module:version?transitive=true";

ADD JAR "ivy://group:module:version?exclude=group:module&transitive=true";

ADD JAR ivy://group:module:version?exclude=group:module&transitive=true;

ADD JAR /path/to/some.jar;

ADD JAR path/to/some.jar;

ADD JAR ivy://path/to/some.jar;

-- NB: Non-quoted paths do not currently support whitespaces
-- e.g. /path to/some.jar
