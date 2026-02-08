---
id: 001
title: Update gitignore for todobot secrets
stage: general
date: 2026-02-08
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: Admin
command: none
labels: ["security", "gitignore", "secrets", "todobot"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .gitignore
tests:
  - none
---

## Prompt

update .gitignore because we have some secret data file in todobot folder

## Response snapshot

Updated .gitignore to exclude sensitive files in the todobot folder:
- todobot/values-local.yaml (contains API keys, database passwords, auth secrets)
- todobot/secrets/ directory
- todobot/*.key, *.pem, *.p12 (certificate files)
- todobot/*secret*, *credential* (any secret/credential files)

Verified that todobot/values-local.yaml is not currently tracked by git, preventing accidental exposure of:
- OpenAI API key
- Database password
- Better Auth secret

## Outcome

- ✅ Impact: Protected sensitive configuration data from being committed to version control
- 🧪 Tests: Verified values-local.yaml is not in git index
- 📁 Files: Modified .gitignore with 7 new exclusion patterns for todobot secrets
- 🔁 Next prompts: Consider creating values-local.yaml.example template file
- 🧠 Reflection: Successfully identified and protected actual API keys and credentials in values-local.yaml

## Evaluation notes (flywheel)

- Failure modes observed: None - secret file was never committed
- Graders run and results (PASS/FAIL): PASS - git ls-files confirms exclusion
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Create example template file for developers
