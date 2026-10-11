# Feature 001: Order history

## User story
As a customer I can view my past orders so that I can reorder items.

## Acceptance scenarios
1. Given I am a customer with orders, when I request my order history, then I see my orders newest first, 20 per page.
2. Given I have no orders, when I request my order history, then I get an empty page, not an error.
3. Given another customer's id, when I request their history, then I get 403.

## Requirements
- FR-1: `GET /api/customers/{id}/orders?page=` returns a page of order summaries.
- FR-2: Only the owner may read the history.
