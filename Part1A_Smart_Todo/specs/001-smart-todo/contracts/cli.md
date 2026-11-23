# CLI Contract

This contract defines the proposed beginner-friendly implementation interface. It does not
change the product requirements. All commands use `python3 -m smart_todo`; positive integer
IDs are the technical decision recommended for implementation.

## Proposed Commands

### Create

`python3 -m smart_todo create --id <positive-integer> --title <title> --description <text> --priority <priority>
--tags <tag1,tag2>`

- Creates with Pending status.
- Rejects duplicate IDs, missing fields, invalid priorities, or invalid tags.

### List

`python3 -m smart_todo list`

- Lists every task.
- May return an empty result with a clear message.

### Get

`python3 -m smart_todo get --id <positive-integer>`

- Displays one complete task.
- Returns task-not-found if the ID is absent.

### Update

`python3 -m smart_todo update --id <positive-integer> [--title <title>] [--description <text>]
[--priority <priority>] [--tags <tag1,tag2>]`

- Updates only supplied fields.
- ID is not accepted as an update field.
- No supplied field or only identical values is a successful no-op and does not rewrite JSON.
- Rejects missing tasks and invalid values.

### Delete

`python3 -m smart_todo delete --id <positive-integer>`

- Deletes the existing task.
- Returns task-not-found if the ID is absent.

### Filter

`python3 -m smart_todo filter --tags <tag1,tag2>`

- Matches tasks containing every requested tag.
- Tag matching is exact and case-insensitive.
- Returns a clear no-matches message for an empty result.

### Sort

`python3 -m smart_todo sort --priority`

- Returns tasks ordered High, Medium, Low.
- Equal priorities retain their existing relative order.

### Change Status

`python3 -m smart_todo status --id <positive-integer> --status <status>`

- Accepts only Pending, In Progress, or Completed.
- Allows every transition among the three statuses.

## Error Contract

- Print clear human-readable errors to standard error.
- Return a failing process status for invalid input or storage failures.
- Do not print secrets or raw unredacted stored-data contents.
- Task-not-found, duplicate-ID, invalid-value, and storage errors use distinct messages.
