CREATE TABLE IF NOT EXISTS news (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    date DATETIME NOT NULL,
    body TEXT,
    deleted BOOLEAN DEFAULT 0
);

CREATE TABLE IF NOT EXISTS comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    news_id INT,
    title VARCHAR(255),
    date DATETIME,
    comment TEXT,
    FOREIGN KEY (news_id) REFERENCES news(id)
);
