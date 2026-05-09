# Performance Comparison: v1 vs v2

- Iterations per size (after warm-up): **5**
- Sizes: 200, 1000, 2000, 5000 records (each runs against JSON + TXT pair)
- v1 root: `D:\20260422\.github\skills\log-analysis-pipeline`
- v2 root: `D:\20260422\.github\skills\log-analysis-pipeline-v2`
- Verdict: **v2 wins on every size**

## Wall time (ms)

| Size | v1 min | v1 avg | v1 max | v2 min | v2 avg | v2 max | Speedup (avg) |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 200 | 7.34 | 7.65 | 8.22 | 3.7 | 4.06 | 4.25 | 1.88x |
| 1000 | 34.26 | 35.59 | 36.68 | 16.84 | 17.35 | 18.37 | 2.05x |
| 2000 | 68.53 | 70.03 | 72.32 | 32.21 | 33.01 | 34.56 | 2.12x |
| 5000 | 174.98 | 179.13 | 184.25 | 85.31 | 90.29 | 96.84 | 1.98x |

## Raw samples (ms)

| Size | v1 samples | v2 samples |
|---:|---|---|
| 200 | [7.47, 8.22, 7.34, 7.85, 7.37] | [4.19, 3.97, 3.7, 4.25, 4.18] |
| 1000 | [34.26, 36.07, 36.68, 36.53, 34.4] | [16.98, 17.53, 18.37, 16.84, 17.04] |
| 2000 | [70.13, 68.69, 70.47, 72.32, 68.53] | [34.56, 32.55, 33.08, 32.65, 32.21] |
| 5000 | [175.5, 174.98, 178.67, 182.25, 184.25] | [96.84, 87.79, 90.18, 91.35, 85.31] |
