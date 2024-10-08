DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS tasks;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE tasks (
  task_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  task TEXT NOT NULL,
  completed INTEGER DEFAULT 0,
  due_date TEXT,
  FOREIGN KEY (user_id) REFERENCES user (id)
)