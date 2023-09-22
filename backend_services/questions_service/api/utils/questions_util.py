import database as db

def is_valid_complexity(complexity):
    valid_complexities =['Easy', 'Medium', 'Hard']
    return complexity in valid_complexities

def qid_exists(qid):
    cur = db.execute_sql_read_fetchone("SELECT EXISTS (SELECT 1 FROM questions WHERE question_id = %s)",
                                       params=(qid,))
    return cur[0]

def title_exists(title):
    cur = db.execute_sql_read_fetchone("SELECT EXISTS (SELECT 1 FROM questions WHERE title = %s)",
                                       params=(title,))
    return cur[0]

def check_duplicate_title(qid, title):
    cur = db.execute_sql_read_fetchone("SELECT EXISTS (SELECT 1 FROM questions WHERE title = %s AND question_id != %s)",
                                       params=(title, qid,))
    return cur[0]