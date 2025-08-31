# Project Setup and Architecture

## 1. Target Android Version

*   **Minimum SDK Version:** API 21 (Android 5.0 Lollipop) - This ensures a wide reach, covering a vast majority of Android devices while still allowing the use of many modern Android features.
*   **Target/Compile SDK Version:** Latest stable version of the Android SDK. This allows the application to leverage the latest features and optimizations provided by the Android platform.

## 2. Programming Language

*   **Primary Language:** Kotlin. Kotlin is the recommended language for modern Android development due to its conciseness, safety features (null safety), and excellent interoperability with Java.

## 3. Core Architectural Pattern

*   **Pattern:** Model-View-ViewModel (MVVM)
*   **Explanation:**
    *   **Model:** Represents the data layer of the application. This includes:
        *   **Repositories:** Manage data sources (network, local database) and provide a clean API for data access to the ViewModels.
        *   **Room Persistence Library:** Used for local data storage (SQLite).
        *   **Data Sources:** (e.g., Retrofit for network calls, if applicable in the future).
    *   **View:** Represents the UI layer of the application. This consists of:
        *   **Activities & Fragments:** Display data to the user and handle user interactions. They observe data changes from the ViewModel and update the UI accordingly.
    *   **ViewModel:** Acts as a bridge between the Model and the View. It holds and manages UI-related data in a lifecycle-conscious way. It exposes data to the View (typically via LiveData or StateFlow) and contains the business logic to process user inputs and fetch/update data from the Model. ViewModels survive configuration changes, preventing data loss.

## 4. Database Solution

*   **Technology:** SQLite with the Room Persistence Library.
*   **Suitability:**
    *   **Offline Storage:** Excellent for storing structured data locally on the device, enabling offline access.
    *   **Structured Data:** Provides a robust way to organize and manage data in tables.
    *   **Query Validation at Compile Time:** Room validates SQL queries at compile time, reducing runtime errors and improving code reliability.
    *   **Abstraction:** Offers a higher-level abstraction over SQLite, making database interactions more straightforward and less error-prone.

## 5. Key Android Libraries

*   **UI:**
    *   **Android Jetpack's Material Components:** For implementing modern Material Design UIs with pre-built, customizable components (buttons, cards, dialogs, etc.).
*   **Navigation:**
    *   **Android Jetpack's Navigation Component:** To manage in-app navigation, handle deep linking, and provide a consistent navigation experience. Simplifies fragment transactions and argument passing.
*   **Asynchronous Operations:**
    *   **Kotlin Coroutines:** For managing background threads and simplifying asynchronous code. Essential for performing network requests, database operations, or any long-running tasks without blocking the main thread.
*   **ViewModels:**
    *   **Android Jetpack's ViewModel:** To store and manage UI-related data in a lifecycle-conscious way, surviving configuration changes.
*   **Observable Data:**
    *   **LiveData / StateFlow (Kotlin):**
        *   **LiveData:** Lifecycle-aware observable data holder. Use when you need simple, lifecycle-aware data observation, especially within the Android Framework components.
        *   **StateFlow:** A hot, observable flow that emits the current and subsequent state updates. Suitable for more complex scenarios and better integration with Kotlin Flows. Recommended for new development, especially if using Coroutines extensively.
*   **Charting:**
    *   **MPAndroidChart:** A powerful and widely-used charting library for Android that supports various chart types, including pie and line charts. It's well-maintained and offers extensive customization options.
        *   *Alternative:* Consider [AnyChart Android](https://github.com/AnyChart/AnyChart-Android) or [ECharts](https://github.com/apache/echarts) (if a web-based solution within a WebView is acceptable for more complex visualizations, though native is preferred).
*   **Excel Generation:**
    *   **Apache POI:** A robust Java library for working with Microsoft Office documents, including Excel (`.xlsx`).
        *   **Considerations:**
            *   **Performance:** Generating large Excel files directly on a mobile device can be resource-intensive (CPU and memory). This might lead to performance issues or even `OutOfMemoryError`s.
            *   **Android-Friendly Wrappers:** Investigate if there are any actively maintained Android-specific wrappers or libraries that optimize Apache POI for mobile or offer a more streamlined API. If not, direct use of Apache POI is possible but requires careful handling of resources, potentially offloading complex generation to background threads and providing user feedback.
            *   **Alternatives for Large Data:** For very large datasets, consider alternative approaches like exporting to CSV (which is simpler and less resource-intensive) or generating the Excel file on a backend server if possible.
*   **View Interaction:**
    *   **View Binding:** Recommended for most cases. It generates a binding class for each XML layout file, providing direct, type-safe access to views. This eliminates `findViewById` calls, reducing boilerplate and preventing null pointer exceptions due to incorrect view IDs.
    *   **Data Binding:** Can be used for more complex scenarios where you need to bind UI components in your layout to data sources in your app using a declarative format rather than programmatically. It's more powerful than View Binding but also has a steeper learning curve. Use when two-way data binding or complex binding expressions are needed.
