-- Requires shared_preload_libraries='pg_stat_statements' and server restart before CREATE EXTENSION.
SELECT queryid,calls,round(total_exec_time::numeric,2) total_ms,
 round(mean_exec_time::numeric,2) mean_ms,rows,shared_blks_hit,shared_blks_read,
 temp_blks_written,query FROM pg_stat_statements
WHERE dbid=(SELECT oid FROM pg_database WHERE datname=current_database()) ORDER BY total_exec_time DESC LIMIT 20;
SELECT queryid,calls,query FROM pg_stat_statements WHERE dbid=(SELECT oid FROM pg_database WHERE datname=current_database()) ORDER BY calls DESC LIMIT 20;
SELECT schemaname,relname,seq_scan,seq_tup_read,idx_scan,idx_tup_fetch,n_live_tup,n_dead_tup
FROM pg_stat_user_tables ORDER BY seq_tup_read DESC;
SELECT schemaname,relname,indexrelname,idx_scan,idx_tup_read,idx_tup_fetch FROM pg_stat_user_indexes ORDER BY idx_scan DESC;
SELECT schemaname,relname,heap_blks_read,heap_blks_hit,idx_blks_read,idx_blks_hit FROM pg_statio_user_tables;
SELECT n.nspname,c.relname,pg_size_pretty(pg_relation_size(c.oid)) heap,
pg_size_pretty(pg_indexes_size(c.oid)) indexes,pg_size_pretty(pg_total_relation_size(c.oid)) total
FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname IN ('credit','private','mart','audit') AND c.relkind IN ('r','m') ORDER BY pg_total_relation_size(c.oid) DESC;
