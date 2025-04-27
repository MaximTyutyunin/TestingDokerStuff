FROM python:3.13-slim

COPY comments.json /
COPY news.json /
COPY FirstFile.py /

RUN pip install Flask==3.1.0
RUN pip install mysql-connector-python==9.2.0

EXPOSE 8080

CMD python3 FirstFile.py