# Quotation Lifecycle Design

This document captures the quotation lifecycle direction for `quotation/`.

It documents both:

- the current implemented internal workflow direction
- the future extension path for a later customer-facing status dimension

See also:

- `docs/quotation/quotation.md`

## Goal

Define a quote lifecycle model that works for:

- today's mostly manual owner or operator follow-up
- tomorrow's possible customer-visible or customer-driven quote flow
- consistent lifecycle timestamps
- clear business semantics in admin and future runtime surfaces

## Current Problem

Today one status field is trying to cover more than one concern.

Those concerns are different:

- internal workflow state for the owner or operator
- external commercial state of the quote in relation to the customer

If both concerns stay mixed in one field, the model becomes ambiguous:

- some states feel too advanced for today's manual flow
- some future customer-driven states do not map cleanly to internal team work
- timestamps become hard to interpret consistently

## Current Direction

The current preferred direction is to keep the quote lifecycle split into two layers:

- the implemented internal `workflow_status`
- a possible future `customer_status` extension when the product supports a real customer-facing quote flow

### Implemented Step 1: Internal Workflow First

The current implementation focuses only on the internal team workflow.

Candidate field name:

- `workflow_status`

Current preferred values:

- `draft`
- `requested`
- `in_progress`
- `completed`
- `cancelled`

This keeps the current implementation aligned with today's real flow:

- the quote is requested
- the owner or operator works it manually
- the final closure may happen outside the system in a person-to-person process
- the owner can explicitly complete or cancel the internal workflow from owner admin actions

### Step 2: Customer-Facing Status Later

If the project later supports a more explicit customer-facing or customer-driven quote flow, add a second field rather than overloading `workflow_status`.

Candidate future field name:

- `customer_status`

Candidate future values:

- `pending`
- `sent`
- `approved`
- `rejected`
- `expired`

This future field should answer:

- what happened with the quote from the customer-facing commercial side?

## Why This Two-Step Direction Is Preferred

### Today

The owner or operator can manage internal progress without pretending that the customer is interacting with the system directly.

Example:

- `workflow_status = in_progress`

### Tomorrow

If the customer later interacts with the system, a dedicated commercial state can be added without breaking the internal workflow semantics.

Example:

- `workflow_status = in_progress`
- `customer_status = sent`

## Timestamp Direction

### Current Implementation

With the current `workflow_status` implementation, the minimal timestamp pair is:

- `requested_at`
- `resolved_at`

### Future Extension

If a future `customer_status` is introduced, the commercial timestamp set can expand to:

- `sent_at`
- `answered_at`

## Example Scenarios

### Scenario A: Manual P2P Follow-Up

The customer requests a quote, and the team handles the rest outside the system.

Possible progression:

- `workflow_status: draft -> requested -> in_progress -> completed`

### Scenario B: Team Works The Quote But The Customer Never Replies

Possible progression:

- `workflow_status: draft -> requested -> in_progress -> cancelled`
- future `customer_status: pending -> expired`

### Scenario C: Future Customer-Visible Quote Flow

Possible progression:

- `workflow_status: requested -> in_progress`
- future `customer_status: pending -> sent -> approved`

## Expansion Guidance

When the next lifecycle expansion starts:

1. keep `workflow_status` as the internal lifecycle dimension
2. derive only the timestamps that belong clearly to that internal workflow
3. avoid introducing customer-facing states until the product really supports them
4. add `customer_status` later as a second dimension instead of expanding `workflow_status` beyond its internal meaning

## Current Implementation Summary

The current implementation aims for the smallest useful redesign.

### Fields

- keep `workflow_status` as the internal lifecycle field
- do not add `customer_status` yet

### Preferred Values

- `draft`
- `requested`
- `in_progress`
- `completed`
- `cancelled`

### Preferred Timestamps

- keep `requested_at`
- add or derive `resolved_at`
- do not derive customer-facing timestamps yet

### Rationale

This implemented step:

- matches today's real manual owner or operator workflow
- avoids pretending that the customer is already participating in the system
- centralizes terminal owner actions behind a quotation service so later notifications or events can be attached there
- keeps the future extension path open without forcing that complexity into the first redesign

## Open Questions

1. Should `resolved_at` remain the single terminal timestamp for both `completed` and `cancelled`?
2. Should `requested_at` be the first timestamp derived automatically from `workflow_status` transitions?
3. Should `resolved_at` be first-write only once the workflow reaches a terminal state?
4. At what product milestone would a dedicated `customer_status` become worth the added complexity?
