

CREATE DATABASE IF NOT EXISTS catalog_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE catalog_db;


CREATE TABLE IF NOT EXISTS catalog_category (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE IF NOT EXISTS catalog_author (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    bio TEXT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 
CREATE TABLE IF NOT EXISTS catalog_book (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author_id BIGINT NOT NULL,
    category_id BIGINT NULL,
    price DECIMAL(10, 2) NOT NULL,
    description TEXT NULL,
    CONSTRAINT fk_book_author 
        FOREIGN KEY (author_id) REFERENCES catalog_author (id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_book_category 
        FOREIGN KEY (category_id) REFERENCES catalog_category (id) 
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--

-- Insert Categories
INSERT INTO catalog_category (id, name) VALUES
(1, 'Computer Science & Software Engineering'),
(2, 'Fiction & Literature'),
(3, 'Data Science & Artificial Intelligence');

-- Insert Authors
INSERT INTO catalog_author (id, name, bio) VALUES
(1, 'Robert C. Martin', 'Renowned software engineer, author of Clean Code and agile software craftsman.'),
(2, 'George Orwell', 'English novelist, essayist, journalist and critic famous for dystopian fiction.'),
(3, 'Aurélien Géron', 'Former hands-on machine learning team lead at Google.');

-- Insert Books
INSERT INTO catalog_book (id, title, author_id, category_id, price, description) VALUES
(1, 'Clean Code: A Handbook of Agile Software Craftsmanship', 1, 1, 44.99, 'A classic guide to writing readable, maintainable, and refactored code.'),
(2, '1984', 2, 2, 14.99, 'A chilling dystopian novel depicting a totalitarian regime and Big Brother.'),
(3, 'Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow', 3, 3, 59.99, 'Practical guide to building intelligent systems with Python ML libraries.');

--
SELECT 
    b.id AS book_id,
    b.title AS book_title,
    a.name AS author_name,
    c.name AS category_name,
    b.price
FROM catalog_book b
INNER JOIN catalog_author a ON b.author_id = a.id
LEFT JOIN catalog_category c ON b.category_id = c.id
ORDER BY b.price DESC;
