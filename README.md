# News Management API

A simple RESTful API for managing news articles and comments, built with Flask and MySQL.

## Table of Contents
- [Technologies](#technologies)
- [Installation](#installation)
- [API Routes](#api-routes)
- [Database Structure](#database-structure)
- [Security](#security)

## Technologies
- **Backend**: Flask (Python)
- **Database**: MySQL
- **Features**: Full CRUD, soft delete, SQL injection protection

## Installation Instructions

1. Install dependencies:
   ```bash
   pip install flask mysql-connector-python
   ```

2. Specify MySQL connection parameters in `db_config`:
   ```python
   db_config = {
       "user": "root",
       "password": "your_password",
       "host": "localhost",
       "port": 3306,
       "database": "news_management"
   }
   ```

3. Run the server:
   ```bash
   python FirstFile.py
   ```

   Or inside the block:
   ```python
   if __name__ == '__main__':
       app.run(debug=True, host='0.0.0.0', port=8080)
   ```

## API Routes

### `GET /api`
**Description**: Returns all articles with comments. Only those with `deleted = 0` are shown.

**Example response**:
```json
{
  "news": [
    {
      "title": "Sample Title",
      "date": "2025-04-21T10:00:00",
      "body": "Full article content...",
      "comments": [
        {"title": "Comment Title", "comment": "This is a comment"}
      ]
    }
  ]
}
```

---

### `GET /api/news/<int:id>`
**Description**: Returns a single article by ID along with comments.

**Example response**:
```json
{
  "news": {
    "title": "Sample Title",
    "date": "2025-04-21T10:00:00",
    "body": "Full article content...",
    "comments": [
      {"title": "Comment Title", "comment": "This is a comment"}
    ]
  }
}
```

**Errors**:  
- `404` — if the article is not found

---

### `POST /api/news`
**Description**: Creates a new article (optionally with comments).

**Example request body**:
```json
{
  "title": "New Article",
  "body": "This is the body text.",
  "comments": [
    {
      "title": "First Comment",
      "comment": "Nice!",
      "date": "2025-04-21T12:00:00"
    }
  ]
}
```

**Example response**:
```json
{
  "message": "Article created",
  "news_id": 5
}
```

**Errors**:  
- `500` — database or validation error

---

### `PUT /api/news/<int:id>`
**Description**: Updates an existing article by ID.

**Example request body**:
```json
{
  "title": "Updated Title",
  "body": "Updated body content."
}
```

**Example response**:
```json
{
  "message": "Article successfully updated"
}
```

**Errors**:  
- `404` — if the article is not found

---

### `DELETE /api/news/<int:id>`
**Description**: Soft deletes an article — sets `deleted = 1`.

**Example response**:
```json
{
  "message": "Article successfully deleted"
}
```

**Errors**:  
- `404` — if the article is not found

---

## Database Structure Description

### Table: `news`
- `id` (INT, AUTO_INCREMENT, PRIMARY KEY)
- `title` (TEXT)
- `body` (TEXT)
- `date` (DATETIME)
- `deleted` (BOOLEAN)

### Table: `comments`
- `id` (INT, AUTO_INCREMENT, PRIMARY KEY)
- `news_id` (INT, FOREIGN KEY → `news.id`)
- `title` (TEXT)
- `comment` (TEXT)
- `date` (DATETIME)

---

## Security Notes
- All SQL queries use **parameterized substitutions** (`%s`) to protect against SQL injections
- No **f-strings** are used for inserting data into queries
- All incoming data is validated (for example, checking for the presence of the `"comments"` key)

---

Would you like me to also create a finished `.md` file that you can download directly?  
(just tell me if you want that)  
: Malicious input like `"; DROP TABLE users; --` could delete data if not protected.