# DHP-Project-1

```markdown
## Database Schema

The application uses PostgreSQL. Below is the schema for the main tables:

### Instructors Table

```sql
CREATE TABLE instructors (
    instructor_id SERIAL PRIMARY KEY,
    instructor_name VARCHAR(255) UNIQUE NOT NULL,
    instructor_email VARCHAR(255) NOT NULL
);
```

### Courses Table

```sql
CREATE TABLE courses (
    course_id SERIAL PRIMARY KEY,
    course_name VARCHAR(255),
    instructor_id INT,
    batch_pattern VARCHAR(10),
    UNIQUE (course_name, instructor_id, batch_pattern)
);
```

### Feedback Table

```sql
CREATE TABLE feedback (
    feedback_id SERIAL PRIMARY KEY,
    course_id INT REFERENCES courses(course_id),
    coursecode2 VARCHAR(50),
    studentemaiid VARCHAR(100),
    studentname VARCHAR(100),
    dateOfFeedback DATE,
    week INT,
    instructorEmailID VARCHAR(100),
    question1Rating INT,
    question2Rating INT,
    remarks TEXT
);
```

### Table Relationships

- The `courses` table has a foreign key relationship with the `instructors` table through the `instructor_id` field.
- The `feedback` table has a foreign key relationship with the `courses` table through the `course_id` field.

### Initial Data Setup

The system includes initial data setup for instructors and courses:

#### Instructors Data

```python
insert_instructors_query = """
INSERT INTO instructors (instructor_id, instructor_name, instructor_email)
VALUES
(3, 'Dr. Achal Agrawal', 'achal@sitare.org'),
(4, 'Ms. Preeti Shukla', 'preeti@sitare.org'),
...
ON CONFLICT (instructor_id) DO NOTHING;
"""
```

#### Courses Data

```python
insert_courses_query = """
INSERT INTO courses (course_name, instructor_id, batch_pattern)
VALUES
('Artificial Intelligence', 1, 'su-230'),
('DBMS', 1, 'su-230'),
...
ON CONFLICT (course_name, instructor_id, batch_pattern) DO NOTHING;
"""
```

Tables are created and initial data is inserted when the application starts via the `create_tables_if_not_exists()` function.
```
