# Navigation System Definition

This document outlines the navigation system for the Android application, utilizing Android Jetpack's Navigation Component.

## 1. Primary Navigation Method

*   **Method:** A **Navigation Drawer**.
*   **Rationale:**
    *   **Multiple Top-Level Destinations:** The application has several distinct, top-level sections (Dashboard, Transactions, Employees, Shareholders, Reports, Admin). A Navigation Drawer provides a clear and organized way to access these.
    *   **Screen Real Estate:** It keeps the main screen area uncluttered by hiding primary navigation links until needed, dedicating more space to content.
    *   **Scalability:** Easily accommodates new top-level sections if the app grows.
*   **Basic Behavior:**
    *   Accessed via a "hamburger" icon (`☰`) located in the `Toolbar` of `MainActivity`.
    *   The drawer slides out from the start side of the screen (left in LTR languages).
    *   It contains a list of menu items, each corresponding to a primary navigation destination.
    *   Clicking an item navigates the user to the respective screen.
    *   The drawer can typically be dismissed by tapping outside of it, pressing the system back button, or swiping it closed.

## 2. Navigation Graph (using Android Jetpack's Navigation Component)

The Navigation Component will manage all in-app navigation. A central navigation graph (`nav_graph.xml`) will define destinations and actions.

*   **Host:** The `NavController` will be hosted in a `NavHostFragment` embedded within the `MainActivity`'s layout.
*   **Main Navigation Graph (`nav_graph.xml`):**

    ```xml
    <navigation xmlns:android="http://schemas.android.com/apk/res/android"
        xmlns:app="http://schemas.android.com/apk/res-auto"
        xmlns:tools="http://schemas.android.com/tools"
        android:id="@+id/nav_graph"
        app:startDestination="@id/dashboardFragment"> <!-- Or loginFragment initially, then to dashboard -->

        <!-- Primary Destinations (linked from Navigation Drawer) -->
        <fragment
            android:id="@+id/dashboardFragment"
            android:name="com.example.app.ui.dashboard.DashboardFragment"
            android:label="Tableau de Bord"
            tools:layout="@layout/fragment_dashboard" />

        <fragment
            android:id="@+id/transactionsFragment"
            android:name="com.example.app.ui.transactions.TransactionsFragment"
            android:label="Transactions"
            tools:layout="@layout/fragment_transactions" >
            <action
                android:id="@+id/action_transactionsFragment_to_addEditTransactionFragment"
                app:destination="@id/addEditTransactionFragment" />
        </fragment>

        <fragment
            android:id="@+id/employeesFragment"
            android:name="com.example.app.ui.employees.EmployeesFragment"
            android:label="Gestion des Employés"
            tools:layout="@layout/fragment_employees">
            <action
                android:id="@+id/action_employeesFragment_to_addEditEmployeeFragment"
                app:destination="@id/addEditEmployeeFragment" />
            <action
                android:id="@+id/action_employeesFragment_to_salaryHistoryFragment"
                app:destination="@id/salaryHistoryFragment" />
        </fragment>

        <fragment
            android:id="@+id/shareholdersFragment"
            android:name="com.example.app.ui.shareholders.ShareholdersFragment"
            android:label="Gestion des Actionnaires"
            tools:layout="@layout/fragment_shareholders">
            <action
                android:id="@+id/action_shareholdersFragment_to_addEditShareholderFragment"
                app:destination="@id/addEditShareholderFragment" />
            <action
                android:id="@+id/action_shareholdersFragment_to_dividendHistoryFragment"
                app:destination="@id/dividendHistoryFragment" />
        </fragment>

        <fragment
            android:id="@+id/reportsFragment"
            android:name="com.example.app.ui.reports.ReportsFragment"
            android:label="Rapports Financiers"
            tools:layout="@layout/fragment_reports" />

        <fragment
            android:id="@+id/adminFragment"
            android:name="com.example.app.ui.admin.AdminFragment"
            android:label="Administration"
            tools:layout="@layout/fragment_admin">
            <action
                android:id="@+id/action_adminFragment_to_userListFragment"
                app:destination="@id/userListFragment" />
            <!-- Actions to other admin sub-sections like DataManagementFragment if they are separate fragments -->
        </fragment>

        <!-- Secondary / Detail Destinations -->
        <dialog <!-- Or fragment if full screen is preferred -->
            android:id="@+id/addEditTransactionFragment"
            android:name="com.example.app.ui.transactions.AddEditTransactionFragment"
            android:label="Ajouter/Modifier Transaction"
            tools:layout="@layout/fragment_add_edit_transaction">
            <argument
                android:name="transactionId"
                app:argType="long"
                android:defaultValue="-1L" /> <!-- -1L for new transaction -->
        </dialog>

        <dialog
            android:id="@+id/addEditEmployeeFragment"
            android:name="com.example.app.ui.employees.AddEditEmployeeFragment"
            android:label="Ajouter/Modifier Employé"
            tools:layout="@layout/fragment_add_edit_employee">
            <argument
                android:name="employeeId"
                app:argType="long"
                android:defaultValue="-1L" />
        </dialog>

        <fragment <!-- Or DialogFragment -->
            android:id="@+id/salaryHistoryFragment"
            android:name="com.example.app.ui.employees.SalaryHistoryFragment"
            android:label="Historique des Salaires"
            tools:layout="@layout/fragment_salary_history">
            <argument
                android:name="employeeId"
                app:argType="long"
                android:defaultValue="-1L" /> <!-- Optional: -1L for all, or specific employee ID -->
        </fragment>

        <dialog
            android:id="@+id/addEditShareholderFragment"
            android:name="com.example.app.ui.shareholders.AddEditShareholderFragment"
            android:label="Ajouter/Modifier Actionnaire"
            tools:layout="@layout/fragment_add_edit_shareholder">
            <argument
                android:name="shareholderId"
                app:argType="long"
                android:defaultValue="-1L" />
        </dialog>

        <fragment <!-- Or DialogFragment -->
            android:id="@+id/dividendHistoryFragment"
            android:name="com.example.app.ui.shareholders.DividendHistoryFragment"
            android:label="Historique des Dividendes"
            tools:layout="@layout/fragment_dividend_history">
            <argument
                android:name="shareholderId"
                app:argType="long"
                android:defaultValue="-1L" /> <!-- Optional -->
        </fragment>

        <fragment
            android:id="@+id/userListFragment"
            android:name="com.example.app.ui.admin.UserListFragment"
            android:label="Liste des Utilisateurs"
            tools:layout="@layout/fragment_user_list">
            <action
                android:id="@+id/action_userListFragment_to_addEditUserFragment"
                app:destination="@id/addEditUserFragment" />
        </fragment>

        <dialog
            android:id="@+id/addEditUserFragment"
            android:name="com.example.app.ui.admin.AddEditUserFragment"
            android:label="Ajouter/Modifier Utilisateur"
            tools:layout="@layout/fragment_add_edit_user">
            <argument
                android:name="userId"
                app:argType="long"
                android:defaultValue="-1L" />
        </dialog>

        <!-- Login Destination -->
        <fragment
            android:id="@+id/loginFragment"
            android:name="com.example.app.ui.auth.LoginFragment"
            android:label="Connexion"
            tools:layout="@layout/fragment_login">
            <action
                android:id="@+id/action_loginFragment_to_dashboardFragment"
                app:destination="@id/dashboardFragment"
                app:popUpTo="@id/loginFragment"
                app:popUpToInclusive="true" />
        </fragment>

    </navigation>
    ```
    *Note: `<dialog>` tags are used for destinations that are preferably DialogFragments. If they are full-screen fragments, use `<fragment>`.*
    *The `android:label` attribute is used by the Navigation Component to automatically update Toolbar titles.*

## 3. Toolbar & Up Navigation

*   **Toolbar Title:** The `android:label` for each fragment destination in `nav_graph.xml` will be automatically used by the Navigation Component to set the Toolbar title when navigating to that screen. This requires setting up the `NavController` with the `Toolbar` (e.g., using `NavigationUI.setupWithNavController(toolbar, navController, appBarConfiguration)`).
*   **Up Navigation (Back Arrow):**
    *   The Navigation Component automatically handles the display of the Up arrow (back arrow) in the `Toolbar` for non-top-level destinations.
    *   `AppBarConfiguration` is used to define which destinations are considered top-level (e.g., those in the Navigation Drawer). For these, the hamburger icon will be shown instead of the Up arrow.
    *   When the Up arrow is pressed, `navController.navigateUp()` is called, which navigates to the previous destination on the back stack.

## 4. Logout Process

*   **Location:**
    *   A "Logout" or "Déconnexion" menu item can be added to the Navigation Drawer's menu file (e.g., `drawer_menu.xml`).
    *   Alternatively, it can be placed in an options menu in the `Toolbar` (overflow menu).
*   **Actions on Logout:**
    1.  **Clear Session:** The ViewModel or a dedicated `AuthManager` class clears all session data from `SharedPreferences` (e.g., `userId`, `username`, `isLoggedIn` flag set to `false`).
    2.  **Navigate to Login:** The `NavController` navigates to the `LoginFragment`.
    3.  **Clear Back Stack:** To prevent the user from navigating back to authenticated screens via the system back button after logging out, the navigation action to `LoginFragment` must clear the back stack.
        *   Example action from any fragment to login:
            ```xml
            <action
                android:id="@+id/action_global_logout_to_loginFragment"
                app:destination="@id/loginFragment"
                app:popUpTo="@id/nav_graph" <!-- Pop up to the root of the graph -->
                app:popUpToInclusive="true" />
            ```
        *   This action can be defined globally in `nav_graph.xml` or triggered programmatically.

## 5. Conditional Navigation (Login)

*   **Startup Logic:** This logic typically resides in `MainActivity`'s `onCreate` method or in a dedicated `LauncherActivity`.
*   **Process:**
    1.  Check `SessionManager` (or similar) if a valid user session exists (e.g., `isLoggedIn` is true and `userId` is present).
    2.  **If Not Authenticated:**
        *   The `NavHostFragment`'s `startDestination` should ideally be `loginFragment`. Or, if `dashboardFragment` is the start destination for authenticated users, programmatically navigate to `loginFragment`.
        *   `navController.navigate(R.id.loginFragment)` (if `dashboardFragment` is default and user is not logged in).
    3.  **If Authenticated:**
        *   If `loginFragment` is the `startDestination`, navigate to `dashboardFragment` and clear `loginFragment` from the back stack:
            `navController.navigate(R.id.action_loginFragment_to_dashboardFragment)`
        *   If `dashboardFragment` is already the `startDestination` (and `nav_graph.xml` is set up this way perhaps for development), no explicit navigation might be needed, but it's cleaner to have a single entry point (`loginFragment` or a splash/dispatcher fragment) that decides where to go.

*   **Alternative: Splash/Dispatcher Fragment as Start Destination:**
    *   A common pattern is to have a `SplashFragment` (with no UI or just a logo) as the `app:startDestination`.
    *   In `SplashFragment`'s `onViewCreated` or `onResume`, check authentication status.
    *   Navigate to `LoginFragment` or `DashboardFragment` accordingly, clearing `SplashFragment` from the back stack.
    ```kotlin
    // In SplashFragment
    // if (authManager.isUserLoggedIn()) {
    //    findNavController().navigate(R.id.action_splashFragment_to_dashboardFragment)
    // } else {
    //    findNavController().navigate(R.id.action_splashFragment_to_loginFragment)
    // }
    ```
    *   The actions from `SplashFragment` would use `app:popUpTo="@id/splashFragment"` and `app:popUpToInclusive="true"`.

This structure provides a robust and maintainable navigation system for the application.
