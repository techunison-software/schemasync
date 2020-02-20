class SyncView(generic.View):
    template_name = 'sync.html'

    def get(self, request, *args, **kwargs):
        try:
            mySql_insert_query = "INSERT INTO hostdb (hostname, port) VALUES (%s,%s)"
            val=("localhost","3306")
            connection = mysql.connector.connect(host='localhost',
                                                    database='test',
                                                    user='root',
                                                    password='Techunison@123')
            cursor = connection.cursor()
            cursor.execute(mySql_insert_query,val)
            connection.commit()
            print(cursor.rowcount, "Record inserted successfully into Laptop table")
            cursor.close()
        except mysql.connector.Error as error:
            print("Failed to insert record into Laptop table {}".format(error))

        finally:
            print("Hello Finally")
            if (connection.is_connected()):
                connection.close()
                print("MySQL connection is closed")