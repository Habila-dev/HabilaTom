# User Authentication Module

This document outlines the components and logic for user authentication within the Android application.

## 1. Login Screen UI Elements

The login screen will be the primary entry point for users to access the application.

*   **Layout:** A `ConstraintLayout` or `LinearLayout` can be used for structuring the elements.
*   **UI Components:**
    *   **App Logo/Name:** An `ImageView` to display the application's logo or a `TextView` for the application name, positioned at the top of the screen for branding.
    *   **Username Input:** An `EditText` (e.g., `id: etUsername`) for the user to enter their username.
        *   `hint`: "Username"
        *   `inputType`: `text`
    *   **Password Input:** An `EditText` (e.g., `id: etPassword`) for the user to enter their password.
        *   `hint`: "Password"
        *   `inputType`: `textPassword` (to mask the input)
    *   **Login Button:** A `Button` (e.g., `id: btnLogin`) that the user clicks to attempt authentication.
        *   `text`: "Login"
    *   **Error Message Display:** A `TextView` (e.g., `id: tvError`) initially hidden (`visibility: GONE` or `INVISIBLE`) to display login-related error messages (e.g., "Invalid username or password", "Username cannot be empty").
    *   **Loading Indicator:** A `ProgressBar` (e.g., `id: pbLoading`) initially hidden, to be shown during the authentication attempt.

## 2. Credential Validation Logic

This process is triggered when the user taps the "Login" button.

1.  **Retrieve Input:** The `LoginActivity` (or `LoginFragment`) retrieves the text from `etUsername` and `etPassword`.
2.  **Basic Client-Side Validation:**
    *   Check if `username` is empty. If so, display an error in `tvError` (e.g., "Username is required") and halt.
    *   Check if `password` is empty. If so, display an error in `tvError` (e.g., "Password is required") and halt.
3.  **ViewModel Interaction:** The View (Activity/Fragment) calls a method in the `LoginViewModel` (e.g., `loginUser(username, password)`).
4.  **Authentication Process (within ViewModel and Repository):**
    *   The `LoginViewModel` initiates a coroutine to call the `UserRepository` (e.g., `userRepository.getUserByUsername(username)`).
    *   **User Fetch:** The `UserRepository` fetches the `User` object from the Room database via `UserDao`.
    *   **User Not Found:** If no user is found with the given username, the `UserRepository` returns `null` or an equivalent error indicator. The `LoginViewModel` updates its state to reflect "User not found," and the View displays an appropriate error message.
    *   **Password Verification:**
        *   If a user is found, the `UserRepository` (or a dedicated authentication service/utility class) compares the provided `password` with the `passwordHash` stored in the fetched `User` object.
        *   **Security Note:** This comparison **must** be done using a secure password hashing scheme (e.g., BCrypt, SCrypt, Argon2). The application should store only hashed passwords. When the user enters a password, it should be hashed using the same algorithm and parameters (including the salt, which should be stored alongside the hash or derived if using a scheme like BCrypt that embeds it) and then compared to the stored hash. **Never compare plain text passwords directly.**
    *   **Incorrect Password:** If the password hash does not match, the `LoginViewModel` updates its state to reflect "Incorrect password," and the View displays an error message (typically a generic "Invalid username or password" to avoid revealing which part was incorrect).
    *   **Successful Login:**
        *   If the password hash matches and the user account is `isActive`, the login is successful.
        *   The `LoginViewModel` will then trigger an update to the user's `lastLogin` timestamp. This involves calling a method in the `UserRepository` (e.g., `userRepository.updateUser(user.copy(lastLogin = System.currentTimeMillis()))`).
        *   The `LoginViewModel` updates its state to reflect "Login successful."
        *   Session information is stored (see Section 3).
        *   The View navigates the user to the main part of the application.
    *   **Inactive User:** If the user is found and password matches, but `user.isActive` is `false`, the login should be denied, and an appropriate message displayed (e.g., "Account is inactive").

## 3. Session Management

Session management ensures that the user remains logged in across app uses until they explicitly log out or the session expires (if implementing session expiry, which is not detailed here but could be an extension).

*   **Storage Mechanism:** `SharedPreferences` is suitable for storing simple session data.
    *   Create a wrapper class (e.g., `SessionManager`) to handle `SharedPreferences` access, making it easier to manage keys and perform operations.
*   **Data to Store:**
    *   `userId`: The ID of the logged-in user.
    *   `username`: The username of the logged-in user.
    *   `userRole`: The role of the user (e.g., "Admin", "User") to control access to certain features.
    *   `isLoggedIn`: A boolean flag indicating whether a user is currently logged in.
    *   (Optional) A session token if interacting with a backend API that uses tokens.
*   **Checking Active Session on Startup:**
    *   When the application starts (typically in a launcher `Activity` or the `onCreate` of the `MainActivity`), the `SessionManager` is queried to check if `isLoggedIn` is true.
    *   If `true`, and potentially other session data like `userId` is valid, the application bypasses the `LoginActivity` and navigates directly to the main screen/dashboard.
    *   If `false` or session data is missing/invalid, the user is directed to the `LoginActivity`.
*   **Logout Process:**
    *   A "Logout" option should be available to the user (e.g., in a settings menu or profile screen).
    *   When the user initiates logout:
        *   The `SessionManager` clears all stored session data from `SharedPreferences` (e.g., set `isLoggedIn` to `false`, remove `userId`, `username`, `userRole`).
        *   The application navigates the user back to the `LoginActivity`.
        *   Any sensitive data in ViewModels or other components related to the user session should be cleared.

## 4. ViewModel Interaction (`LoginViewModel`)

The `LoginViewModel` is responsible for handling the logic of the login screen and managing its state.

*   **Dependencies:**
    *   `UserRepository`: To interact with user data (fetch user, update last login).
    *   `SessionManager`: To save session details upon successful login.
    *   (Potentially) A password hashing utility if the comparison logic is complex and centralized there.
*   **Key Responsibilities:**
    *   Expose methods to be called by the View (e.g., `loginUser(username: String, password: String)`).
    *   Perform input validation (or delegate to a utility class).
    *   Call the `UserRepository` to authenticate the user.
    *   Manage and expose the authentication state to the View.
*   **State Exposure with `LiveData` or `StateFlow`:**
    *   The `LoginViewModel` will use `LiveData` or `StateFlow` to communicate the authentication status and other relevant UI state to the `LoginActivity`/`LoginFragment`.
    *   Example states:
        *   `AuthenticationState.IDLE`: Initial state.
        *   `AuthenticationState.LOADING`: Login attempt is in progress.
        *   `AuthenticationState.SUCCESS`: Login successful.
        *   `AuthenticationState.ERROR_USER_NOT_FOUND`: User does not exist.
        *   `AuthenticationState.ERROR_INVALID_PASSWORD`: Password incorrect.
        *   `AuthenticationState.ERROR_ACCOUNT_INACTIVE`: Account is disabled.
        *   `AuthenticationState.ERROR_EMPTY_USERNAME`: Username field was empty.
        *   `AuthenticationState.ERROR_EMPTY_PASSWORD`: Password field was empty.
        *   `AuthenticationState.ERROR_NETWORK`: (If applicable for future remote auth) Network error.
    *   The View observes this state and updates the UI accordingly (e.g., show/hide `ProgressBar`, display error messages, navigate to the next screen).

**Example `LoginViewModel` Structure (Conceptual):**
```kotlin
// class LoginViewModel(
//     private val userRepository: UserRepository,
//     private val sessionManager: SessionManager,
//     // private val passwordHasher: PasswordHasher // If using a dedicated hasher
// ) : ViewModel() {

//     private val _authenticationState = MutableStateFlow<AuthenticationState>(AuthenticationState.IDLE)
//     val authenticationState: StateFlow<AuthenticationState> = _authenticationState.asStateFlow()

//     fun loginUser(username: String, password: String) {
//         if (username.isBlank()) {
//             _authenticationState.value = AuthenticationState.ERROR_EMPTY_USERNAME
//             return
//         }
//         if (password.isBlank()) {
//             _authenticationState.value = AuthenticationState.ERROR_EMPTY_PASSWORD
//             return
//         }

//         _authenticationState.value = AuthenticationState.LOADING
//         viewModelScope.launch {
//             val user = userRepository.getUserByUsername(username).firstOrNull() // Assuming Flow from DAO

//             if (user == null) {
//                 _authenticationState.value = AuthenticationState.ERROR_USER_NOT_FOUND
//             } else if (!user.isActive) {
//                 _authenticationState.value = AuthenticationState.ERROR_ACCOUNT_INACTIVE
//             } else {
//                 // val isValidPassword = passwordHasher.verifyPassword(password, user.passwordHash, user.salt)
//                 // For this example, direct comparison is implied by the description,
//                 // but actual implementation needs secure hashing and verification.
//                 // This part would be more complex with proper hashing.
//                 if (/* password matches user.passwordHash after hashing 'password' */) {
//                     userRepository.updateUser(user.copy(lastLogin = System.currentTimeMillis()))
//                     sessionManager.saveSession(user.userId, user.username, user.role)
//                     _authenticationState.value = AuthenticationState.SUCCESS
//                 } else {
//                     _authenticationState.value = AuthenticationState.ERROR_INVALID_PASSWORD
//                 }
//             }
//         }
//     }
// }

// sealed class AuthenticationState {
//     object IDLE : AuthenticationState()
//     object LOADING : AuthenticationState()
//     object SUCCESS : AuthenticationState()
//     data class ERROR(val message: String) : AuthenticationState() // Generic error
//     object ERROR_USER_NOT_FOUND : AuthenticationState()
//     object ERROR_INVALID_PASSWORD : AuthenticationState()
//     object ERROR_ACCOUNT_INACTIVE : AuthenticationState()
//     object ERROR_EMPTY_USERNAME : AuthenticationState()
//     object ERROR_EMPTY_PASSWORD : AuthenticationState()
// }
```
This provides a comprehensive definition of the User Authentication Module.
