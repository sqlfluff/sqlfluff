# TPC Fixture Queries

The SQL files in this directory were copied from the
[Apache Doris](https://github.com/apache/doris) project
([tpch-tools/queries](https://github.com/apache/doris/tree/3a2d9d55f1e8e2d74187179ef89c36c8562815fd/tools/tpch-tools/queries),
[tpcds-tools/queries](https://github.com/apache/doris/tree/3a2d9d55f1e8e2d74187179ef89c36c8562815fd/tools/tpcds-tools/queries))
and are themselves derived from the
[TPC-H](https://www.tpc.org/tpch/) and [TPC-DS](https://www.tpc.org/tpcds/)
benchmark specifications published by the
[Transaction Processing Performance Council (TPC)](https://www.tpc.org/).

## Purpose

These queries are used exclusively as representative real-world SQL inputs for
benchmarking and testing sqlfluff's lexer and parser. They are not used to
produce or publish TPC benchmark performance results, and no claims of TPC
compliance are made.

## Structure

| Directory | Benchmark | Queries      |
|-----------|-----------|--------------|
| `tpc-h/`  | TPC-H     | 22 (Q1–Q22)  |
| `tpc-ds/` | TPC-DS    | 99 (Q1–Q99)  |

### Modifications from the Doris source

TPC-DS queries 14, 23, 24, and 39 each consist of two independent statements
in the original specification. The Doris source stores these as separate files
(`query14.sql` + `query14_1.sql`, etc.). Here they have been consolidated: each
pair is stored in a single numbered file (`14.sql`, `23.sql`, `24.sql`,
`39.sql`), with the statements separated by a blank line.

## Attribution and Copyright

The underlying TPC-H and TPC-DS benchmark specifications are copyrighted by
the Transaction Processing Performance Council. For fair use requirements when
reproducing TPC materials, see the
[TPC Fair Use Quick Reference](https://www.tpc.org/TPC_Documents_Current_Versions/pdf/Fair_Use_Quick_Reference_v1.0.0.pdf).
The official benchmark specifications are available at
[tpc.org](https://www.tpc.org/tpc_documents_current_versions/current_specifications5.asp).
