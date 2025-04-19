from flask import Flask, request
from datetime import datetime
import json
import mysql.connector

app = Flask(__name__)
app.json.sort_keys = False
# Database connection details
db_config = {
    'user': 'root',  # Replace with your MySQL username
    'password': '09qsFG$(^9q',  # Replace with your MySQL password
    'host': 'localhost',  # Or the IP address of your MySQL server
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
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""select  news.title, news.date, body, JSON_ARRAYAGG(JSON_OBJECT('comment', comments.comment, 'title', comments.title))
                            from news_management.news
                            left join
                            news_management.comments on news.id = comments.news_id
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
    # Get new article data from request
    new_article = request.get_json()
    connection = get_db_connection()
    cursor = connection.cursor()
    news_id = None
    try:
        cursor.execute("""
            INSERT INTO news (title, date, body, deleted)
            VALUES (%s, %s, %s, %s)
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


@app.route("/api/news/<int:searched_id>", methods=[
    "DELETE"])  # <id> is only for flask, flask parses data inside @app.route("/api/news/<id>") and fetches "id"
def delete_news_by_id(searched_id):
    # new_article = request.get_json() this line of code makes the endpoint to expect some json body which will break
    # the app because it's the delete method doesnt require json object to be sent --> no one will sent it --. error 415

    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM news WHERE id = %s", (searched_id,))
        data = cursor.fetchall()

        if not data:  # If data is empty, return an error
            return {"error": "News article doesnt exist"}, 404

        cursor.execute(f"""UPDATE  news_management.news 
                            SET deleted = 1
                            WHERE id = %s;""",(searched_id,))

        connection.commit()
        return {"message": "Article successfully deleted"}, 200
    except Exception as e:
        connection.rollback()
        return {"error": str(e)}, 500
    finally:
        cursor.close()
        connection.close()



#
# @app.route("/api")
# def get_news():
#     with open("news.json", "r") as file:
#         news = json.load(file)
#     with open("comments.json", "r") as file:
#         comments = json.load(file)
#
#     result = []
#     for news_article in news["news"]:
#         content_date = datetime.strptime(news_article["date"], "%Y-%m-%dT%H:%M:%S")
#         if news_article["deleted"] == False or content_date <= datetime.now():
#             comments_count = 0
#
#             for comment in comments["comments"]:
#                 if comment["news_id"] == news_article["id"]:
#                     comments_count += 1
#
#             news_article["comments_count"] = comments_count
#             result.append(news_article)
#
#     new_list = sorted(result, key=lambda d: d["date"])
#     return {
#         "news": new_list,
#         "news_count": len(new_list)
#     }
#
# @app.route(
#     "/api/news/<int:searched_id>")  # <id> is only for flask, flask parses data inside @app.route("/api/news/<id>") and fetches "id"
# def get_news_by_id(searched_id):
#     with open("comments.json", "r") as file:
#         comments = json.load(file)
#     with open("news.json", "r") as file:
#         news = json.load(file)
#
#     news_result = []
#     for news_article in news["news"]:
#         if news_article["id"] == searched_id:
#
#             comments_count = 0
#             comments_result = []
#             for comment in comments["comments"]:
#                 if news_article["deleted"] == False and comment["news_id"] == news_article["id"]:
#                     comments_count += 1
#                     comments_result.append(comment)
#
#             news_article["comments"] = comments_result
#             news_article["comments_count"] = comments_count
#             news_result.append(news_article)
#             return news_result
#     # sk about from collections import OrderedDict if I should've used it instead
#     return {"error": "News not found"}, 404
#
# @app.route(
#     "/api/news/<int:searched_id>", methods=[
#         "DELETE"])  # <id> is only for flask, flask parses data inside @app.route("/api/news/<id>") and fetches "id"
# def delete_news_by_id(searched_id):
#     with open("news.json", "r") as file:
#         news = json.load(file)
#
#     """This does NOT create new copies of the news articles. Instead, it builds a dictionary
#     where the values are references to the same dictionaries inside news["news"]."""
#     news_dict = {article["id"]: article for article in news["news"]}
#     news_article = news_dict.get(searched_id)
#     if news_article is None:
#         return {"error": "Article doesn’t exist"}, 404
#
#     news_article["deleted"] = True
#
#     with open("news.json", "w") as file:
#         json.dump(news, file, indent=4)
#
#     return {"message": "Article successfully deleted"}, 200
#
# @app.route("/api/news", methods=["POST"])
# def post_news():
#     with open("news.json", "r") as file:
#         news = json.load(file)
#     with open("comments.json", "r") as file:
#         comments = json.load(file)
#
#     """    new_article = request.get_json()
#
#         comments_dict = {comment["id"]: comment for comment in new_article["comments"]}
#         comments["comments"].append(comments_dict)
#         new_article.pop("comments", None)
#         new_article["date"] = datetime.now().isoformat()  # .strftime("%Y-%m-%dT%H:%M:%S")
#         new_article["deleted"] = False
#
#         news["news"].append(new_article)"""
#     # Get new article data from request
#     new_article = request.get_json()
#
#     # Add comments if they exist
#     if "comments" in new_article:
#         comments["comments"].extend(new_article["comments"])
#         new_article.pop("comments")  # Remove comments from article
#
#     # Set article metadata
#     new_article["date"] = datetime.now().isoformat()
#     new_article["deleted"] = False
#
#     with open("news.json", "w") as file:
#         json.dump(news, file, indent=4)
#
#     with open("comments.json", "w") as file:
#         json.dump(comments, file, indent=4)
#
#     return {"message": "All good"}, 200

# sjdfglsjdfg
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
