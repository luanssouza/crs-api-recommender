CREATE TABLE dialog(id INT PRIMARY KEY, telegramId INT, age INT, authorization TINYINT, property VARCHAR(50), object VARCHAR(50) createdAt TIMESTAMP, updatedAt TIMESTAMP);

CREATE TABLE recommendation(id INT PRIMARY KEY, doialogId INT, movieId INT, imdbId VARCHAR(10), properties JSON, requested TINYINT, createdAt TIMESTAMP);

CREATE TABLE explanation(recommendationId INT, doialogId INT, movieId INT, imdbId VARCHAR(10), properties JSON, createdAt TIMESTAMP);

CREATE TABLE answer(id INT, dialogId INT, ask TINYINT, answer VARCHAR (100), createdAt TIMESTAMP);