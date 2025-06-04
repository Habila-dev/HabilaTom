# Data Layer Definition

This document outlines the data layer components for the Android application, including Kotlin data classes, Room DAOs, the Repository pattern, and database initialization.

## 1. Kotlin Data Classes

These data classes represent the entities in our application. They will be used by Room to define the database schema.

```kotlin
// Common imports for annotations (assuming they are in a package like com.example.app.database)
// import androidx.room.Entity
// import androidx.room.PrimaryKey
// import androidx.room.TypeConverters // If using type converters for Date, Enum etc.
// import java.util.Date // Or use Long for timestamps

// --- User Entity ---
@Entity(tableName = "users")
data class User(
    @PrimaryKey(autoGenerate = true)
    val userId: Long = 0,
    val username: String,
    val passwordHash: String, // Store hashed passwords, never plain text
    val role: String, // e.g., "Admin", "User" - could be an Enum
    val createdDate: Long, // Timestamp (e.g., System.currentTimeMillis())
    val lastLogin: Long?, // Nullable timestamp
    val isActive: Boolean = true
)

// --- Transaction Entity ---
enum class TransactionType {
    ENTREE, // Income/Revenue
    SORTIE  // Expense/Payment
}

@Entity(tableName = "transactions")
// Consider adding indices for frequently queried columns like 'date' or 'category'
// @Indices(value = [Index(value = ["date"]), Index(value = ["category"])])
data class Transaction(
    @PrimaryKey(autoGenerate = true)
    val transactionId: Long = 0,
    val date: Long, // Timestamp
    // @TypeConverters(TransactionTypeConverter::class) // Example if using Enum with TypeConverter
    val type: TransactionType, // "Entrée" or "Sortie"
    val amount: Double,
    val description: String,
    val category: String // e.g., "Salaire", "Loyer", "Fournitures"
)

// --- Employee Entity ---
@Entity(tableName = "employees")
data class Employee(
    @PrimaryKey(autoGenerate = true)
    val employeeId: Long = 0,
    val firstName: String,
    val lastName: String,
    val position: String,
    val monthlySalary: Double,
    val hireDate: Long, // Timestamp
    val isActive: Boolean = true,
    val notes: String? = null
)

// --- Shareholder Entity ---
@Entity(tableName = "shareholders")
data class Shareholder(
    @PrimaryKey(autoGenerate = true)
    val shareholderId: Long = 0,
    val firstName: String,
    val lastName: String,
    val socialShares: Int, // Number of social shares
    val acquisitionDate: Long, // Timestamp
    val isActive: Boolean = true,
    val notes: String? = null
)
```
*Note: For `Date` fields, using `Long` to store timestamps (e.g., `System.currentTimeMillis()`) is common and avoids timezone issues. Room can store `Long` directly. If `java.util.Date` objects are preferred, a `TypeConverter` would be needed.*
*For `TransactionType` Enum, a `TypeConverter` would be necessary to tell Room how to store and retrieve it (e.g., as a String).*

## 2. Room DAOs (Data Access Objects)

DAOs provide an abstraction layer for accessing the database. Each entity will have a corresponding DAO interface.

### UserDao
```kotlin
// import androidx.lifecycle.LiveData
// import androidx.room.*
// import kotlinx.coroutines.flow.Flow

@Dao
interface UserDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: User): Long // Returns new rowId

    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insertUsers(users: List<User>): List<Long>

    @Update
    suspend fun updateUser(user: User)

    @Delete
    suspend fun deleteUser(user: User)

    @Query("SELECT * FROM users WHERE userId = :id")
    fun getUserById(id: Long): Flow<User?>

    @Query("SELECT * FROM users WHERE username = :username")
    fun getUserByUsername(username: String): Flow<User?>

    @Query("SELECT * FROM users ORDER BY username ASC")
    fun getAllUsers(): Flow<List<User>>

    @Query("SELECT COUNT(*) FROM users")
    suspend fun getUserCount(): Int // For checking if admin needs to be created
}
```

### TransactionDao
```kotlin
@Dao
interface TransactionDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertTransaction(transaction: Transaction): Long

    @Update
    suspend fun updateTransaction(transaction: Transaction)

    @Delete
    suspend fun deleteTransaction(transaction: Transaction)

    @Query("SELECT * FROM transactions WHERE transactionId = :id")
    fun getTransactionById(id: Long): Flow<Transaction?>

    @Query("SELECT * FROM transactions ORDER BY date DESC")
    fun getAllTransactions(): Flow<List<Transaction>>

    @Query("SELECT * FROM transactions WHERE date BETWEEN :startDate AND :endDate ORDER BY date DESC")
    fun getTransactionsByDateRange(startDate: Long, endDate: Long): Flow<List<Transaction>>

    @Query("SELECT * FROM transactions WHERE type = :transactionType ORDER BY date DESC")
    fun getTransactionsByType(transactionType: TransactionType): Flow<List<Transaction>>

    @Query("SELECT * FROM transactions WHERE category = :category ORDER BY date DESC")
    fun getTransactionsByCategory(category: String): Flow<List<Transaction>>
}
```

### EmployeeDao
```kotlin
@Dao
interface EmployeeDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertEmployee(employee: Employee): Long

    @Update
    suspend fun updateEmployee(employee: Employee)

    @Delete
    suspend fun deleteEmployee(employee: Employee)

    @Query("SELECT * FROM employees WHERE employeeId = :id")
    fun getEmployeeById(id: Long): Flow<Employee?>

    @Query("SELECT * FROM employees ORDER BY lastName ASC, firstName ASC")
    fun getAllEmployees(): Flow<List<Employee>>

    @Query("SELECT * FROM employees WHERE isActive = 1 ORDER BY lastName ASC, firstName ASC")
    fun getActiveEmployees(): Flow<List<Employee>>
}
```

### ShareholderDao
```kotlin
@Dao
interface ShareholderDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertShareholder(shareholder: Shareholder): Long

    @Update
    suspend fun updateShareholder(shareholder: Shareholder)

    @Delete
    suspend fun deleteShareholder(shareholder: Shareholder)

    @Query("SELECT * FROM shareholders WHERE shareholderId = :id")
    fun getShareholderById(id: Long): Flow<Shareholder?>

    @Query("SELECT * FROM shareholders ORDER BY lastName ASC, firstName ASC")
    fun getAllShareholders(): Flow<List<Shareholder>>

    @Query("SELECT * FROM shareholders WHERE isActive = 1 ORDER BY lastName ASC, firstName ASC")
    fun getActiveShareholders(): Flow<List<Shareholder>>
}
```
*Note: DAOs use `suspend` for one-shot operations (insert, update, delete) to be called from coroutines. For queries that observe data changes, they return `Flow` (or `LiveData`). `Flow` is generally preferred in Kotlin-centric applications.*

## 3. Repository Pattern

Repositories abstract the data sources (DAOs in this case) and provide a clean API for ViewModels to interact with data. They can manage whether data comes from a local database, a remote server, or a cache.

### Role of Repositories:
*   **Decoupling:** Decouple ViewModels from the specific data source implementation (Room DAOs).
*   **Centralized Data Logic:** Centralize data access logic, making it easier to manage and test.
*   **Multiple Data Sources:** Can combine data from multiple sources (e.g., local DB and network API). For now, we focus on local DB.
*   **Clean API:** Provide a simple, use-case-driven API to the ViewModels.

### Example: UserRepository

**Interface (`UserRepository.kt`):**
```kotlin
// import com.example.app.database.User
// import kotlinx.coroutines.flow.Flow

interface UserRepository {
    fun getUserById(id: Long): Flow<User?>
    fun getUserByUsername(username: String): Flow<User?>
    fun getAllUsers(): Flow<List<User>>
    suspend fun insertUser(user: User): Long
    suspend fun updateUser(user: User)
    suspend fun deleteUser(user: User)
    suspend fun getUserCount(): Int
    // Potentially: suspend fun createDefaultAdminUserIfNoneExists()
}
```

**Implementation (`UserRepositoryImpl.kt`):**
```kotlin
// import com.example.app.database.User
// import com.example.app.database.UserDao
// import kotlinx.coroutines.flow.Flow
// import javax.inject.Inject // If using Hilt/Dagger for DI

class UserRepositoryImpl /* @Inject constructor */ (
    private val userDao: UserDao
) : UserRepository {

    override fun getUserById(id: Long): Flow<User?> {
        return userDao.getUserById(id)
    }

    override fun getUserByUsername(username: String): Flow<User?> {
        return userDao.getUserByUsername(username)
    }

    override fun getAllUsers(): Flow<List<User>> {
        return userDao.getAllUsers()
    }

    override suspend fun insertUser(user: User): Long {
        return userDao.insertUser(user)
    }

    override suspend fun updateUser(user: User) {
        userDao.updateUser(user)
    }

    override suspend fun deleteUser(user: User) {
        userDao.deleteUser(user)
    }

    override suspend fun getUserCount(): Int {
        return userDao.getUserCount()
    }
}
```
*Similar repositories would be created for `Transaction`, `Employee`, and `Shareholder` entities, possibly grouped logically (e.g., `FinancialDataRepository` for Transactions).*

## 4. Database Initialization & Default Admin User

The Room database needs to be instantiated once per application lifecycle, typically in the `Application` class or via a dependency injection framework.

### Database Class (`AppDatabase.kt`)
```kotlin
// import android.content.Context
// import androidx.room.*
// import androidx.sqlite.db.SupportSQLiteDatabase
// import kotlinx.coroutines.CoroutineScope
// import kotlinx.coroutines.Dispatchers
// import kotlinx.coroutines.launch
// import java.util.concurrent.Executors

@Database(
    entities = [User::class, Transaction::class, Employee::class, Shareholder::class],
    version = 1, // Increment on schema changes
    exportSchema = false // Set to true for production apps to export schema for migrations
)
// @TypeConverters(TransactionTypeConverter::class) // Register global type converters
abstract class AppDatabase : RoomDatabase() {

    abstract fun userDao(): UserDao
    abstract fun transactionDao(): TransactionDao
    abstract fun employeeDao(): EmployeeDao
    abstract fun shareholderDao(): ShareholderDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null

        fun getDatabase(
            context: Context,
            coroutineScope: CoroutineScope // For pre-population
        ): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "app_database" // Database file name
                )
                .addCallback(AppDatabaseCallback(context, coroutineScope)) // Add callback here
                .fallbackToDestructiveMigration() // For development; use proper migration for production
                .build()
                INSTANCE = instance
                instance
            }
        }
    }
}

// --- Callback for Pre-populating Data (Default Admin) ---
private class AppDatabaseCallback(
    private val context: Context, // Or inject UserDao directly if using DI
    private val scope: CoroutineScope
) : RoomDatabase.Callback() {

    override fun onCreate(db: SupportSQLiteDatabase) {
        super.onCreate(db)
        AppDatabase.INSTANCE?.let { database ->
            scope.launch(Dispatchers.IO) { // Run in a background coroutine
                populateInitialData(database.userDao())
            }
        }
    }

    // Called when the database has been opened.
    // Can also be used for initial data check if onCreate is missed for some reason
    // or if you want to check on every app start (though less efficient).
    /*
    override fun onOpen(db: SupportSQLiteDatabase) {
        super.onOpen(db)
        AppDatabase.INSTANCE?.let { database ->
            scope.launch(Dispatchers.IO) {
                // Example: Check if admin exists, if not, create.
                // This is more robust if onCreate might be missed or if you want to ensure admin exists.
                // val userDao = database.userDao()
                // if (userDao.getUserCount() == 0) {
                //    populateInitialData(userDao)
                // }
            }
        }
    }
    */

    suspend fun populateInitialData(userDao: UserDao) {
        // Check if users already exist (e.g., if onCreate is called again after data wipe but before app restart)
        if (userDao.getUserCount() == 0) {
            // TODO: Implement proper password hashing (e.g., using bcrypt or SCrypt)
            // For now, using a placeholder. **NEVER store plain text passwords.**
            val placeholderHashedPassword = "hashed_admin_password" // Replace with actual hashing

            val adminUser = User(
                username = "admin",
                passwordHash = placeholderHashedPassword,
                role = "Admin",
                createdDate = System.currentTimeMillis(),
                lastLogin = null,
                isActive = true
            )
            userDao.insertUser(adminUser)
        }
    }
}
```
*   **Password Hashing:** The `passwordHash` for the default admin user **must** be generated using a strong hashing algorithm (e.g., BCrypt, SCrypt, or Argon2). Storing plain text or weakly hashed passwords is a major security risk. The actual hashing implementation will need to be added.
*   **Dependency Injection:** In a production app, a dependency injection framework like Hilt or Koin would typically manage the database instance and DAOs.
*   **CoroutineScope:** A `CoroutineScope` (e.g., `ApplicationScope` provided by Hilt or a custom one) is passed to `getDatabase` to launch the coroutine for pre-populating data.
*   **Migrations:** For production applications, `fallbackToDestructiveMigration()` should be replaced with proper migration strategies (`addMigrations()`) when the database schema changes.
*   The `onCreate` callback is only invoked the first time the database is created on the device. If the app data is cleared, `onCreate` will run again. The `onOpen` callback is invoked every time the database is opened. For ensuring the admin user, checking in `onOpen` (if `userDao.getUserCount() == 0`) can be more robust, or ensuring the `populateInitialData` logic is idempotent. For simplicity, `onCreate` is used here for the initial setup.
