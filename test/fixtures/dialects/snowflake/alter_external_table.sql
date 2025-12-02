alter external table foo refresh;
alter external table foo refresh '2018/08/05/';
alter external table foo add files ('foo/bar.json.gz', 'bar/foo.json.gz');
alter external table foo remove files ('foo/bar.json.gz', 'bar/foo.json.gz');
alter external table foo add partition(foo='baz', bar='bar', baz='foo') location '2022/01';
alter external table foo drop partition location '2022/01';
alter external table if exists foo set auto_refresh = true;
alter external table if exists foo set tag foo = 'foo', bar = 'bar';
alter external table foo unset tag foo = 'foo';
