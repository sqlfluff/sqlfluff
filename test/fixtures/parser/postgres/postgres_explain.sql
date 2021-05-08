explain (analyze true, costs false, verbose true, buffers true, format xml) select 1;

explain analyze verbose select 1;

explain analyze select 1;

explain (format text) select 1;

explain (format json) select 1;

explain (format yaml) select 1;
