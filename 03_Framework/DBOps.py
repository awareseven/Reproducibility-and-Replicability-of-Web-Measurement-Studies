import psycopg2

import time
import random

class DBOps: 
    def __init__(self):
   
        str()
    def select_DEP(self, query, onerow=False):
        self.cr.execute(query)
        records = self.cr.fetchall()
        if onerow:
            for row in records: 
                return row
        #self.cr.close()
        #self.connection.close()
        return records

    def exec_DEP(self, query):
        print(query)
        self.__init__()
        self.cr.execute(query)
        self.connection.commit()
        self.cr.close()
        self.connection.close()
        return self.cr.rowcount

    def close(self):
        self.cr.close()
        self.connection.close()
        
 
 
    def select(self, query, onerow=False):        
        conString = "user=#user#  password==#password# host=#ip# port=5432 dbname=#db#" 
        try:
            connection = psycopg2.connect(conString)
            cr = connection.cursor()
        except (Exception, psycopg2.Error) as error:
            print("can't connect DB!", error)  

        records=None
        try:
            with connection:
                with connection.cursor() as cr:
                    cr.execute(query) 
                    records = cr.fetchall()
                    if onerow:
                        for row in records: 
                            return row
                    cr.close()
                    connection.close()
                    #return records
        except: 
            time.sleep(random.randint(0,2))
            try:
                with connection:
                    with connection.cursor() as cr:
                        cr.execute(query) 
                        records = cr.fetchall()
                        if onerow:
                            for row in records: 
                                return row
                        cr.close()
                        connection.close()
                        #return records
            except:
                pass
        return records


    
    def exec(self, query):   
        conString = "user=#user#  password==#password# host=#ip# port=5432 dbname=#db#" 
        try:
            connection = psycopg2.connect(conString)
            cr = connection.cursor()
        except (Exception, psycopg2.Error) as error: 
            print("can't connect DB!", error)  
 
        #print(query)
        try:
            with connection:
                with connection.cursor() as cr:
                    cr.execute(query)   
                    cr.close()
                    #connection.close()
                    return cr.rowcount
        except Exception as e:
            print(e)
            time.sleep(random.randint(0,3))
            try:
                with connection:
                    with connection.cursor() as cr:
                        cr.execute(query)   
                        cr.close()
                        #connection.close()
                        return cr.rowcount
            except Exception as e:
                print(e)
                pass


