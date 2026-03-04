# Non-functional requirements

This document describes system-wide qualities and constraints.

## Code quality
- Code is readable and modular (separate concerns across modules/apps).
- Defensive coding and validation are used to reduce runtime errors.
- Code follows PEP 8 conventions where practical.

## Security / access control
- Only authenticated users can access protected pages and API endpoints.
- Permissions are role-based:
  - Reader: view-only
  - Journalist: create/view/update/delete
  - Editor: view/update/delete + approve

## Reliability
- The system should fail gracefully for email/X API failures (do not crash approval flow).

## Maintainability
- Docstrings exist for classes, functions, and methods to support later documentation tasks.

## Portability
- Dependencies are listed in requirements.txt.
- Installation and run instructions are provided in README.md.
