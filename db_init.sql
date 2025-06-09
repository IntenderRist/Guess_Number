CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    player_name TEXT NOT NULL UNIQUE,
    level INTEGER NOT NULL,
    attempts INTEGER NOT NULL,
    record_date DATETIME NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
