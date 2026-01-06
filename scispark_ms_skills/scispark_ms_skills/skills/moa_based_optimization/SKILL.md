---
name: moa-based-optimization
description: Run MoA-based optimization with multi-agent review and aggregation. Use after technical optimization stage is completed.
allowed-tools:
  - read
  - web_request
level: 4
inputs:
  topic: string
  technical_optimization_result_file: path
  compression: boolean
  user_id: string
outputs:
  result_file: path
  task_id: string
---

# MoA Based Optimization

## Instructions
- Aggregate multi-agent messages for optimization
- Produce MoA review and iteration summary
- Save MoA outputs for next collaboration stage

## Examples
- "Run MoA optimization for 'index theorem' without compression"

