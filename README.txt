Конечно. Вот та же документация, переведённая на русский язык, без форматирования Markdown. Все примеры API и JSON остаются на английском.



Название: Документация по API управления новостями

Технологии  
- Backend: Flask (Python)  
- База данных: MySQL  
- Модель данных: статьи и комментарии, связанные через news_id  
- Возможности: Полный CRUD, мягкое удаление, защита от SQL-инъекций



Инструкция по установке

1. Установите зависимости:
pip install flask mysql-connector-python

2. Укажите параметры подключения к MySQL в db_config:
db_config = {
    "user": "root",
    "password": "your_password",
    "host": "localhost",
    "port": 3306,
    "database": "news_management"
}

3. Запустить сервер:
python FirstFile.py

Или в блоке:
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)



Маршруты API

GET /api  
Описание: Возвращает все статьи с комментариями. Показываются только те, у которых deleted = 0.

Пример ответа:
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



GET /api/news/<int:id>  
Описание: Возвращает одну статью по ID вместе с комментариями.

Пример ответа:
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

Ошибки:  
404 — если статья не найдена

  

POST /api/news  
Описание: Создаёт новую статью (опционально с комментариями).

Пример тела запроса:
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

Пример ответа:
{
  "message": "Article created",
  "news_id": 5
}

Ошибки:  
500 — ошибка базы данных или валидации

  

PUT /api/news/<int:id>  
Описание: Обновляет существующую статью по ID.

Пример тела запроса:
{
  "title": "Updated Title",
  "body": "Updated body content."
}

Пример ответа:
{
  "message": "Article successfully updated"
}

Ошибки:  
404 — если статья не найдена

  

DELETE /api/news/<int:id>  
Описание: Мягкое удаление статьи — устанавливает deleted = 1.

Пример ответа:
{
  "message": "Article successfully deleted"
}

Ошибки:  
404 — если статья не найдена

  

Описание структуры базы данных

Таблица news:  
- id (INT, AUTO_INCREMENT, PRIMARY KEY)  
- title (TEXT)  
- body (TEXT)  
- date (DATETIME)  
- deleted (BOOLEAN)

Таблица comments:  
- id (INT, AUTO_INCREMENT, PRIMARY KEY)  
- news_id (INT, FOREIGN KEY → news.id)  
- title (TEXT)  
- comment (TEXT)  
- date (DATETIME)

  

Заметки по безопасности

- Все SQL-запросы используют параметризованные подстановки (%s) для защиты от SQL-инъекций  
- Нет вставки данных в запросы через f-строки  
- Все входящие данные проверяются (например, проверка наличия ключа "comments")

  

Если хочешь, могу сохранить это как текстовый файл или дополнительно объяснить любую часть.