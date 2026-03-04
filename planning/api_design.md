# REST API design

## Goal
Expose a REST endpoint that returns articles relevant to an API client (reader), based on the reader's subscriptions.

## Authentication
- The API endpoint requires an authenticated user.
- The authenticated user is treated as the “API client”.

## Endpoint
- `GET /api/articles/`

## Business rule
Return approved articles where:
- the article's publisher is in the reader's subscribed publishers, OR
- the article's author (journalist) is in the reader's subscribed journalists

## Example response (JSON)
```json
[
  {
    "id": 123,
    "title": "Example title",
    "content": "…",
    "approved": true,
    "publisher": {"id": 1, "name": "Publisher A"},
    "author": {"id": 9, "username": "journalist1"}
  }
]
```

## Error cases
- 401 if unauthenticated (handled by DRF authentication/permissions).
