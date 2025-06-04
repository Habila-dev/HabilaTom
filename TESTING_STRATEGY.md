# Testing Strategy

This document outlines the testing strategy for the Android application to ensure its quality, correctness, and maintainability.

## 1. Overall Testing Goals

*   **Ensure Application Correctness and Stability:** Verify that the application functions as expected under various conditions and that critical business logic is implemented accurately.
*   **Facilitate Refactoring and Future Development:** Provide a safety net for code changes, allowing developers to refactor and add new features with confidence that existing functionality remains intact.
*   **Verify Key Business Logic and User Flows:** Ensure that core operations like financial calculations, transaction processing, salary payments, and user authentication work correctly.
*   **Improve Code Quality:** The process of writing tests often leads to better-designed, more modular, and more maintainable code.

## 2. Testing Levels

The application will employ a multi-layered testing approach, often visualized as a testing pyramid:

*   **Unit Tests:** Form the base of the pyramid. These are small, fast tests that verify individual components (classes, methods) in isolation.
*   **Integration Tests:** Sit in the middle. These tests verify the interaction between two or more components of the application.
*   **UI Tests (End-to-End Tests):** At the top of the pyramid. These tests validate complete user flows by interacting with the application's UI. They are typically slower and more complex to write and maintain.

## 3. Unit Testing Strategy

*   **Scope:**
    *   **ViewModels:**
        *   Test business logic (e.g., input validation, data processing for display).
        *   Verify data transformations and calculations.
        *   Test state changes and emissions from `LiveData` or `StateFlow` (e.g., UI states for loading, success, error).
        *   Test interactions with Repositories by using mock Repository implementations.
    *   **Repositories:**
        *   Test data handling logic (e.g., fetching, saving, updating, deleting data).
        *   Verify interactions with DAOs and other potential data sources (e.g., network services in the future). Use mock DAOs or a real DAO with an in-memory Room database.
    *   **Utility Classes/Functions:**
        *   Test any standalone helper functions or classes that contain pure business logic or data manipulation routines (e.g., date formatters, calculation utilities).
    *   **DAOs (Data Access Objects):**
        *   While Room generates much of the DAO implementation, basic query correctness (e.g., inserting data and then retrieving it to ensure the query works) can be tested using an in-memory Room database. These tests help validate SQL queries defined in `@Query` annotations.
    *   **Business Logic (as defined in `BUSINESS_LOGIC.md`):**
        *   Calculations for financial summaries, salary processing logic, and dividend distribution rules should be thoroughly unit tested, likely within the ViewModels or dedicated use case classes that house this logic.

*   **Tools:**
    *   **JUnit 4 or JUnit 5:** The primary testing framework for writing tests.
    *   **Mockito (or MockK for Kotlin):** For creating mock objects to isolate the component under test from its dependencies. MockK is generally preferred for Kotlin projects due to its idiomatic Kotlin API.
    *   **Robolectric (Optional):** Can be used if some ViewModel or Repository tests have unavoidable Android framework dependencies (e.g., `Context`) and running them on a local JVM (rather than an emulator/device) is desired. However, strive to minimize direct Android framework dependencies in these layers.
    *   **AndroidX Test Libraries:**
        *   `core-testing`: For `InstantTaskExecutorRule` to test `LiveData` synchronously.
        *   Turbine (from CashApp) or Kotlin Coroutines Test utilities (`TestCoroutineDispatcher`, `runBlockingTest`): For testing `StateFlow` and other coroutine-based logic.
        *   `androidx.room:room-testing`: For using `Room.inMemoryDatabaseBuilder` to create an in-memory SQLite database for testing DAOs and Repository interactions with DAOs.

*   **Location:** Unit tests will be placed in the `app/src/test/java/your/package/name/` directory. These tests run on the local JVM.

## 4. Integration Testing Strategy

Integration tests verify the interaction points between different parts of the app.

*   **Scope Examples:**
    *   **ViewModel-Repository-DAO Flow:** Test the complete flow from a ViewModel action, through the Repository, to the DAO, and interacting with an in-memory Room database. For example, call a ViewModel method to save a transaction, then verify through the Repository (or directly via DAO) that the transaction was correctly stored in the in-memory database.
    *   **Authentication Flow:** Test the `UserRepository`'s interaction with `UserDao` and an in-memory database for user registration (if applicable) and login credential verification.
    *   **Database Migrations:** Test Room database migrations to ensure schema changes are handled correctly and data is preserved.

*   **Tools:**
    *   **AndroidX Test Libraries:** `androidx.test.ext:junit` (for AndroidJUnit4 runner), `androidx.test.espresso:espresso-core` (though not directly for UI interaction here, the test environment setup is useful).
    *   **JUnit 4:** Test framework.
    *   **In-memory Room Database:** (`Room.inMemoryDatabaseBuilder`) to provide a real database environment for testing DAO and Repository integration.
    *   **Kotlin Coroutines Test utilities:** For managing coroutines in tests.

*   **Location:** Integration tests are typically instrumented tests and will be placed in the `app/src/androidTest/java/your/package/name/` directory. They run on an Android emulator or physical device.

## 5. UI Testing Strategy

UI tests validate user flows by interacting with the application's user interface.

*   **Scope (Critical User Flows):**
    *   **Authentication:** Login with valid/invalid credentials, logout process.
    *   **Core CRUD Operations:**
        *   Adding a new transaction and verifying it appears in the list.
        *   Editing an existing employee's details and verifying the changes are reflected.
        *   Deleting a transaction and confirming its removal.
    *   **Business Processes:**
        *   Initiating and confirming a salary payment for an employee and verifying the creation of a corresponding 'Sortie' transaction.
        *   Distributing dividends and checking for transaction creation.
    *   **Navigation:**
        *   Navigating to different screens via the Navigation Drawer.
        *   Testing Up navigation from detail screens.
    *   **Filtering:** Applying filters on the Transactions screen and verifying the list updates correctly.
    *   **Data Export (Basic Check):** Triggering an export and verifying that the SAF file picker appears (full file content validation is complex for UI tests and better covered at lower levels or manually).

*   **Tools:**
    *   **Espresso:** Android's primary framework for UI testing. Used for interacting with UI elements (Buttons, EditTexts, RecyclerViews) and making assertions.
    *   **UI Automator (Less Likely Needed):** Useful if tests need to interact with elements outside the app's UI (e.g., system dialogs not handled by Espresso, notifications). Unlikely to be a primary tool for this application.
    *   **AndroidX Test Libraries:**
        *   `ActivityScenario`: For launching and controlling Activities in tests.
        *   `FragmentScenario`: For testing Fragments in isolation.
        *   `androidx.test.espresso.contrib`: For Espresso actions on `RecyclerView`, `DatePicker`, etc.
    *   **Hilt Testing Utilities (if Hilt is used for DI):** For providing test doubles or managing dependencies in UI tests.

*   **Best Practices:**
    *   **Idling Resources:** Implement or use existing Idling Resources to ensure Espresso waits for asynchronous operations (like network requests, database operations, or background calculations) to complete before proceeding with test actions or assertions. This is crucial for test reliability.
    *   **Focused Tests:** Keep UI tests concise and focused on a specific user flow or feature. Avoid overly long tests that try to cover too much.
    *   **Page Object Model (POM):** Consider using the Page Object Model pattern (or similar screen robot patterns) to create reusable, maintainable UI tests. This involves creating classes that represent screens (or parts of screens) and encapsulate the logic for interacting with their UI elements.
    *   **Test Data:** Manage test data carefully. Use a consistent starting state for tests, potentially by clearing app data before test runs or using specific test accounts/data.

*   **Location:** UI tests are instrumented tests and will be placed in the `app/src/androidTest/java/your/package/name/` directory.

## 6. Code Coverage

*   **Goal:** Aim for a reasonable code coverage percentage (e.g., 70-80%) for unit tests, particularly for ViewModels, Repositories, and any classes containing critical business logic. While 100% coverage is often impractical, critical paths should be well-covered.
*   **Tools:** **JaCoCo** (Java Code Coverage) is a standard tool that can be integrated into the Android Gradle build process to generate code coverage reports. These reports help identify untested parts of the codebase.

## 7. When to Write Tests

*   **Alongside Development:** Ideally, tests (especially unit tests) should be written concurrently with the feature development. Test-Driven Development (TDD) is a practice where tests are written before the actual code, but even without strict TDD, writing tests as part of the development cycle is beneficial.
*   **New Features:** All new features should be accompanied by a suite of tests (unit, integration, and UI as appropriate).
*   **Bug Fixes:** When a bug is fixed, write a test that reproduces the bug to ensure it's actually fixed and to prevent regressions in the future.
*   **Refactoring:** Existing tests provide the confidence to refactor code, ensuring that changes do not break existing functionality.

By implementing this testing strategy, the application will be more robust, easier to maintain, and adaptable to future changes.
