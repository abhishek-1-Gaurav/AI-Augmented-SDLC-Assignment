# Data Model: Smart Todo

## Task

| Field | Type | Required | Rules |
|---|---|---:|---|
| ID | positive integer | Yes | Unique across the collection; immutable after creation |
| title | text | Yes | Trimmed; not empty or whitespace-only |
| description | text | Yes | Trimmed; not empty or whitespace-only |
| priority | enum | Yes | Exactly Low, Medium, or High |
| tags | list of text | Yes | Each tag is non-empty; duplicates are rejected or normalized |
| status | enum | Yes | Exactly Pending, In Progress, or Completed |

## Validation Rules

- Creation requires a unique ID, title, description, priority, and tags.
- Creation always initializes status to Pending.
- Update may change title, description, priority, and tags.
- Update MUST NOT accept or expose an ID change.
- Update with no mutable fields or with values identical to the current task is a no-op:
  report success and do not rewrite JSON.
- Status changes use only the dedicated status operation.
- Invalid priority or status values are rejected before storage or state mutation.
- Duplicate IDs are rejected during creation and cannot be introduced through update.
- Missing IDs return a task-not-found domain error.
- Tags are compared exactly and case-insensitively after trimming.
- Multiple filter tags use AND semantics.

## State Transitions

```text
Pending <-> In Progress
Pending <-> Completed
In Progress <-> Completed
```

Every transition among the three statuses is valid. The service MUST reject unknown status
values and nonexistent task IDs.

## Persistence Shape

The JSON collection contains task records. Each record has the Task fields. The storage module
validates both the collection shape and every record. Unknown extra fields may be rejected to
avoid silently losing or misinterpreting data.

## Relationships

- A Task contains a list of Tag values.
- Tag values do not require separate entities.
- The collection maps at most one Task record to each unique ID.
