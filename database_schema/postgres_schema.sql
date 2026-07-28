
CREATE TABLE IF NOT EXISTS orders_order (
    id BIGSERIAL PRIMARY KEY,
    book_id BIGINT NOT NULL, -- Logical reference to catalog_book(id) in MySQL
    quantity INT NOT NULL DEFAULT 1 CHECK (quantity > 0),
    total NUMERIC(10, 2) NOT NULL CHECK (total >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS orders_review (
    id BIGSERIAL PRIMARY KEY,
    book_id BIGINT NOT NULL, -- Logical reference to catalog_book(id) in MySQL
    reviewer_name VARCHAR(255) NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 

-- Insert Orders (referencing book_ids 1, 2, and 3 from MySQL)
INSERT INTO orders_order (book_id, quantity, total, created_at) VALUES
(1, 2, 89.98, CURRENT_TIMESTAMP - INTERVAL '2 days'),
(2, 1, 14.99, CURRENT_TIMESTAMP - INTERVAL '1 day'),
(1, 1, 44.99, CURRENT_TIMESTAMP);

-- Insert Reviews (referencing book_ids 1 and 2 from MySQL)
INSERT INTO orders_review (book_id, reviewer_name, rating, comment, created_at) VALUES
(1, 'Alice Johnson', 5, 'Must-read for every developer. Improved my coding practices dramatically!', CURRENT_TIMESTAMP - INTERVAL '3 days'),
(1, 'Bob Smith', 4, 'Great insights on refactoring, though some Java examples are a bit dated.', CURRENT_TIMESTAMP - INTERVAL '1 day'),
(2, 'Charlie Brown', 5, 'Timeless classic. Scarily relevant to modern society.', CURRENT_TIMESTAMP);


SELECT 
    book_id,
    COUNT(*) AS total_reviews,
    ROUND(AVG(rating), 2) AS average_rating,
    MIN(rating) AS lowest_rating,
    MAX(rating) AS highest_rating
FROM orders_review
GROUP BY book_id
ORDER BY average_rating DESC;
