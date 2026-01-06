---
name: technical-optimization
description: Optimize the initial idea with technical details and related papers. Use after initial idea stage is completed.
allowed-tools:
  - read
  - web_request
level: 4
inputs:
  topic: string
  initial_idea_result_file: path
  compression: boolean
  user_id: string
outputs:
  result_file: path
  task_id: string
---

# Technical Optimization

## Instructions
- Parse initial idea result for target paper title and abstract
- Search related papers; optionally compress contents
- Generate technical optimization draft and save outputs

## Examples
- "Optimize the idea for 'battery materials' with 2 related papers"

