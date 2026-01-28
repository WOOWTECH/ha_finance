import {
  LitElement,
  html,
  css,
  unsafeCSS,
} from "https://unpkg.com/lit-element@3.3.3/lit-element.js?module";

// Inlined shared styles for HA panel compatibility - Dark/Light theme aware
const sharedStylesLit = `
  /* TOP BAR - follows HA dark/light mode */
  .top-bar {
    display: flex;
    align-items: center;
    height: 56px;
    padding: 0 16px;
    background: var(--app-header-background-color, var(--primary-background-color));
    color: var(--app-header-text-color, var(--primary-text-color));
    border-bottom: 1px solid var(--divider-color);
    position: sticky;
    top: 0;
    z-index: 100;
    gap: 12px;
    margin: -16px -16px 16px -16px;
  }
  .top-bar-sidebar-btn {
    width: 40px;
    height: 40px;
    border: none;
    background: transparent;
    color: var(--app-header-text-color, var(--primary-text-color));
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: background 0.2s;
    flex-shrink: 0;
  }
  .top-bar-sidebar-btn:hover { background: var(--secondary-background-color); }
  .top-bar-sidebar-btn svg { width: 24px; height: 24px; }
  .top-bar-title {
    flex: 1;
    font-size: 20px;
    font-weight: 500;
    margin: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .top-bar-actions { display: flex; align-items: center; gap: 4px; flex-shrink: 0; }
  .top-bar-action-btn {
    width: 40px;
    height: 40px;
    border: none;
    background: transparent;
    color: var(--app-header-text-color, var(--primary-text-color));
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: background 0.2s;
  }
  .top-bar-action-btn:hover { background: var(--secondary-background-color); }
  .top-bar-action-btn svg { width: 24px; height: 24px; }

  /* SEARCH ROW - standalone row */
  .search-row {
    display: flex;
    align-items: center;
    height: 48px;
    padding: 0 16px;
    background: var(--primary-background-color);
    border-bottom: 1px solid var(--divider-color);
    margin: 0 -16px 16px -16px;
    gap: 8px;
  }
  .search-row-input-wrapper {
    flex: 1;
    display: flex;
    align-items: center;
    background: var(--card-background-color);
    border: 1px solid var(--divider-color);
    border-radius: 8px;
    padding: 0 12px;
    height: 36px;
    transition: border-color 0.2s, box-shadow 0.2s;
  }
  .search-row-input-wrapper:focus-within {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 2px rgba(var(--rgb-primary-color, 3, 169, 244), 0.2);
  }
  .search-row-icon {
    width: 20px;
    height: 20px;
    color: var(--secondary-text-color);
    flex-shrink: 0;
    margin-right: 8px;
  }
  .search-row-input {
    flex: 1;
    border: none;
    background: transparent;
    font-size: 14px;
    color: var(--primary-text-color);
    outline: none;
    height: 100%;
  }
  .search-row-input::placeholder { color: var(--secondary-text-color); }

  /* ACCOUNT SWITCHER - Health Record style member cards */
  .account-switcher-row {
    display: flex;
    align-items: center;
    padding: 0 16px 16px 16px;
    gap: 12px;
    flex-wrap: wrap;
  }
  .account-card {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    background: var(--card-background-color);
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s;
    border: 2px solid transparent;
    box-shadow: var(--ha-card-box-shadow, 0 2px 2px rgba(0,0,0,0.1));
    min-width: 140px;
  }
  .account-card:hover {
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    transform: translateY(-2px);
  }
  .account-card.active {
    border-color: var(--primary-color);
    background: var(--primary-color);
  }
  .account-card.active .account-card-name,
  .account-card.active .account-card-balance {
    color: var(--text-primary-color, white);
  }
  .account-card-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: var(--primary-color);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 18px;
    font-weight: 500;
  }
  .account-card.active .account-card-avatar {
    background: rgba(255,255,255,0.2);
  }
  .account-card-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
  .account-card-name {
    font-size: 14px;
    font-weight: 500;
    color: var(--primary-text-color);
  }
  .account-card-balance {
    font-size: 12px;
    color: var(--secondary-text-color);
  }
  .add-account-card {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 12px 20px;
    background: var(--secondary-background-color);
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s;
    border: 2px dashed var(--divider-color);
    color: var(--secondary-text-color);
    font-size: 14px;
    min-width: 120px;
  }
  .add-account-card:hover {
    border-color: var(--primary-color);
    color: var(--primary-color);
    background: var(--card-background-color);
  }
  .add-account-card svg {
    width: 20px;
    height: 20px;
  }
`;

// Translation helper
const commonTranslations = {
  en: { menu: 'Menu', search: 'Search...', add: 'Add', more_actions: 'More actions' },
  'zh-Hant': { menu: '選單', search: '搜尋...', add: '新增', more_actions: '更多操作' },
  'zh-Hans': { menu: '菜单', search: '搜索...', add: '添加', more_actions: '更多操作' },
};
function getCommonTranslation(key, lang = 'en') {
  const langKey = lang?.startsWith('zh-TW') || lang?.startsWith('zh-HK') ? 'zh-Hant' :
                  lang?.startsWith('zh') ? 'zh-Hans' : 'en';
  return commonTranslations[langKey]?.[key] || commonTranslations['en'][key] || key;
}

class HaFinancePanel extends LitElement {
  static get properties() {
    return {
      hass: { type: Object },
      narrow: { type: Boolean },
      panel: { type: Object },
      _accounts: { type: Array },
      _selectedAccountId: { type: String },
      _selectedAccount: { type: Object },
      _activeTab: { type: String },
      _loading: { type: Boolean },
      _error: { type: String },
      _chartData: { type: Array },
      _filterType: { type: String },
      _filterDateStart: { type: String },
      _filterDateEnd: { type: String },
      _showTransactionForm: { type: Boolean },
      _showPlanForm: { type: Boolean },
      _editingTransaction: { type: Object },
      _editingPlan: { type: Object },
      _chartError: { type: String },
      _showAddAccountForm: { type: Boolean },
      _showEditAccountForm: { type: Boolean },
      _showDeleteAccountForm: { type: Boolean },
      _showAccountMenu: { type: Boolean },
      _deleteConfirmText: { type: String },
      _searchQuery: { type: String },
      _showMoreMenu: { type: Boolean },
      _allRecordsFilterDateStart: { type: String },
      _allRecordsFilterDateEnd: { type: String },
      _showBalanceAdjustForm: { type: Boolean },
      _editingAccountNotes: { type: String },
    };
  }

  static get styles() {
    return css`
      ${unsafeCSS(sharedStylesLit)}

      :host {
        display: block;
        padding: 16px;
        background: var(--primary-background-color);
        min-height: 100vh;
        box-sizing: border-box;
      }

      .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
        flex-wrap: wrap;
        gap: 8px;
      }

      h1 {
        margin: 0;
        font-size: 24px;
        color: var(--primary-text-color);
      }

      .account-controls {
        display: flex;
        align-items: center;
        gap: 8px;
      }

      .account-selector {
        min-width: 200px;
      }

      .account-selector select {
        width: 100%;
        padding: 8px 12px;
        font-size: 14px;
        border: 1px solid var(--divider-color);
        border-radius: 4px;
        background: var(--card-background-color);
        color: var(--primary-text-color);
      }

      .icon-btn {
        width: 36px;
        height: 36px;
        border: none;
        border-radius: 50%;
        background: var(--secondary-background-color);
        color: var(--primary-text-color);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background 0.2s;
        position: relative;
      }

      .icon-btn:hover {
        background: var(--divider-color);
      }

      .icon-btn svg {
        width: 20px;
        height: 20px;
      }

      .account-menu {
        position: absolute;
        top: 100%;
        right: 0;
        margin-top: 4px;
        background: var(--card-background-color);
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 100;
        min-width: 160px;
        overflow: hidden;
      }

      .account-menu-item {
        padding: 12px 16px;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 8px;
        color: var(--primary-text-color);
        transition: background 0.2s;
      }

      .account-menu-item:hover {
        background: var(--secondary-background-color);
      }

      .account-menu-item.danger {
        color: var(--error-color, #f44336);
      }

      .menu-backdrop {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 99;
      }

      .warning-text {
        color: var(--warning-color, #ff9800);
        font-size: 14px;
        margin-bottom: 16px;
        padding: 12px;
        background: rgba(255, 152, 0, 0.1);
        border-radius: 4px;
      }

      .confirm-input {
        width: 100%;
        padding: 8px 12px;
        font-size: 14px;
        border: 1px solid var(--divider-color);
        border-radius: 4px;
        background: var(--card-background-color);
        color: var(--primary-text-color);
        box-sizing: border-box;
        margin-top: 8px;
      }

      .btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }

      .balance-card {
        background: var(--card-background-color);
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: var(--ha-card-box-shadow, 0 2px 2px rgba(0,0,0,0.1));
      }

      .balance-amount {
        font-size: 32px;
        font-weight: bold;
        color: var(--primary-text-color);
      }

      .balance-label {
        font-size: 14px;
        color: var(--secondary-text-color);
        margin-bottom: 4px;
      }

      .last-transaction {
        font-size: 14px;
        color: var(--secondary-text-color);
        margin-top: 8px;
      }

      .tabs {
        display: flex;
        gap: 4px;
        margin-bottom: 16px;
        border-bottom: 1px solid var(--divider-color);
      }

      .tab {
        padding: 12px 16px;
        cursor: pointer;
        border: none;
        background: none;
        color: var(--secondary-text-color);
        font-size: 14px;
        border-bottom: 2px solid transparent;
        transition: all 0.2s;
      }

      .tab:hover {
        color: var(--primary-text-color);
      }

      .tab.active {
        color: var(--primary-color);
        border-bottom-color: var(--primary-color);
      }

      .content-card {
        background: var(--card-background-color);
        border-radius: 8px;
        padding: 16px;
        box-shadow: var(--ha-card-box-shadow, 0 2px 2px rgba(0,0,0,0.1));
      }

      .filter-bar {
        display: flex;
        gap: 12px;
        margin-bottom: 16px;
        flex-wrap: wrap;
        align-items: center;
      }

      .filter-bar input,
      .filter-bar select {
        padding: 8px 12px;
        font-size: 14px;
        border: 1px solid var(--divider-color);
        border-radius: 4px;
        background: var(--card-background-color);
        color: var(--primary-text-color);
        min-width: 0;
      }

      .filter-bar label {
        font-size: 14px;
        color: var(--secondary-text-color);
      }

      .filter-bar .date-range {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
      }

      .filter-bar .date-range input[type="date"] {
        flex: 1;
        min-width: 120px;
        max-width: 150px;
      }

      .filter-bar .date-separator {
        color: var(--secondary-text-color);
        flex-shrink: 0;
      }

      table {
        width: 100%;
        border-collapse: collapse;
      }

      th, td {
        padding: 12px;
        text-align: left;
        border-bottom: 1px solid var(--divider-color);
      }

      th {
        font-weight: 500;
        color: var(--secondary-text-color);
        font-size: 12px;
        text-transform: uppercase;
      }

      td {
        color: var(--primary-text-color);
      }

      .amount-positive {
        color: var(--success-color, #4caf50);
      }

      .amount-negative {
        color: var(--error-color, #f44336);
      }

      .btn {
        padding: 8px 16px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
        transition: opacity 0.2s;
      }

      .btn:hover {
        opacity: 0.8;
      }

      .btn-primary {
        background: var(--primary-color);
        color: var(--text-primary-color, white);
      }

      .btn-secondary {
        background: var(--secondary-background-color);
        color: var(--primary-text-color);
      }

      .btn-danger {
        background: var(--error-color, #f44336);
        color: white;
      }

      .btn-small {
        padding: 4px 8px;
        font-size: 12px;
      }

      .actions {
        display: flex;
        gap: 8px;
      }

      .add-button {
        margin-top: 16px;
      }

      .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
      }

      .modal {
        background: var(--card-background-color);
        border-radius: 8px;
        padding: 24px;
        min-width: 300px;
        max-width: 90%;
        max-height: 90vh;
        overflow-y: auto;
      }

      .modal h2 {
        margin: 0 0 16px 0;
        color: var(--primary-text-color);
      }

      .form-group {
        margin-bottom: 16px;
      }

      .form-group label {
        display: block;
        margin-bottom: 4px;
        font-size: 14px;
        color: var(--secondary-text-color);
      }

      .form-group input,
      .form-group select {
        width: 100%;
        padding: 8px 12px;
        font-size: 14px;
        border: 1px solid var(--divider-color);
        border-radius: 4px;
        background: var(--card-background-color);
        color: var(--primary-text-color);
        box-sizing: border-box;
      }

      .form-actions {
        display: flex;
        gap: 8px;
        justify-content: flex-end;
        margin-top: 24px;
      }

      .plan-card {
        background: var(--secondary-background-color);
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
      }

      .plan-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
      }

      .plan-title {
        font-weight: 500;
        color: var(--primary-text-color);
      }

      .plan-details {
        font-size: 14px;
        color: var(--secondary-text-color);
      }

      .plan-amount {
        font-size: 18px;
        font-weight: bold;
      }

      .plan-inactive {
        opacity: 0.5;
      }

      .chart-container {
        width: 100%;
        height: 300px;
        position: relative;
      }

      .chart-bar-group {
        display: flex;
        flex-direction: column;
        align-items: center;
        flex: 1;
      }

      .chart-bars {
        display: flex;
        align-items: flex-end;
        gap: 4px;
        height: 200px;
      }

      .chart-bar {
        width: 30px;
        min-height: 2px;
        transition: height 0.3s;
      }

      .chart-bar.income {
        background: var(--success-color, #4caf50);
      }

      .chart-bar.expense {
        background: var(--error-color, #f44336);
      }

      .chart-label {
        font-size: 12px;
        color: var(--secondary-text-color);
        margin-top: 8px;
      }

      .chart-legend {
        display: flex;
        gap: 24px;
        justify-content: center;
        margin-top: 16px;
      }

      .legend-item {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;
        color: var(--secondary-text-color);
      }

      .legend-color {
        width: 16px;
        height: 16px;
        border-radius: 4px;
      }

      .legend-color.income {
        background: var(--success-color, #4caf50);
      }

      .legend-color.expense {
        background: var(--error-color, #f44336);
      }

      .loading {
        text-align: center;
        padding: 32px;
        color: var(--secondary-text-color);
      }

      .error {
        background: var(--error-color, #f44336);
        color: white;
        padding: 12px;
        border-radius: 4px;
        margin-bottom: 16px;
      }

      .empty-state {
        text-align: center;
        padding: 32px;
        color: var(--secondary-text-color);
      }

      /* Type badges for combined records */
      .type-badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 500;
        background: var(--secondary-background-color);
        color: var(--secondary-text-color);
      }
      .type-badge.plan_summary {
        background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.15);
        color: var(--primary-color);
      }
      .plan-row {
        background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.05);
      }

      /* Account Management Section */
      .account-management-section {
        display: flex;
        flex-direction: column;
        gap: 20px;
      }

      .account-info-card {
        background: var(--secondary-background-color);
        border-radius: 12px;
        padding: 20px;
      }

      .account-info-header {
        display: flex;
        align-items: center;
        gap: 16px;
      }

      .account-avatar-large {
        width: 64px;
        height: 64px;
        border-radius: 50%;
        background: var(--primary-color);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 28px;
        font-weight: 500;
        flex-shrink: 0;
      }

      .account-info-details {
        flex: 1;
      }

      .account-name-display {
        margin: 0 0 4px 0;
        font-size: 20px;
        color: var(--primary-text-color);
      }

      .account-balance-display {
        display: flex;
        align-items: center;
        gap: 8px;
      }

      .balance-label-small {
        font-size: 14px;
        color: var(--secondary-text-color);
      }

      .balance-value {
        font-size: 18px;
        font-weight: 600;
      }

      .account-section {
        background: var(--card-background-color);
        border-radius: 8px;
        padding: 16px;
        border: 1px solid var(--divider-color);
      }

      .section-title {
        margin: 0 0 12px 0;
        font-size: 16px;
        font-weight: 500;
        color: var(--primary-text-color);
      }

      .section-title.danger {
        color: var(--error-color, #f44336);
      }

      .section-description {
        font-size: 14px;
        color: var(--secondary-text-color);
        margin: 0 0 12px 0;
      }

      .warning-text-inline {
        color: var(--warning-color, #ff9800);
        background: rgba(255, 152, 0, 0.1);
        padding: 8px 12px;
        border-radius: 4px;
      }

      .danger-section {
        border-color: rgba(244, 67, 54, 0.3);
      }

      .account-notes-input {
        width: 100%;
        min-height: 100px;
        padding: 12px;
        font-size: 14px;
        border: 1px solid var(--divider-color);
        border-radius: 8px;
        background: var(--card-background-color);
        color: var(--primary-text-color);
        resize: vertical;
        box-sizing: border-box;
        margin-bottom: 12px;
        font-family: inherit;
      }

      .account-notes-input:focus {
        outline: none;
        border-color: var(--primary-color);
      }

      .current-balance-display {
        font-size: 24px;
        font-weight: 600;
        padding: 8px 0;
      }

      .form-hint {
        display: block;
        font-size: 12px;
        color: var(--secondary-text-color);
        margin-top: 4px;
      }

      @media (max-width: 600px) {
        :host {
          padding: 8px;
        }

        .header {
          flex-direction: column;
          align-items: stretch;
        }

        .filter-bar {
          flex-direction: column;
          align-items: stretch;
          gap: 8px;
        }

        .filter-bar input,
        .filter-bar select {
          width: 100%;
          box-sizing: border-box;
        }

        .filter-bar .filter-type-row {
          display: flex;
          gap: 8px;
          align-items: center;
        }

        .filter-bar .filter-type-row label {
          white-space: nowrap;
          flex-shrink: 0;
        }

        .filter-bar .filter-type-row select {
          flex: 1;
        }

        .filter-bar .date-range {
          display: flex;
          gap: 8px;
          align-items: center;
          width: 100%;
        }

        .filter-bar .date-range input[type="date"] {
          flex: 1;
          min-width: 0;
          max-width: none;
        }

        .filter-bar .date-separator {
          flex-shrink: 0;
        }

        table {
          font-size: 14px;
        }

        th, td {
          padding: 8px;
        }

        /* RDA mobile layout */
        .account-switcher-row {
          padding: 0 8px 16px 8px;
          overflow-x: auto;
          flex-wrap: nowrap;
          -webkit-overflow-scrolling: touch;
        }

        .account-card {
          min-width: 130px;
          flex-shrink: 0;
          padding: 10px 14px;
        }

        .account-card-avatar {
          width: 36px;
          height: 36px;
          font-size: 16px;
        }

        .add-account-card {
          min-width: 100px;
          flex-shrink: 0;
          padding: 10px 14px;
        }

        .tabs {
          overflow-x: auto;
          -webkit-overflow-scrolling: touch;
          flex-wrap: nowrap;
        }

        .tab {
          white-space: nowrap;
          flex-shrink: 0;
        }

        .balance-card {
          padding: 12px;
        }

        .balance-amount {
          font-size: 28px;
        }

        .content-card {
          padding: 12px;
        }

        .top-bar {
          margin: -8px -8px 8px -8px;
        }

        .search-row {
          margin: 0 -8px 8px -8px;
        }
      }
    `;
  }

  constructor() {
    super();
    this._accounts = [];
    this._selectedAccountId = "";
    this._selectedAccount = null;
    this._activeTab = "all_records";
    this._loading = true;
    this._error = "";
    this._chartData = [];
    this._filterType = "all";
    this._filterDateStart = "";
    this._filterDateEnd = "";
    this._showTransactionForm = false;
    this._showPlanForm = false;
    this._editingTransaction = null;
    this._editingPlan = null;
    this._chartError = "";
    this._showAddAccountForm = false;
    this._showEditAccountForm = false;
    this._showDeleteAccountForm = false;
    this._showAccountMenu = false;
    this._deleteConfirmText = "";
    this._searchQuery = "";
    this._showMoreMenu = false;
    this._allRecordsFilterDateStart = "";
    this._allRecordsFilterDateEnd = "";
    this._showBalanceAdjustForm = false;
    this._editingAccountNotes = "";
  }

  connectedCallback() {
    super.connectedCallback();
    this._loadAccounts();
  }

  async _loadAccounts() {
    this._loading = true;
    this._error = "";

    try {
      const result = await this.hass.callWS({ type: "ha_finance/accounts" });
      this._accounts = result.accounts;

      if (this._accounts.length > 0 && !this._selectedAccountId) {
        this._selectedAccountId = this._accounts[0].id;
        await this._loadAccountDetails();
      }
    } catch (err) {
      this._error = err.message || "Failed to load accounts";
    } finally {
      this._loading = false;
    }
  }

  async _loadAccountDetails() {
    if (!this._selectedAccountId) return;

    this._loading = true;
    try {
      const result = await this.hass.callWS({
        type: "ha_finance/account",
        account_id: this._selectedAccountId,
      });
      this._selectedAccount = result.account;
      await this._loadChartData();
    } catch (err) {
      this._error = err.message || "Failed to load account details";
    } finally {
      this._loading = false;
    }
  }

  async _loadChartData() {
    if (!this._selectedAccountId) return;

    this._chartError = "";
    try {
      const result = await this.hass.callWS({
        type: "ha_finance/chart_data",
        account_id: this._selectedAccountId,
        months: 6,
      });
      this._chartData = result.data;
    } catch (err) {
      console.error("Failed to load chart data:", err);
      this._chartError = err.message || "Failed to load chart data";
      this._chartData = [];
    }
  }

  _onAccountChange(e) {
    this._selectedAccountId = e.target.value;
    this._loadAccountDetails();
  }

  _selectAccount(accountId) {
    this._selectedAccountId = accountId;
    this._loadAccountDetails();
  }

  _onTabChange(tab) {
    this._activeTab = tab;
  }

  _getTranslation(key) {
    const translations = {
      en: {
        panel_title: "Ha Finance Record",
        balance: "Balance",
        last_transaction: "Last transaction",
        all_records: "All Records",
        transactions: "Transactions",
        recurring_plans: "Recurring Plans",
        add_transaction: "Add Transaction",
        add_plan: "Add Plan",
        amount: "Amount",
        note: "Note",
        type: "Type",
        date: "Date",
        filter: "Filter",
        all: "All",
        manual: "Manual",
        recurring: "Recurring",
        adjustment: "Adjustment",
        income: "Income",
        expenses: "Expenses",
        title: "Title",
        frequency: "Frequency",
        day: "Day",
        active: "Active",
        daily: "Daily",
        weekly: "Weekly",
        monthly: "Monthly",
        yearly: "Yearly",
        save: "Save",
        cancel: "Cancel",
        delete: "Delete",
        edit: "Edit",
        next_date: "Next",
        no_transactions: "No transactions yet",
        no_plans: "No recurring plans yet",
        no_data: "No chart data available",
        select_account: "Select account",
        confirm_delete: "Are you sure you want to delete this?",
        add_account: "Add Account",
        edit_account: "Edit Account",
        delete_account: "Delete Account",
        account_name: "Account Name",
        initial_balance: "Initial Balance",
        create: "Create",
        delete_warning: "This will permanently delete this account and all its transactions and plans.",
        type_to_confirm: "Type the account name to confirm:",
        no_accounts: "No accounts yet. Add your first account!",
        account_management: "Account Management",
        account_notes: "Account Notes",
        adjust_balance: "Adjust Balance",
        adjustment_amount: "Adjustment Amount",
        adjustment_reason: "Adjustment Reason",
        current_balance: "Current Balance",
        new_balance: "New Balance",
        start_date: "Start Date",
        end_date: "End Date",
      },
      "zh-Hant": {
        panel_title: "財務記錄",
        balance: "餘額",
        last_transaction: "最近交易",
        all_records: "總合紀錄",
        transactions: "交易記錄",
        recurring_plans: "定期項目",
        add_transaction: "新增交易",
        add_plan: "新增項目",
        amount: "金額",
        note: "備註",
        type: "類型",
        date: "日期",
        filter: "篩選",
        all: "全部",
        manual: "手動",
        recurring: "定期",
        adjustment: "調整",
        income: "收入",
        expenses: "支出",
        title: "標題",
        frequency: "頻率",
        day: "日期",
        active: "啟用",
        daily: "每日",
        weekly: "每週",
        monthly: "每月",
        yearly: "每年",
        save: "儲存",
        cancel: "取消",
        delete: "刪除",
        edit: "編輯",
        next_date: "下次",
        no_transactions: "尚無交易記錄",
        no_plans: "尚無定期項目",
        no_data: "無圖表資料",
        select_account: "選擇帳戶",
        confirm_delete: "確定要刪除嗎？",
        add_account: "新增帳戶",
        edit_account: "編輯帳戶",
        delete_account: "刪除帳戶",
        account_name: "帳戶名稱",
        initial_balance: "初始餘額",
        create: "建立",
        delete_warning: "這將永久刪除此帳戶及其所有交易和定期項目。",
        type_to_confirm: "輸入帳戶名稱以確認：",
        no_accounts: "尚無帳戶。新增您的第一個帳戶！",
        account_management: "帳戶管理",
        account_notes: "帳戶備註",
        adjust_balance: "調整餘額",
        adjustment_amount: "調整金額",
        adjustment_reason: "調整原因",
        current_balance: "目前餘額",
        new_balance: "調整後餘額",
        start_date: "開始日期",
        end_date: "結束日期",
      },
    };

    const lang = this.hass?.language || "en";
    const langKey = lang.startsWith("zh") ? "zh-Hant" : "en";
    return translations[langKey]?.[key] || translations["en"][key] || key;
  }

  _formatCurrency(amount) {
    return new Intl.NumberFormat(this.hass?.language || "en", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(amount);
  }

  _formatDate(isoString) {
    try {
      const date = new Date(isoString);
      return date.toLocaleDateString(this.hass?.language || "en");
    } catch {
      return isoString;
    }
  }

  _getFilteredTransactions() {
    if (!this._selectedAccount?.transactions) return [];

    let transactions = [...this._selectedAccount.transactions].reverse();

    if (this._filterType && this._filterType !== "all") {
      transactions = transactions.filter((tx) => tx.type === this._filterType);
    }

    if (this._filterDateStart) {
      const startDate = new Date(this._filterDateStart);
      transactions = transactions.filter(
        (tx) => new Date(tx.timestamp) >= startDate
      );
    }

    if (this._filterDateEnd) {
      const endDate = new Date(this._filterDateEnd);
      endDate.setHours(23, 59, 59, 999);
      transactions = transactions.filter(
        (tx) => new Date(tx.timestamp) <= endDate
      );
    }

    // Search filter
    if (this._searchQuery && this._searchQuery.trim()) {
      const query = this._searchQuery.toLowerCase().trim();
      transactions = transactions.filter((tx) => {
        const note = (tx.note || "").toLowerCase();
        const amount = String(tx.amount);
        return note.includes(query) || amount.includes(query);
      });
    }

    return transactions;
  }

  _openTransactionForm(transaction = null) {
    this._editingTransaction = transaction;
    this._showTransactionForm = true;
  }

  _closeTransactionForm() {
    this._showTransactionForm = false;
    this._editingTransaction = null;
  }

  async _saveTransaction(e) {
    e.preventDefault();
    const form = e.target;
    const amount = parseFloat(form.amount.value);
    const note = form.note.value;

    try {
      if (this._editingTransaction) {
        await this.hass.callWS({
          type: "ha_finance/update_transaction",
          account_id: this._selectedAccountId,
          transaction_id: this._editingTransaction.id,
          amount,
          note,
        });
      } else {
        await this.hass.callWS({
          type: "ha_finance/add_transaction",
          account_id: this._selectedAccountId,
          amount,
          note,
        });
      }
      this._closeTransactionForm();
      await this._loadAccountDetails();
    } catch (err) {
      this._error = err.message || "Failed to save transaction";
    }
  }

  async _deleteTransaction(transaction) {
    if (!confirm(this._getTranslation("confirm_delete"))) return;

    try {
      await this.hass.callWS({
        type: "ha_finance/delete_transaction",
        account_id: this._selectedAccountId,
        transaction_id: transaction.id,
      });
      await this._loadAccountDetails();
    } catch (err) {
      this._error = err.message || "Failed to delete transaction";
    }
  }

  _openPlanForm(plan = null) {
    this._editingPlan = plan;
    this._showPlanForm = true;
  }

  _closePlanForm() {
    this._showPlanForm = false;
    this._editingPlan = null;
  }

  async _savePlan(e) {
    e.preventDefault();
    const form = e.target;
    const title = form.title.value;
    const amount = parseFloat(form.amount.value);
    const frequency = form.frequency.value;
    const day = parseInt(form.day.value);
    const active = form.active.checked;

    try {
      if (this._editingPlan) {
        await this.hass.callWS({
          type: "ha_finance/update_plan",
          account_id: this._selectedAccountId,
          plan_id: this._editingPlan.id,
          title,
          amount,
          frequency,
          day,
          active,
        });
      } else {
        await this.hass.callWS({
          type: "ha_finance/add_plan",
          account_id: this._selectedAccountId,
          title,
          amount,
          frequency,
          day,
          active,
        });
      }
      this._closePlanForm();
      await this._loadAccountDetails();
    } catch (err) {
      this._error = err.message || "Failed to save plan";
    }
  }

  async _deletePlan(plan) {
    if (!confirm(this._getTranslation("confirm_delete"))) return;

    try {
      await this.hass.callWS({
        type: "ha_finance/delete_plan",
        account_id: this._selectedAccountId,
        plan_id: plan.id,
      });
      await this._loadAccountDetails();
    } catch (err) {
      this._error = err.message || "Failed to delete plan";
    }
  }

  _toggleSidebar() {
    // Dispatch event to toggle Home Assistant sidebar
    this.dispatchEvent(new CustomEvent("hass-toggle-menu", { bubbles: true, composed: true }));
  }

  _toggleMoreMenu() {
    this._showMoreMenu = !this._showMoreMenu;
  }

  _closeMoreMenu() {
    this._showMoreMenu = false;
  }

  _onSearchInput(e) {
    this._searchQuery = e.target.value;
  }

  render() {
    if (this._loading && this._accounts.length === 0) {
      return html`<div class="loading">Loading...</div>`;
    }

    return html`
      <!-- Top Bar -->
      <div class="top-bar">
        <button class="top-bar-sidebar-btn" @click=${this._toggleSidebar} title="${getCommonTranslation('menu', this.hass?.language)}">
          <svg viewBox="0 0 24 24"><path fill="currentColor" d="M3,6H21V8H3V6M3,11H21V13H3V11M3,16H21V18H3V16Z"/></svg>
        </button>
        <h1 class="top-bar-title">${this._getTranslation("panel_title")}</h1>
      </div>

      <!-- Search Row - standalone -->
      <div class="search-row">
        <div class="search-row-input-wrapper">
          <svg class="search-row-icon" viewBox="0 0 24 24"><path fill="currentColor" d="M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z"/></svg>
          <input
            class="search-row-input"
            type="text"
            placeholder="${getCommonTranslation('search', this.hass?.language)}"
            .value=${this._searchQuery}
            @input=${this._onSearchInput}
          />
        </div>
      </div>

      <!-- Account Switcher - Health Record style -->
      ${this._accounts.length > 0 ? html`
        <div class="account-switcher-row">
          ${this._accounts.map(
            (account) => html`
              <div
                class="account-card ${account.id === this._selectedAccountId ? 'active' : ''}"
                @click=${() => this._selectAccount(account.id)}
              >
                <div class="account-card-avatar">${account.name.charAt(0).toUpperCase()}</div>
                <div class="account-card-info">
                  <div class="account-card-name">${account.name}</div>
                  <div class="account-card-balance">${this._formatCurrency(account.balance || 0)}</div>
                </div>
              </div>
            `
          )}
          <div class="add-account-card" @click=${this._openAddAccountForm}>
            <svg viewBox="0 0 24 24"><path fill="currentColor" d="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z"/></svg>
            ${this._getTranslation("add_account")}
          </div>
        </div>
      ` : ""}


      ${this._error ? html`<div class="error">${this._error}</div>` : ""}

      ${this._accounts.length === 0 ? this._renderNoAccounts() : ""}
      ${this._selectedAccount ? this._renderAccountContent() : (this._accounts.length > 0 ? this._renderNoAccount() : "")}
      ${this._showTransactionForm ? this._renderTransactionForm() : ""}
      ${this._showPlanForm ? this._renderPlanForm() : ""}
      ${this._showAddAccountForm ? this._renderAddAccountForm() : ""}
      ${this._showEditAccountForm ? this._renderEditAccountForm() : ""}
      ${this._showDeleteAccountForm ? this._renderDeleteAccountForm() : ""}
    `;
  }

  _renderNoAccounts() {
    return html`
      <div class="content-card">
        <div class="empty-state">
          ${this._getTranslation("no_accounts")}
          <br><br>
          <button class="btn btn-primary" @click=${this._openAddAccountForm}>
            ${this._getTranslation("add_account")}
          </button>
        </div>
      </div>
    `;
  }

  _renderNoAccount() {
    return html`
      <div class="content-card">
        <div class="empty-state">${this._getTranslation("select_account")}</div>
      </div>
    `;
  }

  _renderAccountContent() {
    const lastTx = this._selectedAccount.transactions?.slice(-1)[0];

    return html`
      <div class="balance-card">
        <div class="balance-label">${this._getTranslation("balance")}</div>
        <div class="balance-amount">
          ${this._formatCurrency(this._selectedAccount.balance)}
        </div>
        ${lastTx
          ? html`
              <div class="last-transaction">
                ${this._getTranslation("last_transaction")}:
                <span class=${lastTx.amount >= 0 ? "amount-positive" : "amount-negative"}>
                  ${lastTx.amount >= 0 ? "+" : ""}${this._formatCurrency(lastTx.amount)}
                </span>
                (${lastTx.note || "-"})
              </div>
            `
          : ""}
      </div>

      <div class="tabs">
        <button
          class="tab ${this._activeTab === "all_records" ? "active" : ""}"
          @click=${() => this._onTabChange("all_records")}
        >
          ${this._getTranslation("all_records")}
        </button>
        <button
          class="tab ${this._activeTab === "transactions" ? "active" : ""}"
          @click=${() => this._onTabChange("transactions")}
        >
          ${this._getTranslation("transactions")}
        </button>
        <button
          class="tab ${this._activeTab === "plans" ? "active" : ""}"
          @click=${() => this._onTabChange("plans")}
        >
          ${this._getTranslation("recurring_plans")}
        </button>
        <button
          class="tab ${this._activeTab === "account_management" ? "active" : ""}"
          @click=${() => this._onTabChange("account_management")}
        >
          ${this._getTranslation("account_management")}
        </button>
      </div>

      <div class="content-card">
        ${this._activeTab === "all_records" ? this._renderAllRecords() : ""}
        ${this._activeTab === "transactions" ? this._renderTransactions() : ""}
        ${this._activeTab === "plans" ? this._renderPlans() : ""}
        ${this._activeTab === "account_management" ? this._renderAccountManagement() : ""}
      </div>
    `;
  }

  _renderTransactions() {
    const transactions = this._getFilteredTransactions();

    return html`
      <div class="filter-bar">
        <div class="filter-type-row">
          <label>${this._getTranslation("filter")}:</label>
          <select
            @change=${(e) => (this._filterType = e.target.value)}
            .value=${this._filterType}
          >
            <option value="all">${this._getTranslation("all")}</option>
            <option value="manual">${this._getTranslation("manual")}</option>
            <option value="recurring">${this._getTranslation("recurring")}</option>
            <option value="adjustment">${this._getTranslation("adjustment")}</option>
          </select>
        </div>
        <div class="date-range">
          <input
            type="date"
            placeholder="${this._getTranslation("start_date")}"
            @change=${(e) => (this._filterDateStart = e.target.value)}
            .value=${this._filterDateStart}
          />
          <span class="date-separator">-</span>
          <input
            type="date"
            placeholder="${this._getTranslation("end_date")}"
            @change=${(e) => (this._filterDateEnd = e.target.value)}
            .value=${this._filterDateEnd}
          />
        </div>
      </div>

      ${transactions.length === 0
        ? html`<div class="empty-state">${this._getTranslation("no_transactions")}</div>`
        : html`
            <table>
              <thead>
                <tr>
                  <th>${this._getTranslation("date")}</th>
                  <th>${this._getTranslation("amount")}</th>
                  <th>${this._getTranslation("note")}</th>
                  <th>${this._getTranslation("type")}</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                ${transactions.map(
                  (tx) => html`
                    <tr>
                      <td>${this._formatDate(tx.timestamp)}</td>
                      <td class=${tx.amount >= 0 ? "amount-positive" : "amount-negative"}>
                        ${tx.amount >= 0 ? "+" : ""}${this._formatCurrency(tx.amount)}
                      </td>
                      <td>${tx.note || "-"}</td>
                      <td>${this._getTranslation(tx.type)}</td>
                      <td class="actions">
                        <button
                          class="btn btn-secondary btn-small"
                          @click=${() => this._openTransactionForm(tx)}
                        >
                          ${this._getTranslation("edit")}
                        </button>
                        <button
                          class="btn btn-danger btn-small"
                          @click=${() => this._deleteTransaction(tx)}
                        >
                          ${this._getTranslation("delete")}
                        </button>
                      </td>
                    </tr>
                  `
                )}
              </tbody>
            </table>
          `}

      <button
        class="btn btn-primary add-button"
        @click=${() => this._openTransactionForm()}
      >
        ${this._getTranslation("add_transaction")}
      </button>
    `;
  }

  _renderAllRecords() {
    // Combine transactions and recurring plan records
    const transactions = this._selectedAccount?.transactions || [];
    const plans = Object.entries(this._selectedAccount?.recurring_plans || {});

    // Create combined list
    let allRecords = transactions.map(tx => ({
      ...tx,
      recordType: 'transaction',
      displayType: this._getTranslation(tx.type),
    }));

    // Add plan info to display
    plans.forEach(([planId, plan]) => {
      // Add a summary row for each active plan
      if (plan.active) {
        allRecords.push({
          id: `plan_${planId}`,
          recordType: 'plan_summary',
          title: plan.title,
          amount: plan.amount,
          frequency: plan.frequency,
          day: plan.day,
          next_date: plan.next_date,
          timestamp: plan.next_date || new Date().toISOString(),
          displayType: `${this._getTranslation("recurring")} - ${this._getTranslation(plan.frequency)}`,
        });
      }
    });

    // Sort by timestamp descending
    allRecords.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

    // Apply date filter for all records
    if (this._allRecordsFilterDateStart) {
      const startDate = new Date(this._allRecordsFilterDateStart);
      allRecords = allRecords.filter(
        (record) => new Date(record.timestamp) >= startDate
      );
    }

    if (this._allRecordsFilterDateEnd) {
      const endDate = new Date(this._allRecordsFilterDateEnd);
      endDate.setHours(23, 59, 59, 999);
      allRecords = allRecords.filter(
        (record) => new Date(record.timestamp) <= endDate
      );
    }

    // Apply search filter
    if (this._searchQuery && this._searchQuery.trim()) {
      const query = this._searchQuery.toLowerCase().trim();
      allRecords = allRecords.filter((record) => {
        const note = (record.note || record.title || "").toLowerCase();
        const amount = String(record.amount);
        const type = (record.displayType || "").toLowerCase();
        return note.includes(query) || amount.includes(query) || type.includes(query);
      });
    }

    return html`
      <div class="filter-bar">
        <div class="date-range">
          <input
            type="date"
            placeholder="${this._getTranslation("start_date")}"
            @change=${(e) => (this._allRecordsFilterDateStart = e.target.value)}
            .value=${this._allRecordsFilterDateStart}
          />
          <span class="date-separator">-</span>
          <input
            type="date"
            placeholder="${this._getTranslation("end_date")}"
            @change=${(e) => (this._allRecordsFilterDateEnd = e.target.value)}
            .value=${this._allRecordsFilterDateEnd}
          />
        </div>
      </div>
      ${allRecords.length === 0
        ? html`<div class="empty-state">${this._getTranslation("no_transactions")}</div>`
        : html`
            <table>
              <thead>
                <tr>
                  <th>${this._getTranslation("date")}</th>
                  <th>${this._getTranslation("amount")}</th>
                  <th>${this._getTranslation("note")}</th>
                  <th>${this._getTranslation("type")}</th>
                </tr>
              </thead>
              <tbody>
                ${allRecords.map(
                  (record) => html`
                    <tr class="${record.recordType === 'plan_summary' ? 'plan-row' : ''}">
                      <td>${this._formatDate(record.timestamp)}</td>
                      <td class=${record.amount >= 0 ? "amount-positive" : "amount-negative"}>
                        ${record.amount >= 0 ? "+" : ""}${this._formatCurrency(record.amount)}
                      </td>
                      <td>${record.note || record.title || "-"}</td>
                      <td>
                        <span class="type-badge ${record.recordType}">${record.displayType}</span>
                      </td>
                    </tr>
                  `
                )}
              </tbody>
            </table>
          `}
    `;
  }

  _renderPlans() {
    const plans = Object.entries(this._selectedAccount.recurring_plans || {});

    return html`
      ${plans.length === 0
        ? html`<div class="empty-state">${this._getTranslation("no_plans")}</div>`
        : plans.map(
            ([planId, plan]) => html`
              <div class="plan-card ${!plan.active ? "plan-inactive" : ""}">
                <div class="plan-header">
                  <span class="plan-title">${plan.title}</span>
                  <span class="plan-amount ${plan.amount >= 0 ? "amount-positive" : "amount-negative"}">
                    ${plan.amount >= 0 ? "+" : ""}${this._formatCurrency(plan.amount)}
                  </span>
                </div>
                <div class="plan-details">
                  ${this._getTranslation(plan.frequency)} |
                  ${this._getTranslation("day")}: ${plan.day} |
                  ${this._getTranslation("next_date")}: ${plan.next_date || "-"}
                </div>
                <div class="actions" style="margin-top: 12px;">
                  <button
                    class="btn btn-secondary btn-small"
                    @click=${() => this._openPlanForm({ id: planId, ...plan })}
                  >
                    ${this._getTranslation("edit")}
                  </button>
                  <button
                    class="btn btn-danger btn-small"
                    @click=${() => this._deletePlan({ id: planId })}
                  >
                    ${this._getTranslation("delete")}
                  </button>
                </div>
              </div>
            `
          )}

      <button
        class="btn btn-primary add-button"
        @click=${() => this._openPlanForm()}
      >
        ${this._getTranslation("add_plan")}
      </button>
    `;
  }

  _renderAccountManagement() {
    const account = this._selectedAccount;
    if (!account) return html``;

    return html`
      <div class="account-management-section">
        <!-- Account Info Card -->
        <div class="account-info-card">
          <div class="account-info-header">
            <div class="account-avatar-large">${account.name.charAt(0).toUpperCase()}</div>
            <div class="account-info-details">
              <h3 class="account-name-display">${account.name}</h3>
              <div class="account-balance-display">
                <span class="balance-label-small">${this._getTranslation("current_balance")}:</span>
                <span class="balance-value ${account.balance >= 0 ? 'amount-positive' : 'amount-negative'}">
                  ${this._formatCurrency(account.balance)}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Account Notes Section -->
        <div class="account-section">
          <h4 class="section-title">${this._getTranslation("account_notes")}</h4>
          <textarea
            class="account-notes-input"
            placeholder="${this._getTranslation("account_notes")}..."
            .value=${this._editingAccountNotes !== "" ? this._editingAccountNotes : (account.notes || "")}
            @input=${(e) => this._editingAccountNotes = e.target.value}
          ></textarea>
          <button class="btn btn-primary" @click=${this._saveAccountNotes}>
            ${this._getTranslation("save")}
          </button>
        </div>

        <!-- Balance Adjustment Section -->
        <div class="account-section">
          <h4 class="section-title">${this._getTranslation("adjust_balance")}</h4>
          <p class="section-description">
            ${this._getTranslation("current_balance")}:
            <strong class="${account.balance >= 0 ? 'amount-positive' : 'amount-negative'}">
              ${this._formatCurrency(account.balance)}
            </strong>
          </p>
          <button class="btn btn-secondary" @click=${() => this._showBalanceAdjustForm = true}>
            ${this._getTranslation("adjust_balance")}
          </button>
        </div>

        <!-- Edit Account Section -->
        <div class="account-section">
          <h4 class="section-title">${this._getTranslation("edit_account")}</h4>
          <button class="btn btn-secondary" @click=${this._openEditAccountForm}>
            ${this._getTranslation("edit_account")}
          </button>
        </div>

        <!-- Delete Account Section -->
        <div class="account-section danger-section">
          <h4 class="section-title danger">${this._getTranslation("delete_account")}</h4>
          <p class="section-description warning-text-inline">
            ${this._getTranslation("delete_warning")}
          </p>
          <button class="btn btn-danger" @click=${this._openDeleteAccountForm}>
            ${this._getTranslation("delete_account")}
          </button>
        </div>
      </div>

      ${this._showBalanceAdjustForm ? this._renderBalanceAdjustForm() : ""}
    `;
  }

  _renderBalanceAdjustForm() {
    const currentBalance = this._selectedAccount?.balance || 0;

    return html`
      <div class="modal-overlay" @click=${() => this._showBalanceAdjustForm = false}>
        <div class="modal" @click=${(e) => e.stopPropagation()}>
          <h2>${this._getTranslation("adjust_balance")}</h2>
          <form @submit=${this._saveBalanceAdjustment}>
            <div class="form-group">
              <label>${this._getTranslation("current_balance")}</label>
              <div class="current-balance-display ${currentBalance >= 0 ? 'amount-positive' : 'amount-negative'}">
                ${this._formatCurrency(currentBalance)}
              </div>
            </div>
            <div class="form-group">
              <label>${this._getTranslation("adjustment_amount")}</label>
              <input
                type="number"
                name="adjustment"
                step="0.01"
                required
                placeholder="+100 or -50"
              />
              <small class="form-hint">正數為增加，負數為減少</small>
            </div>
            <div class="form-group">
              <label>${this._getTranslation("adjustment_reason")}</label>
              <input
                type="text"
                name="reason"
                placeholder="${this._getTranslation("adjustment_reason")}"
              />
            </div>
            <div class="form-actions">
              <button type="button" class="btn btn-secondary" @click=${() => this._showBalanceAdjustForm = false}>
                ${this._getTranslation("cancel")}
              </button>
              <button type="submit" class="btn btn-primary">
                ${this._getTranslation("save")}
              </button>
            </div>
          </form>
        </div>
      </div>
    `;
  }

  async _saveBalanceAdjustment(e) {
    e.preventDefault();
    const form = e.target;
    const adjustment = parseFloat(form.adjustment.value);
    const reason = form.reason.value || this._getTranslation("adjustment");

    if (isNaN(adjustment) || adjustment === 0) {
      this._error = "Please enter a valid adjustment amount";
      return;
    }

    try {
      // Create an adjustment transaction
      await this.hass.callWS({
        type: "ha_finance/add_transaction",
        account_id: this._selectedAccountId,
        amount: adjustment,
        note: `[${this._getTranslation("adjustment")}] ${reason}`,
        transaction_type: "adjustment",
      });
      this._showBalanceAdjustForm = false;
      await this._loadAccountDetails();
    } catch (err) {
      this._error = err.message || "Failed to adjust balance";
    }
  }

  async _saveAccountNotes() {
    try {
      await this.hass.callWS({
        type: "ha_finance/update_account",
        account_id: this._selectedAccountId,
        notes: this._editingAccountNotes,
      });
      await this._loadAccountDetails();
      // Reset editing state
      this._editingAccountNotes = "";
    } catch (err) {
      this._error = err.message || "Failed to save notes";
    }
  }

  _renderCharts() {
    if (this._chartError) {
      return html`<div class="error">${this._chartError}</div>`;
    }

    if (this._chartData.length === 0) {
      return html`<div class="empty-state">${this._getTranslation("no_data")}</div>`;
    }

    const maxValue = Math.max(
      ...this._chartData.flatMap((d) => [d.income, d.expenses])
    );
    const scale = maxValue > 0 ? 180 / maxValue : 1;

    return html`
      <div class="chart-container">
        <div style="display: flex; justify-content: space-around; align-items: flex-end; height: 220px;">
          ${this._chartData.map(
            (data) => html`
              <div class="chart-bar-group">
                <div class="chart-bars">
                  <div
                    class="chart-bar income"
                    style="height: ${data.income * scale}px"
                    title="${this._getTranslation("income")}: ${this._formatCurrency(data.income)}"
                  ></div>
                  <div
                    class="chart-bar expense"
                    style="height: ${data.expenses * scale}px"
                    title="${this._getTranslation("expenses")}: ${this._formatCurrency(data.expenses)}"
                  ></div>
                </div>
                <div class="chart-label">${data.month}</div>
              </div>
            `
          )}
        </div>
        <div class="chart-legend">
          <div class="legend-item">
            <div class="legend-color income"></div>
            <span>${this._getTranslation("income")}</span>
          </div>
          <div class="legend-item">
            <div class="legend-color expense"></div>
            <span>${this._getTranslation("expenses")}</span>
          </div>
        </div>
      </div>
    `;
  }

  _renderTransactionForm() {
    const tx = this._editingTransaction;

    return html`
      <div class="modal-overlay" @click=${this._closeTransactionForm}>
        <div class="modal" @click=${(e) => e.stopPropagation()}>
          <h2>${tx ? this._getTranslation("edit") : this._getTranslation("add_transaction")}</h2>
          <form @submit=${this._saveTransaction}>
            <div class="form-group">
              <label>${this._getTranslation("amount")}</label>
              <input
                type="number"
                name="amount"
                step="0.01"
                required
                .value=${tx?.amount || ""}
              />
            </div>
            <div class="form-group">
              <label>${this._getTranslation("note")}</label>
              <input
                type="text"
                name="note"
                .value=${tx?.note || ""}
              />
            </div>
            <div class="form-actions">
              <button type="button" class="btn btn-secondary" @click=${this._closeTransactionForm}>
                ${this._getTranslation("cancel")}
              </button>
              <button type="submit" class="btn btn-primary">
                ${this._getTranslation("save")}
              </button>
            </div>
          </form>
        </div>
      </div>
    `;
  }

  _renderPlanForm() {
    const plan = this._editingPlan;

    return html`
      <div class="modal-overlay" @click=${this._closePlanForm}>
        <div class="modal" @click=${(e) => e.stopPropagation()}>
          <h2>${plan ? this._getTranslation("edit") : this._getTranslation("add_plan")}</h2>
          <form @submit=${this._savePlan}>
            <div class="form-group">
              <label>${this._getTranslation("title")}</label>
              <input
                type="text"
                name="title"
                required
                .value=${plan?.title || ""}
              />
            </div>
            <div class="form-group">
              <label>${this._getTranslation("amount")}</label>
              <input
                type="number"
                name="amount"
                step="0.01"
                required
                .value=${plan?.amount || ""}
              />
            </div>
            <div class="form-group">
              <label>${this._getTranslation("frequency")}</label>
              <select name="frequency" required>
                <option value="daily" ?selected=${plan?.frequency === "daily"}>
                  ${this._getTranslation("daily")}
                </option>
                <option value="weekly" ?selected=${plan?.frequency === "weekly"}>
                  ${this._getTranslation("weekly")}
                </option>
                <option value="monthly" ?selected=${plan?.frequency === "monthly" || !plan}>
                  ${this._getTranslation("monthly")}
                </option>
                <option value="yearly" ?selected=${plan?.frequency === "yearly"}>
                  ${this._getTranslation("yearly")}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>${this._getTranslation("day")}</label>
              <input
                type="number"
                name="day"
                min="1"
                max="28"
                required
                .value=${plan?.day || 1}
              />
            </div>
            <div class="form-group">
              <label>
                <input
                  type="checkbox"
                  name="active"
                  ?checked=${plan?.active !== false}
                />
                ${this._getTranslation("active")}
              </label>
            </div>
            <div class="form-actions">
              <button type="button" class="btn btn-secondary" @click=${this._closePlanForm}>
                ${this._getTranslation("cancel")}
              </button>
              <button type="submit" class="btn btn-primary">
                ${this._getTranslation("save")}
              </button>
            </div>
          </form>
        </div>
      </div>
    `;
  }

  // Account Management Methods
  _toggleAccountMenu() {
    this._showAccountMenu = !this._showAccountMenu;
  }

  _closeAccountMenu() {
    this._showAccountMenu = false;
  }

  _openAddAccountForm() {
    this._showAddAccountForm = true;
    this._closeAccountMenu();
  }

  _closeAddAccountForm() {
    this._showAddAccountForm = false;
  }

  _openEditAccountForm() {
    this._showEditAccountForm = true;
    this._closeAccountMenu();
  }

  _closeEditAccountForm() {
    this._showEditAccountForm = false;
  }

  _openDeleteAccountForm() {
    this._showDeleteAccountForm = true;
    this._deleteConfirmText = "";
    this._closeAccountMenu();
  }

  _closeDeleteAccountForm() {
    this._showDeleteAccountForm = false;
    this._deleteConfirmText = "";
  }

  async _saveNewAccount(e) {
    e.preventDefault();
    const form = e.target;
    const name = form.name.value.trim();
    const initialBalance = parseFloat(form.initial_balance.value) || 0;

    if (!name) {
      this._error = "Account name is required";
      return;
    }

    try {
      const result = await this.hass.callWS({
        type: "ha_finance/add_account",
        name,
        initial_balance: initialBalance,
      });
      this._closeAddAccountForm();
      await this._loadAccounts();
      // Select the new account
      if (result.account) {
        this._selectedAccountId = result.account.id;
        await this._loadAccountDetails();
      }
    } catch (err) {
      this._error = err.message || "Failed to create account";
    }
  }

  async _updateAccount(e) {
    e.preventDefault();
    const form = e.target;
    const name = form.name.value.trim();

    if (!name) {
      this._error = "Account name is required";
      return;
    }

    try {
      await this.hass.callWS({
        type: "ha_finance/update_account",
        account_id: this._selectedAccountId,
        name,
      });
      this._closeEditAccountForm();
      await this._loadAccounts();
      await this._loadAccountDetails();
    } catch (err) {
      this._error = err.message || "Failed to update account";
    }
  }

  async _deleteAccount() {
    try {
      await this.hass.callWS({
        type: "ha_finance/delete_account",
        account_id: this._selectedAccountId,
      });
      this._closeDeleteAccountForm();
      this._selectedAccountId = "";
      this._selectedAccount = null;
      await this._loadAccounts();
      // Select first remaining account if any
      if (this._accounts.length > 0) {
        this._selectedAccountId = this._accounts[0].id;
        await this._loadAccountDetails();
      }
    } catch (err) {
      this._error = err.message || "Failed to delete account";
    }
  }

  _onDeleteConfirmInput(e) {
    this._deleteConfirmText = e.target.value;
  }

  _renderAddAccountForm() {
    return html`
      <div class="modal-overlay" @click=${this._closeAddAccountForm}>
        <div class="modal" @click=${(e) => e.stopPropagation()}>
          <h2>${this._getTranslation("add_account")}</h2>
          <form @submit=${this._saveNewAccount}>
            <div class="form-group">
              <label>${this._getTranslation("account_name")}</label>
              <input
                type="text"
                name="name"
                required
                autofocus
              />
            </div>
            <div class="form-group">
              <label>${this._getTranslation("initial_balance")}</label>
              <input
                type="number"
                name="initial_balance"
                step="0.01"
                value="0"
              />
            </div>
            <div class="form-actions">
              <button type="button" class="btn btn-secondary" @click=${this._closeAddAccountForm}>
                ${this._getTranslation("cancel")}
              </button>
              <button type="submit" class="btn btn-primary">
                ${this._getTranslation("create")}
              </button>
            </div>
          </form>
        </div>
      </div>
    `;
  }

  _renderEditAccountForm() {
    return html`
      <div class="modal-overlay" @click=${this._closeEditAccountForm}>
        <div class="modal" @click=${(e) => e.stopPropagation()}>
          <h2>${this._getTranslation("edit_account")}</h2>
          <form @submit=${this._updateAccount}>
            <div class="form-group">
              <label>${this._getTranslation("account_name")}</label>
              <input
                type="text"
                name="name"
                required
                .value=${this._selectedAccount?.name || ""}
              />
            </div>
            <div class="form-actions">
              <button type="button" class="btn btn-secondary" @click=${this._closeEditAccountForm}>
                ${this._getTranslation("cancel")}
              </button>
              <button type="submit" class="btn btn-primary">
                ${this._getTranslation("save")}
              </button>
            </div>
          </form>
        </div>
      </div>
    `;
  }

  _renderDeleteAccountForm() {
    const accountName = this._selectedAccount?.name || "";
    const canDelete = this._deleteConfirmText === accountName;

    return html`
      <div class="modal-overlay" @click=${this._closeDeleteAccountForm}>
        <div class="modal" @click=${(e) => e.stopPropagation()}>
          <h2>${this._getTranslation("delete_account")}</h2>
          <div class="warning-text">
            ${this._getTranslation("delete_warning")}
          </div>
          <div class="form-group">
            <label>${this._getTranslation("type_to_confirm")}</label>
            <div style="font-weight: bold; margin: 8px 0;">"${accountName}"</div>
            <input
              type="text"
              class="confirm-input"
              .value=${this._deleteConfirmText}
              @input=${this._onDeleteConfirmInput}
              placeholder="${accountName}"
            />
          </div>
          <div class="form-actions">
            <button type="button" class="btn btn-secondary" @click=${this._closeDeleteAccountForm}>
              ${this._getTranslation("cancel")}
            </button>
            <button
              type="button"
              class="btn btn-danger"
              ?disabled=${!canDelete}
              @click=${this._deleteAccount}
            >
              ${this._getTranslation("delete")}
            </button>
          </div>
        </div>
      </div>
    `;
  }
}

customElements.define("ha-finance-panel", HaFinancePanel);
