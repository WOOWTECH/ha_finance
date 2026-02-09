# Ha Finance Record

A Home Assistant custom component for personal finance tracking. Manage multiple accounts, record transactions, set up recurring plans, and visualize your finances — all from the HA sidebar.

[繁體中文版 README](README_TW.md)

## Features

- **Multi-Account Management** — Create and manage multiple financial accounts, each with its own balance, transactions, and recurring plans.
- **Quick Transaction Recording** — Enter amount + note and press "Confirm Record" to log income or expenses instantly.
- **Recurring Plans** — Schedule automatic transactions (income or expense) on a daily, weekly, monthly, or yearly basis.
- **Sidebar Panel** — A Lit Element–based dashboard in the HA sidebar with transaction history, charts, and account management tabs.
- **Bilingual UI** — English and Traditional Chinese (zh-Hant), auto-detected from your HA language setting.
- **Automation Events** — Fire events on transactions, recurring executions, balance adjustments, and low-balance alerts for use in HA automations.

## Installation

### HACS (Manual Repository)

1. Open HACS in Home Assistant.
2. Go to **Integrations** → three-dot menu → **Custom repositories**.
3. Add `https://github.com/woowtech-ai-coder/ha_finance` as an **Integration**.
4. Search for "Finance Record" and install.
5. Restart Home Assistant.

### Manual

1. Copy the `custom_components/ha_finance/` folder into your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.

## Configuration

1. Go to **Settings** → **Devices & Services** → **Add Integration**.
2. Search for **Finance Record**.
3. Enter an account name, optional account ID, and initial balance.
4. To add more accounts, repeat the process — each config entry creates a separate account.

### Options

After setup, click **Configure** on the integration entry to:

- Add or manage recurring plans (income/expense schedules)
- Edit account settings
- Delete the account

## Entities

Each account creates the following entities:

| Platform | Entity | Description |
|----------|--------|-------------|
| `number` | Balance | Current account balance |
| `number` | Quick Amount | Amount input for quick transactions |
| `text` | Quick Note | Note input for quick transactions |
| `button` | Confirm Record | Press to record the quick transaction |
| `sensor` | Balance Display | Formatted balance sensor |
| `sensor` | Last Transaction | Amount of the most recent transaction |
| `sensor` | Last Note | Note of the most recent transaction |
| `sensor` | Last Time | Timestamp of the most recent transaction |

Each recurring plan adds:

| Platform | Entity | Description |
|----------|--------|-------------|
| `number` | Amount | Plan amount (positive = income, negative = expense) |
| `number` | Execution Day | Day of week/month/year the plan executes |
| `select` | Frequency | Daily / Weekly / Monthly / Yearly |
| `switch` | Active | Enable or disable the plan |
| `sensor` | Next Date | Next scheduled execution date |
| `sensor` | Last Executed | When the plan last ran |

## Events

Use these in automations:

| Event | Description |
|-------|-------------|
| `ha_finance_transaction_added` | Fired when a manual transaction is recorded |
| `ha_finance_recurring_executed` | Fired when a recurring plan executes |
| `ha_finance_balance_adjusted` | Fired when balance is manually adjusted |
| `ha_finance_low_balance` | Fired when balance drops below the configured threshold |

## Sidebar Panel

After adding at least one account, a **Finance Record** panel appears in the HA sidebar. It provides:

- Transaction history with date filtering
- Income/expense charts
- Account overview and management
- Quick transaction entry

## License

This project is provided as-is for personal use.
