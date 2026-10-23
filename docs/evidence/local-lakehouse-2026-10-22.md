# Local Spark/Delta evidence — 2026-10-22

## Purpose

This run verifies that the lakehouse ideas can be learned locally without paying for Databricks or installing Java on the host. Spark and Delta Lake run inside a non-root Docker container.

Command:

```bash
make docker-lakehouse
```

## Result

The job processed the same 1,000 synthetic claims used for the local model demonstration.

| Layer or gate | Rows |
| --- | ---: |
| Bronze claims | 1,000 |
| Validated Silver claims | 1,000 |
| Quarantined claims | 0 |
| Point-in-time Gold feature rows | 1,000 |

Bronze preserves raw inputs. Silver enforces non-negative amounts, timestamp order, and valid policy references. Invalid rows are written to a separate quarantine table rather than silently discarded. Gold adds model-ready features, including historical payment amounts only when the earlier claim had closed by the current claim's report time.

## Issues found during verification

The first run correctly quarantined all records because the explicit Spark schemas omitted two source columns. This made later CSV fields shift into the wrong schema positions. The schemas were corrected to match the source contract. A second issue came from comparing columns by position after a join reordered them; the Silver data is now explicitly restored to source-column order before computing quarantine records.

The successful rerun produced the counts above. This is useful evidence for why strict schemas and quarantine metrics matter: an apparently successful pipeline can otherwise create empty or misleading feature tables.

## Local operational facts

- The image uses Python 3.12 and Java 21.
- Maven packages for Delta are cached in a named Docker volume after the first download.
- Generated Delta data stays under the ignored `data/lakehouse/` directory and is reproducible.
- The inference image was separately verified healthy at `/health/ready`; separating training-only dependencies reduced it to approximately 159 MB.
