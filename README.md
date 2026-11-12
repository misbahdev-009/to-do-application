# To-Do List REST API

A basic CRUD To-Do API built with **FastAPI**, **PyMongo** and **MongoDB Atlas**.

## 1. MongoDB Atlas setup

1. Sign up at https://www.mongodb.com/cloud/atlas and create a **free (M0) cluster**.
2. **Database Access → Add New Database User**: choose *Password* authentication, set a
   username and password, and give it *Read and write to any database*.
3. **Network Access → Add IP Address**:
   - For development, click **Add Current IP Address**, or use `0.0.0.0/0` (allow from anywhere).
   - Don't use `0.0.0.0/0` in production.
4. **Database → Connect → Drivers → Python**, then copy the connection string:
   `mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority`
5. Replace `<username>` and `<password>`. If the password contains special characters
   (`@ : / ? #`), URL-encode them (e.g. `@` becomes `%40`).
6. The `todo_db` database and `todos` collection are created automatically on the first insert.

## 2. Local setup

```bash
git clone <your-repo> && cd todo-api

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env            # then edit .env with your MONGO_URI and DB_NAME
```

## 3. Run the server

```bash
uvicorn app.main:app --reload
```

- API base: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## 4. API reference

| Method | Endpoint          | Description        | Success |
|--------|-------------------|--------------------|---------|
| POST   | `/api/todos`      | Create a task      | 201     |
| GET    | `/api/todos`      | List all tasks     | 200     |
| GET    | `/api/todos/{id}` | Get one task       | 200     |
| PUT    | `/api/todos/{id}` | Update a task      | 200     |
| DELETE | `/api/todos/{id}` | Delete a task      | 200     |

`GET /api/todos` also accepts optional `?status=pending|completed`, `?skip=0` and `?limit=100`.

Errors: `400` (invalid ObjectId or validation failure), `404` (not found), `500` (database/server error).

### Create: `POST /api/todos`

```bash
curl -X POST http://127.0.0.1:8000/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk, eggs, bread"}'
```

Response `201`:

```json
{
  "id": "6733a1f2e4b0c9a1d2f3b4c5",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "status": "pending",
  "created_at": "2026-11-12T10:30:00.123000Z"
}
```

### List: `GET /api/todos`

```bash
curl http://127.0.0.1:8000/api/todos
curl "http://127.0.0.1:8000/api/todos?status=completed"
```

### Get one: `GET /api/todos/{id}`

```bash
curl http://127.0.0.1:8000/api/todos/6733a1f2e4b0c9a1d2f3b4c5
```

### Update: `PUT /api/todos/{id}`

```bash
curl -X PUT http://127.0.0.1:8000/api/todos/6733a1f2e4b0c9a1d2f3b4c5 \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "status": "completed"}'
```

### Delete: `DELETE /api/todos/{id}`

```bash
curl -X DELETE http://127.0.0.1:8000/api/todos/6733a1f2e4b0c9a1d2f3b4c5
```

Response `200`:

```json
{ "message": "Todo deleted successfully", "id": "6733a1f2e4b0c9a1d2f3b4c5" }
```

### Error examples

Invalid ID, `GET /api/todos/123` gives `400`:

```json
{ "error": { "status": 400, "message": "'123' is not a valid ObjectId (expected 24-character hex string)." } }
```

Empty title, `POST /api/todos` with `{"title": "   "}` gives `400`:

```json
{
  "error": {
    "status": 400,
    "message": "Validation failed",
    "details": [{ "field": "title", "message": "Value error, title must not be empty" }]
  }
}
```

Unknown ID gives `404`:

```json
{ "error": { "status": 404, "message": "Todo with id '6733a1f2e4b0c9a1d2f3b4c5' not found." } }
```