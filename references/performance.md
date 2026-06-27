# Performance Reference

## Expected runtimes (approximate)

| Operation | 100 rows | 10,000 rows | 1,000,000 rows |
|-----------|----------|-------------|-----------------|
| read_table (CSV) | < 0.01s | < 0.05s | < 0.5s |
| read_table (Parquet) | < 0.01s | < 0.03s | < 0.2s |
| render (bar) | < 0.5s | < 1s | < 5s |
| render (line) | < 0.5s | < 1s | < 5s |
| render (scatter) | < 0.3s | < 1s | < 10s |
| sha256 | < 0.01s | < 0.01s | < 0.1s |

Measured on a standard workstation with Python 3.13.
