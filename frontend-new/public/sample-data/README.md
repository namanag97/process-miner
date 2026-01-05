# Sample Order-to-Cash Event Log

A sample event log designed for testing **all** process mining analysis types.

## Dataset Overview

| Metric | Value |
|--------|-------|
| Cases | 25 |
| Events | 200+ |
| Activities | 10 |
| Resources | 8 |
| Duration | ~2 weeks |

## Process Variants

The dataset includes 5 different process execution patterns:

| Variant | % of Cases | Description |
|---------|------------|-------------|
| **Happy Path** | 40% | Full order flow: Receive → Validate → Credit → Approve → Ship → Deliver → Pay → Close |
| **Rejection** | 20% | Order rejected after credit check |
| **Fast-Track** | 20% | Skips validation/credit (trusted customers) |
| **Rework** | 12% | Order needs re-validation (loops back) |
| **Delayed Payment** | 8% | Multiple payment attempts |

## Activities

1. Order Received
2. Validate Order
3. Credit Check
4. Order Approved
5. Order Rejected
6. Prepare Shipment
7. Ship Order
8. Deliver Order
9. Receive Payment
10. Close Case

## Resources

8 employees with different roles:
- Sarah Chen, Mike Johnson, Emma Williams, David Brown
- Lisa Garcia, James Wilson, Maria Martinez, Robert Taylor

## Columns

| Column | Type | Description |
|--------|------|-------------|
| case_id | string | Unique case identifier (CASE-XXXX) |
| activity | string | Activity name |
| timestamp | datetime | When the activity occurred |
| resource | string | Who performed the activity |
| cost | number | Activity cost in dollars |

## Suitable Analyses

This dataset supports **all** process mining analysis types:

✅ **Discovery** - Multiple paths, loops, and parallelism  
✅ **Variants** - 5 distinct process variants  
✅ **Statistics** - Rich metrics with timestamps and costs  
✅ **Performance** - Variable durations reveal bottlenecks  
✅ **Organizational** - 8 resources with handovers  
✅ **Conformance** - Compare against ideal model  
✅ **Declarative** - Many constraint patterns present  

## Usage

Upload this file to the Process Mining platform:
1. Go to Upload Wizard
2. Select this CSV file
3. Map columns: `case_id`, `activity`, `timestamp`, `resource`
4. Run any analysis in the Showcase
