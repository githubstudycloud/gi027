# Log Analysis Summary Report

## Overview

| Metric | Value |
|---|---|
| Input files | 2 |
| Total records | 4 |
| Total groups | 4 |

## Category Summary

| Issue Category | Issue Subcategory | Root Cause | Count |
|---|---|---|---:|
| Stability | Timeout | Slow downstream service | 1 |
| Stability | Network | Network jitter | 1 |
| Correctness | Signature | Key version mismatch | 1 |
| DataConsistency | Mapping | Missing DTO mapping | 1 |

## Nested Details

### 1. Stability / Timeout / Slow downstream service

| Use Case | Key Evidence | Fix Action | Fix Conclusion | Rerun Conclusion | Source File |
|---|---|---|---|---|---|
| Login retry timeout | P95 latency is 4.2s | Add timeout and retry policy | Mitigated | Passed | sample-input-1.json |

### 2. Stability / Network / Network jitter

| Use Case | Key Evidence | Fix Action | Fix Conclusion | Rerun Conclusion | Source File |
|---|---|---|---|---|---|
| Order query intermittent failure | 3 connection resets | Enable keepalive in connection pool | Fixed | Passed | sample-input-2.txt |

### 3. Correctness / Signature / Key version mismatch

| Use Case | Key Evidence | Fix Action | Fix Conclusion | Rerun Conclusion | Source File |
|---|---|---|---|---|---|
| Payment callback signature mismatch | Gateway and service use different key versions | Align key versions | Fixed | Passed | sample-input-1.json |

### 4. DataConsistency / Mapping / Missing DTO mapping

| Use Case | Key Evidence | Fix Action | Fix Conclusion | Rerun Conclusion | Source File |
|---|---|---|---|---|---|
| Profile update missing fields | Trace comparison shows field not propagated | Add missing mapping and regression tests | Fixed | Passed | sample-input-2.txt |

