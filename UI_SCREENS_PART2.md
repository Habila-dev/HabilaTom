# UI Specifications: Employee, Salary, Shareholder & Dividend Management

This document outlines the UI specifications for screens related to managing employees, salaries, shareholders, and dividends.

## C. Employee & Salary Management Screen (`EmployeesFragment`)

This screen allows users to manage employee information and process salary payments.

1.  **Overall Layout:**
    *   **Toolbar:**
        *   Title: "Gestion des Employés et Salaires".
        *   Action Buttons:
            *   "Add New Employee": `+` (plus) icon.
            *   "Filter": Filter icon (e.g., to filter by status: Active/Inactive).
            *   (Optional) "Export": Overflow menu item for Excel exports.
    *   **Main Content:** A `ConstraintLayout` or `LinearLayout` to hold the employee list and potentially action buttons like "Pay Selected Salaries".

2.  **Employee List Display:**
    *   **Component:** `RecyclerView` (e.g., `id: rvEmployees`).
    *   **Item Layout (`list_item_employee.xml`):**
        *   `TextView` for Full Name (e.g., "Doe, John").
        *   `TextView` for Poste (Position) (e.g., "Développeur Android").
        *   `TextView` for Salaire Mensuel (formatted currency, e.g., "3.000,00 €").
        *   `TextView` or `Chip` for Statut ("Actif" or "Inactif"). This could be color-coded (e.g., green for Active, gray for Inactive).
    *   **Interactions:**
        *   **Click:** Navigates to `AddEditEmployeeFragment` in "Edit" mode, pre-filled with the employee's data.
        *   **Selection (for batch payment):** Checkboxes on each item, visible when a "select mode" is active, or long-press to initiate selection.
    *   **"Pay Salaries" Button:** A `Button` (e.g., "Payer Salaires Sélectionnés") that becomes active when one or more active employees are selected. Alternatively, an option within each item or on the detail screen for individual payments.

3.  **Add/Edit Employee (Screen/Dialog - `AddEditEmployeeFragment` or DialogFragment):**
    *   **Layout:** `ScrollView` containing a `LinearLayout` (vertical) of input fields.
    *   **Input Fields (using `TextInputLayout` for hints and errors):**
        *   `EditText` for Nom (Last Name).
        *   `EditText` for Prénom (First Name).
        *   `EditText` or `Spinner` for Poste (Position).
        *   `EditText` for Salaire Mensuel (`inputType="numberDecimal"`).
        *   `EditText` (non-editable) with calendar icon `ImageButton` for Date d'Embauche (opens `DatePickerDialog`).
        *   `Switch` or `CheckBox` for Statut (Label: "Employé Actif ?").
        *   `EditText` for Notes (`inputType="textMultiLine"`).
    *   **Action Buttons:** "Save", "Cancel".
    *   **Mode:**
        *   **Add Mode:** Fields empty/default. Title: "Ajouter Employé".
        *   **Edit Mode:** Fields pre-populated. Title: "Modifier Employé".

4.  **Salary Payment Process:**
    *   **Initiation:**
        *   **Batch:** User selects active employees from the list and clicks a "Payer Salaires Sélectionnés" `Button`.
        *   **Individual:** (Alternative) An option like "Payer Salaire" within each employee's detail view or as a quick action in the list.
    *   **Selection:** If batch, `RecyclerView` items will have `CheckBox`es. A counter for selected employees might be shown.
    *   **Confirmation Dialog (`AlertDialog`):**
        *   Title: "Confirmer Paiement Salaires".
        *   Message: "Payer [X] salaires pour un total de [Total Amount] € ?"
        *   Buttons: "Confirmer", "Annuler".
    *   **Transaction Creation:** On "Confirmer", the `EmployeesViewModel` iterates through selected employees, creates a `Transaction` object for each (type 'Sortie', category 'Salaires', amount `employee.monthlySalary`, description "Paiement de salaire - [Employee Name] - [Month/Year]"), and calls `transactionRepository.insertTransactions(list_of_salary_transactions)`.
    *   **Feedback:** `Toast` or `Snackbar` (e.g., "Paiement des salaires effectué avec succès." or "Erreur lors du paiement.").

5.  **View Salary Payment History (Screen/Dialog - `SalaryHistoryFragment` or DialogFragment):**
    *   **Access:** A button like "Voir Historique des Salaires" on the main `EmployeesFragment` or from an individual employee's detail screen (then filtered for that employee).
    *   **Display:** A `RecyclerView` showing salary payment transactions.
        *   `Item Layout`: Date, Employee Name (if viewing for all), Montant, Description.
    *   **Filtering:** May allow filtering by date range or employee.
    *   **Data Source:** `TransactionsViewModel` or `EmployeesViewModel` fetching transactions filtered by `category = 'Salaires'`.

6.  **Export to Excel:**
    *   Located in Toolbar menu or as dedicated buttons.
    *   **"Exporter Liste des Employés":** Exports data as defined in `BUSINESS_LOGIC.md` (ID, Name, Position, Salary, Hire Date, Active).
    *   **"Exporter Paiements Salaires":** Exports salary payment history (Date, Employee Name, Amount, Description).

7.  **ViewModel Interaction:**
    *   An `EmployeesViewModel` will:
        *   Manage the list of employees (fetch from `EmployeeRepository`).
        *   Handle add/edit operations (calling `employeeRepository.insertEmployee()` or `updateEmployee()`).
        *   Orchestrate the salary payment process (interacting with `EmployeeRepository` to get employee data and `TransactionRepository` to save salary transactions).
        *   Provide data for salary payment history.
        *   Initiate Excel exports by providing data to an exporter utility.

## D. Shareholder & Dividend Management Screen (`ShareholdersFragment`)

This screen allows users to manage shareholder information and process dividend distributions.

1.  **Overall Layout:**
    *   **Toolbar:**
        *   Title: "Gestion des Actionnaires et Dividendes".
        *   Action Buttons:
            *   "Add New Shareholder": `+` (plus) icon.
            *   "Filter": Filter icon (e.g., by status Active/Inactive).
            *   (Optional) "Export": Overflow menu item.
    *   **Main Content:** `ConstraintLayout` or `LinearLayout`.

2.  **Shareholder List Display:**
    *   **Component:** `RecyclerView` (e.g., `id: rvShareholders`).
    *   **Item Layout (`list_item_shareholder.xml`):**
        *   `TextView` for Full Name.
        *   `TextView` for Parts Sociales (e.g., "150 parts").
        *   `TextView` or `Chip` for Statut ("Actif" or "Inactif"), color-coded.
    *   **Interactions:**
        *   **Click:** Navigates to `AddEditShareholderFragment` in "Edit" mode.

3.  **Add/Edit Shareholder (Screen/Dialog - `AddEditShareholderFragment` or DialogFragment):**
    *   **Layout:** `ScrollView` with `LinearLayout` of input fields.
    *   **Input Fields (using `TextInputLayout`):**
        *   `EditText` for Nom (Last Name).
        *   `EditText` for Prénom (First Name).
        *   `EditText` for Parts Sociales (`inputType="number"`).
        *   `EditText` (non-editable) with calendar icon for Date d'Acquisition (opens `DatePickerDialog`).
        *   `Switch` or `CheckBox` for Statut (Label: "Actionnaire Actif ?").
        *   `EditText` for Notes (`inputType="textMultiLine"`).
    *   **Action Buttons:** "Save", "Cancel".
    *   **Mode:** Add/Edit titles and data pre-population as with employees.

4.  **Dividend Distribution Process:**
    *   **Initiation:** A `Button` on the main screen (e.g., "Distribuer Dividendes").
    *   **Input Dialog (`AlertDialog` or custom DialogFragment):**
        *   Title: "Distribution de Dividendes".
        *   `EditText` for "Montant Total à Distribuer" (`inputType="numberDecimal"`).
        *   Buttons: "Calculer & Confirmer", "Annuler".
    *   **Calculation & Confirmation Dialog:**
        *   After user inputs total amount and clicks "Calculer & Confirmer":
        *   Display:
            *   "Montant total à distribuer: [Total Amount] €"
            *   "Nombre total de parts sociales (actifs): [Total Active Shares]"
            *   "Montant par part: [Amount per Share] €"
            *   "Nombre d'actionnaires actifs concernés: [Count]"
        *   Buttons: "Confirmer Distribution", "Annuler".
    *   **Transaction Creation:** On "Confirmer Distribution", `ShareholdersViewModel` calculates amount per shareholder and creates 'Sortie' transactions (category 'Dividendes') for each active shareholder, then calls `transactionRepository.insertTransactions(list_of_dividend_transactions)`.
    *   **Feedback:** `Toast` or `Snackbar`.

5.  **View Dividend Payment History (Screen/Dialog - `DividendHistoryFragment` or DialogFragment):**
    *   **Access:** Button like "Voir Historique des Dividendes".
    *   **Display:** `RecyclerView` listing dividend payment transactions.
        *   `Item Layout`: Date, Shareholder Name, Montant, Description.
    *   **Filtering:** By date range or shareholder.
    *   **Data Source:** `TransactionsViewModel` or `ShareholdersViewModel` fetching transactions filtered by `category = 'Dividendes'`.

6.  **Export to Excel:**
    *   Located in Toolbar menu or as dedicated buttons.
    *   **"Exporter Liste des Actionnaires":** (ID, Name, Shares, Acquisition Date, Active).
    *   **"Exporter Paiements Dividendes":** (Date, Shareholder Name, Amount, Description).

7.  **ViewModel Interaction:**
    *   A `ShareholdersViewModel` will:
        *   Manage shareholder list (from `ShareholderRepository`).
        *   Handle add/edit operations.
        *   Orchestrate dividend distribution (interacting with `ShareholderRepository` for share data and `TransactionRepository` for saving dividend transactions).
        *   Provide data for dividend payment history.
        *   Initiate Excel exports.
