import psycopg2
class db_crud:
    def __init__(self):
        self.conn = psycopg2.connect(
            host="arjuna.db.elephantsql.com",
            database="bkxwjxhh",
            user="bkxwjxhh",
            password="O5_S6rDOodpP1oB0_k6vN6K0kU5qB1R9")

    def bookdata_insert(self,data):

        cur = self.conn.cursor()
        cur.execute(f"""INSERT INTO book_table VALUES ('{data['isbn']}',
                                                        '{data['itemId']}',
                                                        '{data['category']}',
                                                        '{data['title'].replace('"','').replace("'","")}',
                                                        '{data['author']}',
                                                        '{data['publisher']}',
                                                        '{data['p_date']}',
                                                        {int(data['price'])},
                                                        {int(data['page'])},
                                                        {float(data['avg_score'].strip())},
                                                        '{data['description'].replace('"','').replace("'","")}');""")
            
        self.conn.commit()
        cur.close()
    def review_insert(self,data):
        cur = self.conn.cursor()
        cur.execute(f"""INSERT INTO review_table VALUES ('{data['isbn']}',
                                                        '{data['user_id'].replace('"','').replace("'","")}',
                                                        {data['score']},
                                                        '{data['rev_content'].replace('"','').replace("'","")}');""")
            
        self.conn.commit()
        cur.close()

    def itemlist_extra(self):
        cur = self.conn.cursor()
        cur.execute("""SELECT item_id,isbn FROM book_table_after""")
        data = cur.fetchall()
        cur.close()
        return data
    
    def get_category(self):
        cur = self.conn.cursor()
        cur.execute("""SELECT category FROM book_table_after""")
        data = cur.fetchall()
        cur.close()
        return data

    def review_extra(self):
        cur = self.conn.cursor()
        cur.execute("""SELECT isbn FROM review_table_after""")
        data = cur.fetchall()
        cur.close()
        return data
    
    def category_book_list(self,category):
        cur = self.conn.cursor()
        cur.execute(f"""SELECT bt.title,bt.isbn FROM book_table_after AS bt WHERE bt.category='{category}'""")
        data = cur.fetchall()
        cur.close()
        return data
    
    def select_book_detail(self,isbn):
        cur = self.conn.cursor()
        cur.execute(f"""SELECT * FROM book_table_after AS bt WHERE bt.isbn='{isbn}'""")
        data = cur.fetchall()
        cur.close()
        return data
    
    def db_conn_exit(self):
        self.conn.close()