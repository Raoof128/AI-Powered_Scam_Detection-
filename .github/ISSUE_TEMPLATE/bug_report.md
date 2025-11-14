---
name: Bug Report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

## Bug Description
A clear and concise description of what the bug is.

## To Reproduce
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior
A clear and concise description of what you expected to happen.

## Actual Behavior
What actually happened.

## Screenshots
If applicable, add screenshots to help explain your problem.

## Environment
- **OS**: [e.g., macOS, Ubuntu 22.04, Windows 11]
- **Python Version**: [e.g., 3.11.5]
- **Platform Version**: [e.g., 0.1.0]
- **Installation Method**: [e.g., Docker, pip install, from source]
- **Docker Version** (if applicable): [e.g., 24.0.0]

## API Request (if applicable)
```bash
# Paste the curl command or API request that caused the issue
curl -X POST "http://localhost:8000/api/v1/detect" \
  -H "Content-Type: application/json" \
  -d '{"message": "...", "message_type": "email"}'
```

## Error Messages
```
Paste any error messages, stack traces, or logs here
```

## Additional Context
Add any other context about the problem here.

## Possible Solution
If you have suggestions on how to fix the bug, please describe them here.

## Checklist
- [ ] I have searched existing issues to ensure this bug hasn't been reported
- [ ] I have included all relevant information above
- [ ] I have tested with the latest version
- [ ] I can reproduce this issue consistently
