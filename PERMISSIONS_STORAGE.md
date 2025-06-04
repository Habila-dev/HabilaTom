# Permissions and File Storage Strategy

This document outlines the Android permissions required by the application and the strategy for data and file storage.

## 1. Required Android Permissions

*   **Internet:**
    *   The application, as currently defined, operates primarily offline. No features explicitly require internet access (e.g., cloud sync, fetching external data).
    *   Therefore, the `android.permission.INTERNET` permission is **not needed** at this stage. If future features require internet connectivity, this permission will need to be added to the `AndroidManifest.xml`.

*   **File Storage (for Android 10 / API 29 and above - Scoped Storage):**
    *   **Scoped Storage:** Modern Android versions use Scoped Storage, which enhances user privacy and control over file access.
        *   **App-Specific Storage:** The application can read and write files to its own dedicated directories (internal and external app-specific storage) without requiring any special permissions. The SQLite database and SharedPreferences will reside here.
        *   **Shared Storage (Exports):** For saving files like Excel reports or database backups to shared locations where the user can easily access them (e.g., `Downloads` directory, cloud storage providers), the **Storage Access Framework (SAF)** will be used.
            *   `ACTION_CREATE_DOCUMENT`: This intent allows the user to select a location and name for a new file. It does not require direct `WRITE_EXTERNAL_STORAGE` permission for common user-accessible directories.
            *   `ACTION_OPEN_DOCUMENT`: Used for importing files (e.g., database restore), allowing the user to pick a file.

*   **File Storage (for Android 9 / API 28 and below - Legacy Storage):**
    *   The project's `minSdkVersion` is API 21 (Android 5.0 Lollipop). For devices running Android 9 (API 28) or older, Scoped Storage is not enforced by default.
    *   If saving files (exports, backups) to public shared storage (e.g., the root of the external storage or public directories like `Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)`) directly without SAF on these older versions, the following permission would be required:
        *   `android.permission.WRITE_EXTERNAL_STORAGE` (This also implicitly grants `READ_EXTERNAL_STORAGE`).
    *   **Recommendation:** To maintain consistency and better security practices, prioritize using SAF for all Android versions if feasible for export/import. If direct legacy storage access is implemented as a fallback or specific requirement for older OS versions, this permission must be declared in `AndroidManifest.xml` with a `android:maxSdkVersion="28"` attribute to ensure it's only requested on older devices.
        ```xml
        <uses-permission
            android:name="android.permission.WRITE_EXTERNAL_STORAGE"
            android:maxSdkVersion="28" />
        ```
    *   However, given SAF's capabilities, it's generally better to rely on it across all supported API levels for user-initiated file saving to shared locations.

*   **Notification Permission (Android 13 / API 33 and above):**
    *   The application currently does not define features that require sending notifications (e.g., reminders, task completion alerts).
    *   Therefore, the `android.permission.POST_NOTIFICATIONS` permission is **not needed** at this stage. If notification features are added in the future, this permission will be required for devices running Android 13 or higher.

## 2. Requesting Permissions

*   **Runtime Permissions:** If `WRITE_EXTERNAL_STORAGE` is deemed necessary for older OS versions (API 23-28), it is a "dangerous" permission and must be requested at runtime.
    *   **In-Context Requests:** Permissions should be requested when the user first attempts to use a feature that requires it (e.g., when tapping an "Export" button that might use legacy storage methods).
    *   **Explanation:** Provide a clear explanation to the user why the permission is needed before showing the system permission dialog. If the user denies the permission (and especially if they select "Don't ask again"), the app should handle this gracefully (e.g., disable the feature, show an informative message).
*   **SAF:** The Storage Access Framework does not require runtime permission prompts for accessing user-chosen locations; the user interaction with the file picker itself serves as consent.

## 3. Data Storage Strategy

*   **Application Data (SQLite Database):**
    *   The main application database (`AppDatabase.db`, managed by Room) will be stored in the app's **private internal storage directory**:
        ` /data/data/your.package.name/databases/ `
    *   This location is secure, private to the application, and automatically cleaned up when the app is uninstalled. It requires no special permissions.

*   **User Configuration/Session Data:**
    *   `SharedPreferences` will be used for storing:
        *   User session information (e.g., `userId`, `username`, `isLoggedIn` flag, `userRole`).
        *   Simple application settings or user preferences.
    *   This data is also stored in the app's private internal storage directory and requires no special permissions.

## 4. File Exports (Excel, Database Backups)

*   **Storage Location:**
    *   **Storage Access Framework (SAF):** This is the **recommended method** for all user-initiated exports.
        *   When the user chooses to export a file (Excel report or database backup), the app will launch an `ACTION_CREATE_DOCUMENT` intent.
        *   The user then selects the destination directory (e.g., `Downloads`, a specific folder on their device, cloud storage providers integrated with SAF) and confirms or changes the proposed file name.
    *   **Benefits of SAF:**
        *   No direct storage permissions (`WRITE_EXTERNAL_STORAGE`) are needed for this on Android 10+.
        *   Gives users full control over where their files are saved.
        *   More secure as the app only gets write access to the specific URI chosen by the user.

*   **File Naming Convention:**
    *   **Excel Reports:** `[AppName]_[ReportName]_[Date].xlsx`
        *   Example: `HabilaGestion_Transactions_2023-10-27.xlsx`, `HabilaGestion_SalaryReport_2023-11.xlsx`
    *   **Database Backups:** `[AppName]_Backup_[Date]_[Time].db`
        *   Example: `HabilaGestion_Backup_20231027_153000.db`
        *   Using a detailed timestamp helps in identifying and managing multiple backup files.

*   **MIME Types (for SAF Intents):**
    *   **Excel (.xlsx):** `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
    *   **Database Backup (.db):** `application/octet-stream` (generic binary) or `application/x-sqlite3` (more specific, though `octet-stream` is widely compatible for user saving).

## 5. File Imports (Database Restore)

*   **Source Location:**
    *   **Storage Access Framework (SAF):** This is the **recommended method**.
        *   When the user chooses to restore data, the app will launch an `ACTION_OPEN_DOCUMENT` intent.
        *   The user selects the database backup file (`.db`) from their device storage or cloud providers.
    *   The app will receive a URI for the selected file, from which it can read the data.

*   **MIME Types (for SAF `ACTION_OPEN_DOCUMENT` intent):**
    *   `application/octet-stream` and/or `application/x-sqlite3` to filter for appropriate database files.

*   **Security Note:**
    *   As stated in `UI_SCREENS_PART3.md`, before proceeding with a database restore, a **critical warning dialog** must be displayed to the user. This dialog will clearly state that the restore operation will overwrite all current application data and is irreversible, requiring explicit user confirmation.

By adhering to Scoped Storage principles and utilizing the Storage Access Framework, the application will ensure better user privacy, control, and compatibility with modern Android versions.
