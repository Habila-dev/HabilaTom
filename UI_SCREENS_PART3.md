# UI Specifications: Reports & Administration

This document outlines the UI specifications for the Reports and Administration screens of the Android application.

## E. Reports Screen (`ReportsFragment`)

This screen allows users to generate, view, and export various financial reports.

1.  **Overall Layout:**
    *   **Toolbar:** Title: "Rapports Financiers".
    *   **Content Area:** A `LinearLayout` (vertical) is suitable.
        *   Top section for report selection and filters.
        *   Bottom section for displaying the generated report.

2.  **Report Selection:**
    *   **Component:** A `Spinner` or a `RadioGroup` within a `CardView` for selecting the report type.
    *   **Options:**
        *   "Rapport de Transactions"
        *   "État des Revenus et Dépenses" (Simplified)
        *   "Rapport sur les Salaires"
        *   "Rapport sur les Dividendes"

3.  **Filter Options (Common for most reports):**
    *   **Layout:** Within a `CardView`, below the report selector.
    *   **Date Range:**
        *   `EditText` for Start Date (opens `DatePickerDialog`), `EditText` for End Date (opens `DatePickerDialog`).
        *   Labels: "Date de début", "Date de fin".
    *   **Additional Filters (Contextual, visibility changes based on selected report):**
        *   For "Rapport de Transactions": `Spinner` or `MultiSelectListPreference` (if in a PreferenceScreen-like setup) for "Catégorie(s)".
    *   **"Generate Report" Button:** A `Button` at the bottom of the filter section.

4.  **Report Display Area:**
    *   **Layout:** A `CardView` or a dedicated section below filters to show the report. Initially, it might show a placeholder text like "Sélectionnez un type de rapport et appliquez les filtres."
    *   **Header:** `TextView` indicating the report title and period (e.g., "Rapport de Transactions (01/01/2023 - 31/01/2023)").
    *   **Display Types:**
        *   **Tabular Data (Transaction Report, Salary Report, Dividend Report):** A `RecyclerView` where each item represents a row in the report.
        *   **Summary Data (Income and Expense Statement):** A series of `LinearLayouts` (horizontal) within a vertical `LinearLayout`, each containing a label `TextView` and a value `TextView` (e.g., "Total Entrées: [Amount]").
        *   **Charts:** If a report benefits from a visual (e.g., a Bar Chart for monthly income vs. expense in the "État des Revenus et Dépenses"), it would be embedded using MPAndroidChart.

5.  **Specific Report Content (Examples):**
    *   **Transaction Report:**
        *   `RecyclerView` columns: Date, Type, Montant, Description, Catégorie.
        *   Summary `TextViews` below the list: "Total Entrées: [Amount]", "Total Sorties: [Amount]", "Solde: [Amount]".
    *   **Income and Expense Statement (Simplified):**
        *   `TextView`: "Total Entrées: [Amount]"
        *   `TextView`: "Total Sorties: [Amount]" (Potentially followed by a `RecyclerView` if breaking down by category: Category Name, Total Amount for Category)
        *   `TextView` (prominent): "Bénéfice/Perte Net(te): [Amount]" (value colored green for profit, red for loss).
    *   **Salary Report:**
        *   `RecyclerView` columns: Date Paiement, Nom Employé, Montant Versé.
        *   Summary `TextView`: "Total Salaires Versés: [Amount]".
    *   **Dividend Report:**
        *   `RecyclerView` columns: Date Paiement, Nom Actionnaire, Montant Versé.
        *   Summary `TextView`: "Total Dividendes Versés: [Amount]".

6.  **Export to Excel:**
    *   A `Button` (e.g., "Exporter en Excel") visible after a report is generated.
    *   Action: Triggers export of the currently displayed report data. The Excel format should mirror the on-screen report structure.

7.  **ViewModel Interaction:**
    *   A `ReportsViewModel` will:
        *   Hold the state for selected report type and filter values.
        *   When "Generate Report" is clicked, fetch data from relevant repositories (`TransactionRepository`, `EmployeeRepository`, `ShareholderRepository`) based on selections.
        *   Process/aggregate data as required for the specific report.
        *   Expose the prepared report data (lists, summary values, chart data) via `LiveData`/`StateFlow` to the `ReportsFragment`.
        *   Handle the "Export to Excel" action by providing the report data to an exporter utility.

## F. Administration Screen (`AdminFragment`)

This screen provides access to user management, data management, and other administrative functions. This screen is typically accessible only to users with an "Admin" role.

1.  **Overall Layout:**
    *   **Toolbar:** Title: "Administration".
    *   **Navigation:** A `RecyclerView` where each item is a navigation link to a specific admin section (e.g., "Gestion des Utilisateurs", "Gestion des Données"). Each item would have a title and an icon.

2.  **User Management Section:**
    *   **Navigation:** Clicking the "Gestion des Utilisateurs" item navigates to `UserListFragment`.
    *   **User List Screen (`UserListFragment`):**
        *   **Toolbar:** Title "Utilisateurs", "Add New User" (`+`) icon.
        *   **Display:** `RecyclerView` showing users.
            *   `Item Layout`: `TextView` for Username, `TextView` for Role (e.g., "Admin", "Gestionnaire"), `Chip` or `TextView` for Active Status (color-coded).
        *   **Interaction:** Clicking a user item opens `AddEditUserFragment` for that user.
    *   **Add/Edit User Screen/Dialog (`AddEditUserFragment` or DialogFragment):**
        *   **Title:** "Ajouter Utilisateur" / "Modifier Utilisateur".
        *   **Input Fields (`TextInputLayout`):**
            *   `EditText` for Username.
            *   `EditText` for Password (`inputType="textPassword"`) - For new users or if changing.
            *   `EditText` for Confirm Password (`inputType="textPassword"`) - Only for new users or if password changed.
            *   `Spinner` for Role: "Administrateur", "Gestionnaire", "Utilisateur" (roles should be predefined).
            *   `Switch` or `CheckBox` for "Compte Actif?".
        *   **Password Note:**
            *   For new users, password is required.
            *   For existing users, password fields can be optional ("Laisser vide pour ne pas changer").
            *   Passwords **must** be securely hashed before saving to the database.
        *   **Action Buttons:** "Save", "Cancel".

3.  **Data Management Section:**
    *   Accessed by clicking "Gestion des Données" from the main `AdminFragment` list. This might lead to a dedicated `DataManagementFragment`.
    *   **Backup Data:**
        *   `Button`: "Sauvegarder les Données".
        *   **Action:**
            1.  Request necessary file storage permissions (if not already granted).
            2.  Use `ACTION_CREATE_DOCUMENT` (Storage Access Framework) to let the user choose a location and name for the backup file (e.g., `AppName-Backup-YYYYMMDD-HHMMSS.db`).
            3.  The ViewModel copies the current SQLite database file to the chosen location (on a background thread).
        *   **Feedback:** `Toast` or `Snackbar` on success (with file path) or failure.
    *   **Import/Restore Data:**
        *   `Button`: "Restaurer les Données".
        *   **Action:**
            1.  Request file read permissions.
            2.  Use `ACTION_OPEN_DOCUMENT` to let the user select a previously backed-up `.db` file.
            3.  **CRITICAL WARNING DIALOG:**
                *   Title: "Attention: Restauration des Données".
                *   Message: "Ceci remplacera toutes les données actuelles par le contenu du fichier de sauvegarde. Cette action est irréversible. Voulez-vous continuer ?"
                *   Buttons: "Restaurer", "Annuler".
            4.  If confirmed, the ViewModel handles closing the current database, replacing the database file, and then re-initializing the database connection (on a background thread).
        *   **Feedback:** `Toast` or `Snackbar` on success (app might restart or require manual restart) or failure.

4.  **Application Settings (Optional):**
    *   Navigation item: "Paramètres de l'Application".
    *   Leads to a screen built using `PreferenceFragmentCompat` if using Android's standard preference system.
    *   **Examples:**
        *   Default date range for reports (e.g., "Derniers 30 jours", "Mois en cours").
        *   Theme selection (Light/Dark/System Default).
        *   Notification preferences (if notifications are added later).

5.  **View Application Logs (Optional - for advanced troubleshooting):**
    *   Navigation item: "Consulter les Logs".
    *   Leads to a screen displaying recent application logs.
    *   **Display:** A `RecyclerView` where each item is a log entry (timestamp, log level, tag, message).
    *   **Source:** Logs could be read from a file where Timber (or another logging library) saves them, or from a dedicated Room table if logs are stored persistently for a short period.
    *   **Actions:** "Refresh", "Clear Logs" (if stored by app), "Export Logs".

6.  **ViewModel Interaction:**
    *   `AdminViewModel` (or specific ViewModels like `UserManagementViewModel`, `DataManagementViewModel`):
        *   `UserManagementViewModel`: Handles CRUD for users, interacts with `UserRepository`, ensures password hashing.
        *   `DataManagementViewModel`: Manages database backup/restore logic, file system interactions, and provides feedback.
        *   `SettingsViewModel` (if using custom settings screen): Manages preference values.
        *   `LogsViewModel` (if logs screen is implemented): Fetches and formats log data.
