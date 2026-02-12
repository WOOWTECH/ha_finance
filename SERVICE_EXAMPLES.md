# ha_finance Service Examples

All 6 actions registered under the `ha_finance` domain. Call them from **Developer Tools > Actions** or in automations.

> Replace `my_account` with your actual account ID (set during config flow).

---

## 1. Add Transaction

Add a financial transaction to an account. Positive amounts are income, negative are expenses.

```yaml
action: ha_finance.add_transaction
data:
  account_id: "my_account"
  amount: -350.50
  note: "Grocery shopping"
```

| Field | Required | Description |
|-------|----------|-------------|
| `account_id` | Yes | The account ID |
| `amount` | Yes | Transaction amount (-999999999 to 999999999) |
| `note` | No | Optional note (defaults to empty string) |

---

## 2. Adjust Balance

Set an account balance to an exact value. Creates an adjustment transaction for the delta.

```yaml
action: ha_finance.adjust_balance
data:
  account_id: "my_account"
  new_balance: 50000.00
```

| Field | Required | Description |
|-------|----------|-------------|
| `account_id` | Yes | The account ID |
| `new_balance` | Yes | The new balance value |

---

## 3. Add Recurring Plan

Create a recurring financial plan (e.g. salary, rent, subscription).

```yaml
action: ha_finance.add_plan
data:
  account_id: "my_account"
  title: "Monthly Salary"
  amount: 50000
  frequency: "monthly"
  day: 1
  month: 1
  active: true
```

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `account_id` | Yes | | The account ID |
| `title` | Yes | | Plan name |
| `amount` | Yes | | Amount per occurrence |
| `frequency` | Yes | | `daily`, `weekly`, `monthly`, or `yearly` |
| `day` | Yes | | Execution day (1-7 for weekly, 1-28 for monthly/yearly) |
| `month` | No | `1` | Execution month for yearly frequency (1-12) |
| `active` | No | `true` | Whether the plan is active |

---

## 4. Update Recurring Plan

Update one or more fields of an existing plan. Only provided fields are changed.

```yaml
action: ha_finance.update_plan
data:
  account_id: "my_account"
  plan_id: "a1b2c3d4"
  amount: 55000
  title: "Updated Salary"
```

| Field | Required | Description |
|-------|----------|-------------|
| `account_id` | Yes | The account ID |
| `plan_id` | Yes | The plan ID (8-char hex, returned when created) |
| `title` | No | New plan name |
| `amount` | No | New amount |
| `frequency` | No | New frequency |
| `day` | No | New execution day |
| `month` | No | New execution month |
| `active` | No | New active state |

---

## 5. Delete Recurring Plan

Permanently remove a recurring plan from an account.

```yaml
action: ha_finance.delete_plan
data:
  account_id: "my_account"
  plan_id: "a1b2c3d4"
```

| Field | Required | Description |
|-------|----------|-------------|
| `account_id` | Yes | The account ID |
| `plan_id` | Yes | The plan ID to delete |

---

## 6. Set Plan Active State

Enable or disable a recurring plan without deleting it.

```yaml
action: ha_finance.set_plan_active
data:
  account_id: "my_account"
  plan_id: "a1b2c3d4"
  active: false
```

| Field | Required | Description |
|-------|----------|-------------|
| `account_id` | Yes | The account ID |
| `plan_id` | Yes | The plan ID |
| `active` | Yes | `true` to enable, `false` to disable |
