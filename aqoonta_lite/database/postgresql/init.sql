-- database/postgresql/init.sql

-- Create table for lessons
CREATE TABLE lessons (
    id SERIAL PRIMARY KEY,
    topic VARCHAR(100),
    title VARCHAR(200),
    content TEXT
);

-- Create table for quizzes
CREATE TABLE quizzes (
    id SERIAL PRIMARY KEY,
    lesson_id INTEGER REFERENCES lessons(id),
    question TEXT,
    option_a TEXT,
    option_b TEXT,
    option_c TEXT,
    option_d TEXT,
    correct_option CHAR(1)
);

-- Insert sample lesson
INSERT INTO lessons (topic, title, content) VALUES
('finance', 'What is Money?', 'Money is a medium of exchange...');

-- Insert sample quiz
INSERT INTO quizzes (lesson_id, question, option_a, option_b, option_c, option_d, correct_option) VALUES
(1, 'What is the primary function of money?', 'To buy stocks', 'To serve as a medium of exchange', 'To store gold', 'To trade cows', 'B');