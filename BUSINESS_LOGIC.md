# Core Business Logic Definition

This document details the core business logic from the Python application that needs to be ported to Kotlin/Java for the Android application.

## 1. Financial Summary Calculations

These calculations provide an overview of the company's financial health. They will primarily be used in dashboards and financial reports.

*   **Total Entrées (Total Income):**
    *   **Logic:** Sum of `amount` for all `Transaction` records where `type` is `TransactionType.ENTREE`.
    *   **Implementation:** Typically a method in `TransactionRepository` (e.g., `getTotalIncome(): Flow<Double>`) that executes a Room DAO query (e.g., `SELECT SUM(amount) FROM transactions WHERE type = 'ENTREE'`).
*   **Total Sorties (Total Expenses):**
    *   **Logic:** Sum of `amount` for all `Transaction` records where `type` is `TransactionType.SORTIE`.
    *   **Implementation:** Similar to Total Entrées, a method in `TransactionRepository` (e.g., `getTotalExpenses(): Flow<Double>`) using a DAO query (e.g., `SELECT SUM(amount) FROM transactions WHERE type = 'SORTIE'`).
*   **Solde Actuel (Current Balance):**
    *   **Logic:** `Total Entrées` - `Total Sorties`.
    *   **Implementation:** This would typically be calculated in a `FinancialReportViewModel` by observing the `Flow`s for total income and total expenses from the `TransactionRepository` and combining their results.
        ```kotlin
        // In ViewModel
        // val totalIncome: StateFlow<Double> = transactionRepository.getTotalIncome().stateIn(...)
        // val totalExpenses: StateFlow<Double> = transactionRepository.getTotalExpenses().stateIn(...)
        // val currentBalance: StateFlow<Double> = combine(totalIncome, totalExpenses) { income, expenses ->
        //     income - expenses
        // }.stateIn(...)
        ```
*   **Entrées du Mois (Monthly Income):**
    *   **Logic:** Sum of `amount` for `Transaction` records where `type` is `TransactionType.ENTREE` and `date` is within the current calendar month.
    *   **Implementation:** A method in `TransactionRepository` (e.g., `getIncomeForMonth(year: Int, month: Int): Flow<Double>`) that takes the current year and month, calculates the start and end timestamps for that month, and uses a DAO query with a date range.
*   **Sorties du Mois (Monthly Expenses):**
    *   **Logic:** Sum of `amount` for `Transaction` records where `type` is `TransactionType.SORTIE` and `date` is within the current calendar month.
    *   **Implementation:** Similar to Monthly Income, a method in `TransactionRepository` (e.g., `getExpensesForMonth(year: Int, month: Int): Flow<Double>`).
*   **Solde Cumulé (Cumulative Balance over time for charting):**
    *   **Logic:** For each transaction, ordered by `date` (and potentially `transactionId` for tie-breaking), calculate the running total. Start with an initial balance (could be 0 or the balance before the first transaction in the considered range). Iterate through transactions: add `amount` if `TransactionType.ENTREE`, subtract `amount` if `TransactionType.SORTIE`. This results in a list of (date, cumulativeBalance) pairs.
    *   **Implementation:** This is more complex. It can be handled in the `TransactionRepository` or a dedicated use case/interactor class.
        *   Fetch all transactions sorted by date: `transactionDao.getAllTransactionsSortedByDate(): Flow<List<Transaction>>`.
        *   In the Repository or UseCase, transform this list:
            ```kotlin
            // fun getCumulativeBalanceFlow(): Flow<List<Pair<Long, Double>>> {
            //     return transactionDao.getAllTransactionsSortedByDate().map { transactions ->
            //         var currentBalance = 0.0
            //         val balanceOverTime = mutableListOf<Pair<Long, Double>>()
            //         for (transaction in transactions) {
            //             currentBalance += if (transaction.type == TransactionType.ENTREE) transaction.amount else -transaction.amount
            //             balanceOverTime.add(Pair(transaction.date, currentBalance))
            //         }
            //         balanceOverTime
            //     }
            // }
            ```
    *   **Location:** Methods for individual totals (`getTotalIncome`, `getTotalExpenses`, `getIncomeForMonth`, `getExpensesForMonth`, `getCumulativeBalanceFlow`) would reside in the `TransactionRepository` (which calls corresponding DAO methods). The final calculation of `Solde Actuel` or `Solde du Mois` by combining these values would typically occur in a `FinancialReportViewModel` or a relevant ViewModel that needs to display this summary.

## 2. Salary Processing Logic

This logic handles the payment of salaries to employees.

*   **Paying Salaries:**
    *   **Trigger:** User initiates salary payment, typically selecting active employees from a list in the UI.
    *   **Process (likely in an `EmployeeViewModel` or `SalaryViewModel`):**
        1.  For each selected active `Employee`:
        2.  Create a new `Transaction` object:
            *   `transactionId`: 0 (auto-generated by Room).
            *   `date`: Current date (`System.currentTimeMillis()`) or a user-selected payment date.
            *   `type`: `TransactionType.SORTIE`.
            *   `amount`: `employee.monthlySalary`.
            *   `description`: "Paiement de salaire - ${employee.firstName} ${employee.lastName} - [Month/Year]". The Month/Year should be determined programmatically (e.g., current month or a selected payroll month).
            *   `category`: "Salaires".
        3.  Call `transactionRepository.insertTransaction(newTransaction)` for each generated transaction. This should ideally be done in a single database transaction if multiple salaries are processed at once. Room can handle this by having the DAO method take a `List<Transaction>`.
*   **Total Salaries Paid (for a period):**
    *   **Logic:** Sum of `amount` for `Transaction` records where `category` is 'Salaires' and `date` is within a user-specified date range.
    *   **Implementation:** A method in `TransactionRepository` (e.g., `getTotalSalariesPaid(startDate: Long, endDate: Long): Flow<Double>`) using a DAO query:
        `SELECT SUM(amount) FROM transactions WHERE category = 'Salaires' AND date BETWEEN :startDate AND :endDate`.

## 3. Dividend Distribution Logic

This logic handles the payment of dividends to shareholders.

*   **Paying Dividends:**
    *   **Trigger:** User initiates dividend payment, typically selecting active shareholders and specifying a total dividend amount.
    *   **Process (likely in a `ShareholderViewModel` or `DividendViewModel`):**
        1.  User inputs `totalDividendAmountToDistribute`.
        2.  Fetch all active shareholders to calculate `totalActiveSocialShares`: `shareholderRepository.getActiveShareholders().first().sumOf { it.socialShares }`. (Ensure this is done carefully, possibly getting the sum directly from a DAO query if performance is a concern for many shareholders).
        3.  If `totalActiveSocialShares` is 0, prevent division by zero and show an error.
        4.  Calculate `amountPerShare = totalDividendAmountToDistribute / totalActiveSocialShares`.
        5.  For each selected (or all active) `Shareholder`:
        6.  Create a new `Transaction` object:
            *   `transactionId`: 0 (auto-generated by Room).
            *   `date`: Current date (`System.currentTimeMillis()`) or a user-selected payment date.
            *   `type`: `TransactionType.SORTIE`.
            *   `amount`: `amountPerShare * shareholder.socialShares`. Rounding might need to be considered here.
            *   `description`: "Distribution de dividendes - ${shareholder.firstName} ${shareholder.lastName} - [Date of distribution or relevant period]".
            *   `category`: "Dividendes".
        7.  Call `transactionRepository.insertTransaction(newTransaction)` for each. Similar to salaries, batch insertion is preferable.

## 4. Excel Export Functionality

This involves fetching data and formatting it into an `.xlsx` file. Apache POI is the suggested library. File I/O operations **must** be performed on a background thread (e.g., using Kotlin Coroutines with `Dispatchers.IO`).

*   **General Structure:**
    *   A dedicated utility class (e.g., `ExcelExporter`) or methods within relevant ViewModels (delegating the actual Excel creation to a worker/utility).
    *   Methods will take lists of data (e.g., `List<Transaction>`, `List<Employee>`) as input.
    *   These methods will construct a `Workbook` object (e.g., `XSSFWorkbook` for `.xlsx`), create sheets, rows, and cells, and populate them with data.
    *   The resulting `Workbook` will be written to an `OutputStream` (e.g., to a file in the app's cache directory or directly via Storage Access Framework if letting the user choose location).

*   **Transactions Export:**
    *   **Sheet Name:** "Transactions"
    *   **Columns:** Date (formatted), Type (Entrée/Sortie), Montant, Description, Catégorie.
    *   **Data Source:** `transactionRepository.getAllTransactions()` or a filtered list based on UI criteria.
*   **Employee List Export:**
    *   **Sheet Name:** "Employés"
    *   **Columns:** ID Employé, Nom, Prénom, Poste, Salaire Mensuel (formatted currency), Date Embauche (formatted), Statut (Actif/Inactif).
    *   **Data Source:** `employeeRepository.getAllEmployees()`.
*   **Salary Payments Export:**
    *   **Sheet Name:** "Paiements Salaires"
    *   **Columns:** Date Paiement (formatted), Nom Employé, Montant Versé (formatted currency), Description.
    *   **Data Source:** `transactionRepository.getTransactionsByCategory("Salaires")` or filtered by date range.
*   **Shareholder List Export:**
    *   **Sheet Name:** "Actionnaires"
    *   **Columns:** ID Actionnaire, Nom, Prénom, Parts Sociales, Date Acquisition (formatted), Statut (Actif/Inactif).
    *   **Data Source:** `shareholderRepository.getAllShareholders()`.
*   **Dividend Payments Export:**
    *   **Sheet Name:** "Paiements Dividendes"
    *   **Columns:** Date Paiement (formatted), Nom Actionnaire, Montant Versé (formatted currency), Description.
    *   **Data Source:** `transactionRepository.getTransactionsByCategory("Dividendes")` or filtered by date range.

*   **Implementation Note:** The ViewModel would initiate the export process. It would fetch the required data from repositories and then pass it to the `ExcelExporter`. The `ExcelExporter` would handle the Apache POI interaction. The ViewModel would observe the export status (e.g., in progress, success with file URI, error) via `LiveData`/`StateFlow` to update the UI.

## 5. Data Validation (General Note)

Input validation is crucial before processing data or saving it to the database to maintain data integrity.

*   **Location:** Primarily in ViewModels. When user input is received (e.g., from `EditText` fields for creating a transaction, adding an employee, or setting a dividend amount):
    *   The View passes the raw input to the ViewModel.
    *   The ViewModel validates the data:
        *   **Required Fields:** Check for non-empty strings (e.g., description, names).
        *   **Numeric Values:** Ensure amounts are valid numbers, positive where required (e.g., transaction amount, salary).
        *   **Dates:** Validate date formats or ensure selected dates are logical (e.g., hire date not in the future).
        *   **Business Rules:** Enforce any specific business rules (e.g., salary must be above a minimum if applicable).
    *   If validation fails, the ViewModel updates a `LiveData`/`StateFlow` with an error message or state that the View observes to display feedback to the user (e.g., highlighting incorrect fields, showing an error message).
    *   Only if validation passes does the ViewModel proceed to interact with Repositories to save or process data.

This approach mirrors how input validation is often handled in UIs before backend submission, ensuring data quality at the point of entry.
