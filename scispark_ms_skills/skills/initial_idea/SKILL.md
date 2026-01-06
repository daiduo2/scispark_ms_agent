---
name: initial-idea
description: Generate initial idea draft from arXiv facts and hypotheses. Use when the user provides a scientific topic to start research workflow.
allowed-tools:
  - read
  - web_request
level: 4
inputs:
  topic: string
  num: integer
  compression: boolean
  user_id: string
outputs:
  result_file: path
  task_id: string
---

# Initial Idea

## Instructions
- Search related papers for the given topic
- Extract factual information and generate hypotheses
- Compose an initial idea draft and save outputs

## Examples
- "Start initial idea for 'index theorem' with 3 papers, no compression"

