---
name: human-ai-collaboration
description: Perform human-AI collaboration to finalize optimization. Use after MoA-based optimization stage is completed.
allowed-tools:
  - read
  - web_request
level: 4
inputs:
  topic: string
  moa_based_optimization_result_file: path
  compression: boolean
  user_id: string
outputs:
  result_file: path
  task_id: string
---

# Human-AI Collaboration

## Instructions
- Summarize MoA outputs and extract next optimization steps
- Generate collaboration messages and construct final draft
- Save final outputs for reporting and review

## Examples
- "Finalize with human-AI collaboration for 'battery materials'"

