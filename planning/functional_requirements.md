# Functional requirements

This document summarises what the application must *do*.

## Roles
- **Reader**: can view published (approved) content; can subscribe to publishers and/or journalists.
- **Journalist**: can create and manage their own articles/newsletters.
- **Editor**: can review and approve articles; once approved, subscribers are notified.

## Core features
1. **Authentication**
   - Users can log in and log out.
   - Users have a role (Reader/Editor/Journalist) and are added to a corresponding Django group.

2. **Publishers**
   - A publisher can have multiple editors and journalists.

3. **Articles**
   - Articles have an **approved** flag.
   - Editors can view pending articles and approve them.
   - Readers can view approved articles.

4. **Subscriptions**
   - Readers can subscribe to:
     - publishers
     - journalists
   - Subscriptions determine which articles are returned to the API client and which users receive notifications.

5. **Notifications on approval**
   - When an editor approves an article:
     - the article is emailed to all relevant subscribers (publisher and/or journalist subscribers)
     - the article is posted to an X account via HTTP API (requests)

6. **REST API**
   - A REST endpoint returns the set of articles based on the API client's (reader's) subscriptions.

7. **Automated tests**
   - Unit tests verify the API returns the correct articles for different subscription scenarios.
