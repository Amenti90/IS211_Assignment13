CREATE TABLE IF NOT EXISTS students (
    id       INTEGER         PRIMARY KEY AUTOINCREMENT,
    firstname VARCHAR (50)  NOT NULL,
    lastname VARCHAR (50)   NOT NULL
);


CREATE TABLE IF NOT EXISTS quizzes (
    id              INTEGER      PRIMARY KEY AUTOINCREMENT,
    subject         VARCHAR (50),
    no_of_questions INTEGER,
    date            DATE
);


CREATE TABLE IF NOT EXISTS results (
    id            INTEGER  PRIMARY KEY AUTOINCREMENT,
    student_id       INTEGER  REFERENCES students (id),
    quiz_id       INTEGER  REFERENCES quizes (id),
    score         INT (3)     NOT NULL,
    UNIQUE (
        student_id,
        quiz_id
    )
)
