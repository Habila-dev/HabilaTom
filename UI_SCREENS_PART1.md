# UI Specifications: Main Dashboard & Transactions Management

This document outlines the UI specifications for the Main Dashboard and Transactions Management screens of the Android application.

## A. Main Dashboard Screen (`MainActivity` or `DashboardFragment`)

This screen provides an at-a-glance overview of the company's financial status and key metrics.

1.  **Overall Layout:**
    *   **Structure:** A `CoordinatorLayout` is recommended for the root, allowing for rich scrolling behaviors.
        *   An `AppBarLayout` within the `CoordinatorLayout` will house the `Toolbar`.
        *   A `NestedScrollView` or `RecyclerView` (if the dashboard itself has many sections that could be individual view types) will contain the main content area, allowing it to scroll independently.
    *   **Toolbar:**
        *   Displays the screen title (e.g., "Tableau de Bord" or App Name).
        *   May contain action icons like "Settings" (e.g., gear icon) or "User Profile" (e.g., user icon), though these might also be in the navigation drawer.
    *   **Navigation:**
        *   If a **Navigation Drawer** is used (common for apps with multiple top-level sections like Dashboard, Transactions, Employees, etc.), a "hamburger" icon (`三`) will be present in the Toolbar to open it.
        *   If **Bottom Navigation** is chosen for primary navigation between main sections, it would be placed at the bottom of this screen. For this document, we'll assume a context where a Navigation Drawer is more likely given the potential number of management sections.

2.  **Key Metrics Display:**
    *   **Layout:** A `GridLayout` or a series of `LinearLayouts` (horizontal, then wrapped in a vertical one) can be used to display key metrics.
    *   **Appearance:** Each metric will be displayed within a Material Design `CardView` for clear visual separation and a modern look.
    *   **Content of Cards:**
        *   **Solde Actuel (Current Balance):**
            *   Label: `TextView` "Solde Actuel"
            *   Value: `TextView` displaying the formatted currency amount (e.g., "12.345,67 €"). Value text should be prominent.
        *   **Total Entrées (Total Income):**
            *   Label: `TextView` "Total Entrées"
            *   Value: `TextView` displaying the formatted currency amount.
            *   Delta: Optional `TextView` below or beside the value, e.g., "+1.234 € ce mois" (income this month), possibly with a positive color (e.g., green).
        *   **Total Sorties (Total Expenses):**
            *   Label: `TextView` "Total Sorties"
            *   Value: `TextView` displaying the formatted currency amount.
            *   Delta: Optional `TextView` below or beside the value, e.g., "-567 € ce mois" (expenses this month), possibly with a negative color (e.g., red).
        *   **Employés Actifs (Active Employees):**
            *   Label: `TextView` "Employés Actifs"
            *   Value: `TextView` displaying the count (e.g., "15 Employés").

3.  **Charts Display:**
    *   Charts will be implemented using a library like **MPAndroidChart**. Each chart will likely be contained within its own `CardView`.
    *   **Évolution du Solde (Balance Evolution):**
        *   **Type:** Line Chart (`LineChart`).
        *   **Data Source:** A list of (timestamp, balance) pairs provided by the `DashboardViewModel`.
        *   **Axes:**
            *   X-axis (horizontal): Dates, formatted appropriately (e.g., "Jan", "Feb", "Mar" or "DD/MM").
            *   Y-axis (vertical): Solde (currency amount).
        *   **Description:** A `TextView` label like "Évolution du Solde sur les 6 derniers mois".
    *   **Répartition Entrées vs Sorties (Income vs Expenses Breakdown - Current Month or All Time):**
        *   **Type:** Pie Chart (`PieChart`).
        *   **Data:** Two values: Total Income for the period, Total Expenses for the period.
        *   **Labels:** Slices labeled "Entrées" and "Sorties", with corresponding percentages or values. Colors should be distinct (e.g., green for Entrées, red for Sorties).
        *   **Description:** A `TextView` label like "Répartition Entrées/Sorties (Ce Mois)".
    *   **Répartition du Capital (Capital Distribution - Shareholders):**
        *   **Type:** Pie Chart (`PieChart`).
        *   **Data:** List of (Shareholder Name, `socialShares`) pairs. The chart will represent the proportion of shares held by each shareholder.
        *   **Labels:** Slices labeled with shareholder names or IDs, showing percentage or number of shares.
        *   **Description:** A `TextView` label like "Répartition du Capital Social".

4.  **Dernières Transactions (Recent Transactions List):**
    *   **Layout:** A `RecyclerView` to display a short list (e.g., 5-10 most recent transactions).
    *   **Item Layout (`list_item_transaction_recent.xml`):**
        *   `TextView` for Date (e.g., "DD/MM/YYYY" or "Hier").
        *   `ImageView` or colored `View` as a visual cue for Type (e.g., green up arrow for 'Entrée', red down arrow for 'Sortie').
        *   `TextView` for Montant (formatted currency).
        *   `TextView` for Description (single line, truncated with ellipsis if too long).
        *   `TextView` for Catégorie.
    *   **Header:** A `TextView` label "Dernières Transactions".
    *   **"View All" Button:** A `Button` or `TextView` with text "Voir Tout" or an arrow icon at the end of the list or in the section header, which navigates to the full `TransactionsFragment`.

5.  **Data Source & ViewModel Interaction:**
    *   All data displayed on this screen will be provided by a `DashboardViewModel`.
    *   The `DashboardViewModel` will fetch data from relevant repositories (`TransactionRepository`, `EmployeeRepository`, `ShareholderRepository`).
    *   It will expose `LiveData` or `StateFlow` for:
        *   Key metrics (Solde Actuel, Total Entrées, Total Sorties, Employés Actifs counts, monthly deltas).
        *   Chart data (formatted lists/sets suitable for MPAndroidChart).
        *   The list of recent transactions.
    *   The Fragment/Activity will observe these data streams and update the UI accordingly.

## B. Transactions Management Screen (`TransactionsFragment`)

This screen allows users to view, add, edit, delete, and filter all financial transactions.

1.  **Overall Layout:**
    *   **Toolbar:**
        *   Title: "Transactions".
        *   Action Buttons:
            *   "Add New": An icon (e.g., `+` (plus) icon, `Iconics` library or Material Vector Drawable).
            *   "Filter": An icon (e.g., filter funnel icon).
            *   "Export": (Optional, could be in an overflow menu) An icon for exporting to Excel.
    *   **Content Area:** `ConstraintLayout` or `LinearLayout` to hold summary stats and the RecyclerView.

2.  **Transaction List Display:**
    *   **Component:** `RecyclerView` (e.g., `id: rvTransactions`).
    *   **Item Layout (`list_item_transaction_full.xml`):** Similar to the recent transactions item, but potentially with more detail or less truncation.
        *   `TextView` for Date.
        *   `TextView` for Type (e.g., "Entrée" or "Sortie"), possibly styled with color.
        *   `TextView` for Montant (formatted currency).
        *   `TextView` for Description (can be multiple lines or expandable).
        *   `TextView` for Catégorie.
    *   **Visual Cues:** Background color for items or a specific icon/color bar can differentiate 'Entrée' (e.g., light green background/accent) from 'Sortie' (e.g., light red background/accent).
    *   **Interactions:**
        *   **Click:** Opens the `AddEditTransactionFragment` (or DialogFragment) in "Edit" mode, pre-filled with the clicked transaction's data.
        *   **Long-press or Swipe:** Reveals quick actions like "Delete". A confirmation dialog (`AlertDialog`) must be shown before actual deletion.

3.  **Filtering Options:**
    *   **Display:** Triggered by the "Filter" action button. Could be:
        *   A `BottomSheetDialogFragment`.
        *   An expandable section at the top of the screen.
        *   A dedicated DialogFragment.
    *   **Filter Controls:**
        *   **Date Range:** Two `EditText` fields that open `DatePickerDialog`s (one for start date, one for end date).
        *   **Transaction Type:** `ChipGroup` with `Chip`s for "Tous", "Entrée", "Sortie" or `RadioGroup` with `RadioButton`s.
        *   **Category:** `Spinner` or an AutoCompleteTextView populated with existing categories. Could also be a multi-select list if filtering by multiple categories is needed.
    *   **Actions:**
        *   "Apply Filters" `Button`.
        *   "Reset Filters" `Button`.

4.  **Summary Statistics (for filtered data):**
    *   **Display:** `TextViews` located above the `RecyclerView` or in a sticky header/footer.
    *   **Content:**
        *   "Total Entrées (filtrées): [Amount]"
        *   "Total Sorties (filtrées): [Amount]"
        *   "Solde (filtré): [Amount]"
    *   These values update whenever filters are applied or transactions are changed.

5.  **Add/Edit Transaction (Screen/Dialog - `AddEditTransactionFragment` or `AddEditTransactionDialog`):**
    *   **Layout:** A `ScrollView` containing a `LinearLayout` (vertical) of input fields.
    *   **Input Fields:**
        *   **Date:** `EditText` (not editable directly) with a calendar icon `ImageButton` to open a `DatePickerDialog`. Pre-fills with current date for "Add", existing date for "Edit".
        *   **Type:** `RadioGroup` with "Entrée" and "Sortie" `RadioButton`s.
        *   **Montant:** `EditText` with `inputType="numberDecimal"`. Use `TextInputLayout` for hints and error messages.
        *   **Description:** `EditText` (multi-line `inputType="textMultiLine"`). Use `TextInputLayout`.
        *   **Catégorie:** `Spinner` or `AutoCompleteTextView` populated with existing categories from the database. An option to quickly add a new category might be useful (e.g., a small "+" button next to the spinner/input).
    *   **Action Buttons:**
        *   "Save" `Button`.
        *   "Cancel" `Button`.
    *   **Mode:**
        *   **Add Mode:** Fields are empty or have defaults. Title: "Ajouter Transaction".
        *   **Edit Mode:** Fields are pre-populated with the selected transaction's data. Title: "Modifier Transaction".

6.  **Export to Excel:**
    *   A `Button` (e.g., in Toolbar overflow menu or near filter actions).
    *   Triggers the Excel export functionality defined in `BUSINESS_LOGIC.md` for the currently displayed (and filtered) list of transactions.
    *   Should provide feedback to the user (e.g., Toast, Snackbar) on success or failure, and potentially an option to share/open the generated file.

7.  **ViewModel Interaction:**
    *   A `TransactionsViewModel` will be responsible for:
        *   Fetching and holding the list of all transactions (or applying filters) from `TransactionRepository`.
        *   Exposing `LiveData`/`StateFlow` for the transaction list and summary statistics to the `TransactionsFragment`.
        *   Managing the current filter state.
        *   Handling the logic for adding a new transaction (calling `transactionRepository.insertTransaction()`).
        *   Handling the logic for updating an existing transaction (calling `transactionRepository.updateTransaction()`).
        *   Handling the logic for deleting a transaction (calling `transactionRepository.deleteTransaction()`).
        *   Providing data for category suggestions in the Add/Edit screen.
        *   Initiating the Excel export process by providing the filtered list to an exporter utility.
