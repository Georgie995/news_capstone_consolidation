# Database design and normalisation

## Entities (tables)
- **CustomUser**
  - Extends Django's AbstractUser with a `role` field.
  - Reader subscriptions:
    - Many-to-many to Publisher (`subscribed_publishers`)
    - Many-to-many to CustomUser for journalists (`subscribed_journalists`)
- **Publisher**
  - Has many editors and journalists (relationships implemented via user fields / relations).
- **Article**
  - Belongs to an author (journalist user)
  - Optionally belongs to a publisher
  - Has an `approved` flag for editorial workflow
- **Newsletter**
  - Similar relationship pattern to Article (author/publisher), depending on implementation.

## Normalisation notes (high level)
- Publisher data is stored in its own table (no repeated publisher names on articles beyond a foreign key).
- Users are stored once in CustomUser; relationships are represented by foreign keys/many-to-many tables.
- Subscriptions are modelled as many-to-many relationships, avoiding repeated lists/strings in a single field.

## Relationship summary
- Publisher 1—* Article (via FK on Article)
- Journalist 1—* Article (via FK on Article.author)
- Reader *—* Publisher (subscriptions)
- Reader *—* Journalist (subscriptions)
