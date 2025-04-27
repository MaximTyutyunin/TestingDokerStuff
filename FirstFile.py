from flask import Flask, request
from datetime import datetime
import json
import mysql.connector

'''
по текущему списку задач: 
- [DONE] заставить приложение работать из контейнера 
- [DONE] переписать ридми с .txt на .md 
- [DONE] переписать ридми на английский
- почистить репозиторий от мусора
———
далее что можно еще сделать: 
- написать модульные тесты на pytest с использованием test-containers (если дойдут до этого руки - напиши мне, я тебе сразу готовый шаблон скину) 
- [TODO] сделать docker-compose где будет 2 контейнера : контейнер с приложением и контейнер с базой данных 
- подумать, как мы могли бы внедрить в приложение работу с пользователем и его авторизацию
'''


app = Flask(__name__)
app.json.sort_keys = False
# Database connection details
db_config = {
    'user': 'root',  # Replace with your MySQL username
    'password': '09qsFG$(^9q',  # Replace with your MySQL password
    'host': 'db',  # Or the IP address of your MySQL server
    'port': 3306,  # Default MySQL port
    'database': 'news_management'  # The schema you want to use
}


def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        print("DB connected:", conn.is_connected())
        return conn
    except mysql.connector.Error as e:
        print("Database connection failed:", e)
        raise  # Let your route handle the error

@app.route("/api")
def get_news_db():
    """
    get news with according comments, each news article is sorted by title and date
        - no json required
        - Returns 500 if the article with the given ID doesn't exist.
        - Returns 200 on success.
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""select  news.title, news.date, body, 
                                JSON_ARRAYAGG(JSON_OBJECT('comment', comments.comment, 'title', comments.title))
                            from news_management.news
                            left join news_management.comments on news.id = comments.news_id
                            where news.deleted = 0
                            group by  news.title, news.date, body """)
        data = cursor.fetchall()

        result = []
        for news_article in data:
            result.append({
                "title": news_article[0], "date": news_article[1], "body": news_article[2],
                "comments": json.loads(news_article[3])
            })
        return {
            "news": result,
            # "news_count": len(new_list)
        }
    except Exception as e:
        connection.rollback()
        return {"error": str(e)}, 500
    finally:
        cursor.close()
        connection.close()

@app.route("/api/news/<int:searched_id>")  # <id> is only for flask, flask parses data inside @app.route("/api/news/<id>") and fetches "id"
def get_news_by_id(searched_id):
    """
    get a specific article with ID and sort all its comments by date
        - no json required
        - Returns 500 if the article with the given ID doesn't exist.
        - Returns news article to user on success.
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        query = """SELECT news.title, news.date, news.body,
                      JSON_ARRAYAGG(JSON_OBJECT('comment', comments.comment, 'title', comments.title))
               FROM news
               LEFT JOIN comments ON news.id = comments.news_id
               WHERE news.id = %s
               GROUP BY news.title, news.date, news.body;
        """
        cursor.execute(query, (searched_id,))
        data = cursor.fetchall()

        if not data:  # If data is empty, return an error
            return {"error": "News not found"}, 404

        news_article = data[0]
        result = {
            "title": news_article[0],
            "date": news_article[1],
            "body": news_article[2],
            "comments": json.loads(news_article[3])
        }
        return {"news": result}
    except Exception as e:
        connection.rollback()
        return {"error": str(e)}, 500
    finally:
        cursor.close()
        connection.close()

@app.route("/api/news", methods=["POST"])
def post_news():
    """
    insert new item into the DB , comments go into comments table and news go into the news table
        - Returns 201 when Article created.
    """
    # Get new article data from request
    new_article = request.get_json()
    connection = get_db_connection()
    cursor = connection.cursor()
    news_id = None
    try:
        cursor.execute("""
            insert into news (title, date, body, deleted)
            values (%s, %s, %s, %s)
        """, (new_article["title"], datetime.now().isoformat(), new_article["body"], 0))

        news_id = cursor.lastrowid
        if "comments" in new_article:
            for comment in new_article["comments"]:
                cursor.execute("""
                   insert into comments (news_id, title, date, comment)
                    values (%s, %s, %s, %s)
                """, (news_id, comment["title"], comment["date"], comment["comment"]))
        connection.commit()
        return {"message": "Article created", "news_id": news_id}, 201
    except Exception as e:
        connection.rollback()
        return {"error": str(e)}, 500
    finally:
        cursor.close()
        connection.close()

@app.route("/api/news/<int:searched_id>", methods=["PUT"])
def put_news(searched_id):
    """
    update an item in the DB
     - requires json body
     - Returns 404 if the article with the given ID doesn't exist.
     - Returns 200 on success.
    """
    updated_article = request.get_json()
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("select * from news where id = %s", (searched_id,))
        if not cursor.fetchone():
            return {"error": "Article not found"}, 404

        cursor.execute("""
                   UPDATE news
                   SET title = %s, body = %s, date = %s
                   WHERE id = %s
               """, (updated_article["title"], updated_article["body"], datetime.now().isoformat(), searched_id))

        return {"message": "Article successfully updated"}, 200
    except Exception as e:
        connection.rollback()
        return {"error": str(e)}, 500
    finally:
        cursor.close()
        connection.close()



@app.route("/api/news/<int:searched_id>", methods=["DELETE"])  # <id> is only for flask, flask parses data inside @app.route("/api/news/<id>") and fetches "id"
def delete_news_by_id(searched_id):
    # new_article = request.get_json() this line of code makes the endpoint to expect some json body which will break
    # the app because it's the delete method doesnt require json object to be sent --> no one will sent it --. error 415
    """
    Marks a news article as deleted in the database (soft delete).
    - Does not remove the row from the table.
    - Returns 404 if the article with the given ID doesn't exist.
    - Returns 200 on success.
    - No JSON body is expected for DELETE requests.
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM news WHERE id = %s LIMIT 1", (searched_id,))
        data = cursor.fetchone()

        if not data:  # If data is empty, return an error
            return {"error": "News article doesnt exist"}, 404

        cursor.execute(f"""UPDATE  news_management.news 
                            SET deleted = 1
                            WHERE id = %s; """,(searched_id,))

        connection.commit()
        return {"message": "Article successfully deleted"}, 200
    except Exception as e:
        connection.rollback()
        return {"error": str(e)}, 500
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
