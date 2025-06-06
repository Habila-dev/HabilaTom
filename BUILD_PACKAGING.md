# Build & Packaging Outline

This document outlines the strategy for building, signing, and packaging the Android application for release.

## 1. Build Types & Flavors

*   **Build Types:** Android Gradle builds use build types to define how the app is packaged. The two standard build types are:
    *   **`debug`:** Used for development and testing. Typically includes debugging symbols, is not minified, and may be signed with a generic debug key provided by Android Studio.
    *   **`release`:** Used for generating the production version of the app that will be distributed to users. This build should be signed with a private release key, and code should be shrunk and obfuscated.

*   **Product Flavors (Brief Mention):**
    *   Product flavors allow creating different versions of the app from the same codebase (e.g., free vs. paid versions, different branding, or targeting different environments like staging vs. production APIs).
    *   For the initial scope of this application, product flavors are likely **not required**. If the application evolves to have such distinct versions, flavors can be introduced.

## 2. Generating a Signed APK/AAB for Release

To distribute the application, it must be signed with a private release key.

*   **Keystore Creation:**
    *   A private signing key is stored in a **keystore** (a `.jks` or `.keystore` file).
    *   This keystore can be generated using:
        *   **Android Studio:** Via `Build > Generate Signed Bundle / APK...`, then choosing "APK" or "Android App Bundle", and then "Create new..." for the key store.
        *   **`keytool` command-line utility:** (Part of the Java Development Kit).
            ```bash
            keytool -genkey -v -keystore my-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias my-key-alias
            ```
    *   **Critical Importance:** The keystore file, its password, the key alias, and the key password **must be stored securely and backed up**.
        *   **Losing the keystore means you will not be able to publish updates to your app on Google Play under the same app listing.**
        *   It's recommended to use strong, unique passwords.

*   **Configuring Gradle for Release Builds:**
    *   The app-level `build.gradle.kts` (or `build.gradle`) file needs to be configured to use the signing key for release builds.
    *   **Securely Store Credentials:** Keystore passwords, key alias, and key password should **not** be hardcoded directly in `build.gradle`. Instead, store them in:
        *   `gradle.properties` file in the user's Gradle home directory (`~/.gradle/gradle.properties`).
        *   Project-specific `gradle.properties` (ensure this file is added to `.gitignore` to prevent committing it to version control).
        *   Environment variables, read by the Gradle build script.

    *   **Conceptual `build.gradle.kts` example:**
        ```kotlin
        // In app/build.gradle.kts

        android {
            // ... other configurations

            signingConfigs {
                create("release") {
                    storeFile = file(System.getenv("MYAPP_RELEASE_STORE_FILE") ?: project.property("myapp.release.storeFile").toString())
                    storePassword = System.getenv("MYAPP_RELEASE_STORE_PASSWORD") ?: project.property("myapp.release.storePassword").toString()
                    keyAlias = System.getenv("MYAPP_RELEASE_KEY_ALIAS") ?: project.property("myapp.release.keyAlias").toString()
                    keyPassword = System.getenv("MYAPP_RELEASE_KEY_PASSWORD") ?: project.property("myapp.release.keyPassword").toString()
                }
            }

            buildTypes {
                getByName("release") {
                    isMinifyEnabled = true // Enable R8/ProGuard
                    proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
                    signingConfig = signingConfigs.getByName("release")
                    // Other release-specific configurations
                }
                getByName("debug") {
                    // Debug-specific configurations
                    applicationIdSuffix = ".debug" // Optional: differentiate debug builds
                    versionNameSuffix = "-debug"   // Optional
                }
            }
        }
        ```
    *   **Example `gradle.properties` (add to `.gitignore`):**
        ```properties
        myapp.release.storeFile=/path/to/your/my-release-key.jks
        myapp.release.storePassword=your_store_password
        myapp.release.keyAlias=your_key_alias
        myapp.release.keyPassword=your_key_password
        ```

*   **ProGuard/R8 for Code Shrinking & Obfuscation:**
    *   **Enable:** Set `isMinifyEnabled = true` in the `release` build type block. This activates R8 (the default code shrinker in Android Gradle Plugin, successor to ProGuard).
    *   **Benefits:**
        *   **Shrinking:** Removes unused code and resources, reducing the app's size.
        *   **Obfuscation:** Renames classes, fields, and methods with short, meaningless names, making it harder to reverse-engineer the application.
    *   **Configuration (`proguard-rules.pro`):**
        *   R8 is generally good at figuring out what code is needed, but sometimes specific rules are required.
        *   Default rules are provided by `proguard-android-optimize.txt`.
        *   Custom rules in `proguard-rules.pro` are necessary for:
            *   Classes accessed via reflection (e.g., some serialization libraries).
            *   Ensuring Room entities, DAOs, and database classes are not removed or obfuscated in a way that breaks Room.
            *   Keeping annotations needed at runtime.
            *   Native method names if using JNI.
            *   Any third-party libraries that require specific ProGuard/R8 rules (check their documentation).
        *   Thorough testing of the release build is crucial after enabling minification.

*   **Build Process:**
    *   **Using Android Studio:**
        1.  Go to `Build > Generate Signed Bundle / APK...`.
        2.  Choose "Android App Bundle" (recommended for Google Play) or "APK".
        3.  Select the module.
        4.  Provide the keystore path, passwords, and key alias.
        5.  Choose the "release" build variant.
        6.  Click "Finish" or "Create".
    *   **Using Gradle Command Line:**
        *   For Android App Bundle (`.aab`): `./gradlew bundleRelease`
        *   For APK (`.apk`): `./gradlew assembleRelease`

## 3. Android App Bundle (.aab) vs. APK (.apk)

*   **APK (Android Package Kit):**
    *   A single file containing all the app's code, resources, assets, certificates, and manifest file.
    *   Can be directly installed on an Android device (sideloading).
    *   Universal APKs contain resources for all device configurations, making them larger.

*   **AAB (Android App Bundle):**
    *   A **publishing format** for Google Play. You upload the AAB to the Play Console.
    *   Google Play then uses Dynamic Delivery to generate and serve optimized APKs tailored to each user's device configuration (e.g., screen density, CPU architecture, language).
    *   **Benefits:**
        *   **Smaller App Size:** Users download only the code and resources needed for their specific device, resulting in smaller downloads and less storage space used.
        *   **Required for new apps on Google Play (since August 2021).**
        *   Enables advanced features like Play Feature Delivery (on-demand delivery of features).

*   **Recommendation:**
    *   **For Google Play distribution:** Generate and upload an **Android App Bundle (.aab)**.
    *   **For direct distribution/sideloading (e.g., internal testing, enterprise distribution):** A traditional **APK (.apk)** might be more straightforward, although Google Play can also generate installable APKs from an AAB for testing purposes using `bundletool` or via internal app sharing.

## 4. Versioning

Proper versioning is crucial for app updates. This is managed in the app-level `build.gradle.kts` or `build.gradle` file.

*   **`versionCode`:**
    *   An integer that **must be incremented** with each new version of the app released to Google Play or otherwise distributed.
    *   Used internally by Android and Google Play to determine if one version is newer than another.
    *   Example: `1`, `2`, `3`, ...

*   **`versionName`:**
    *   A user-facing string that represents the version of the app (e.g., "1.0", "1.0.1-beta", "2.0-rc1").
    *   This is what users see in the "About app" section or on the Google Play store listing.
    *   Example: `"1.0"`, `"1.1"`, `"2.0"`

*   **Management:**
    ```kotlin
    // In app/build.gradle.kts
    android {
        defaultConfig {
            // ...
            versionCode = 1
            versionName = "1.0"
        }
    }
    ```
    *   Increment `versionCode` and update `versionName` appropriately for every release. Maintain a consistent versioning scheme (e.g., Semantic Versioning - Major.Minor.Patch).

## 5. Pre-Release Checklist (High-Level)

Before generating a release build, perform these checks:

*   **Remove/Disable Debugging Code:**
    *   Ensure all `Log.d`, `Log.v`, etc., statements not intended for production are removed or wrapped in conditional blocks (e.g., `if (BuildConfig.DEBUG) { Log.d(...) }`).
    *   Remove any developer-specific settings or test data generation code.
*   **Final Testing:**
    *   Thoroughly test the release build (which has minification enabled) on various devices and Android versions (emulators and physical devices). Pay close attention to areas that might be affected by ProGuard/R8.
    *   Verify all core user flows.
*   **Review App Permissions:** Ensure the `AndroidManifest.xml` only requests permissions that are strictly necessary for the app's functionality.
*   **App Icon & Branding:** Confirm the correct app icon, splash screen (if any), and branding elements are in place.
*   **Secrets/API Keys:** Double-check that no sensitive information (API keys, secrets, etc.) is hardcoded in the app. (While this app is primarily offline, this is a general best practice).
*   **Update Versioning:** Increment `versionCode` and set the correct `versionName` in `build.gradle`.
*   **Review ProGuard/R8 Rules:** Check `proguard-rules.pro` and test if any classes are being incorrectly removed or obfuscated. The `usage.txt` file generated by R8 (in `app/build/outputs/mapping/release/`) can help identify removed code.

This outline provides a solid foundation for building and packaging the application for release.
