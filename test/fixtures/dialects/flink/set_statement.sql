SET 'table.exec.state.ttl' = '10d';
SET execution.runtime-mode = streaming;
SET pipeline.name = 'foo';
SET execution.checkpointing.mode = EXACTLY_ONCE;
