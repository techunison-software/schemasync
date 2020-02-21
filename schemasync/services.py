from .models import SourceForm,DatabaseModel
import mysql.connector
import login.settings as projectsettings

class DatabaseServices():
    def validateFormDetails(self,form,status):
        try:
            dbServices=DatabaseServices()
            # status=[]
            sourcedb=DatabaseModel(self,form.cleaned_data['s_hostname'], form.cleaned_data['s_port'], form.cleaned_data['s_database'], 
                            form.cleaned_data['s_username'], form.cleaned_data['s_password'])
            status.append("Checking source database connectivity")
            sourcedbconnection=dbServices.checkDBConnectivity(sourcedb,status)
            destinationdb=DatabaseModel(self,form.cleaned_data['d_hostname'],form.cleaned_data['d_port'],
                            form.cleaned_data['d_database'],form.cleaned_data['d_username'],form.cleaned_data['d_password'])
            status.append("Checking destination database connectivity")
            destinationdbconnection=dbServices.checkDBConnectivity(destinationdb,status)
            returnResult=[status]
            if(isinstance(sourcedbconnection, str) | isinstance(destinationdbconnection, str)):
                raise(Exception)
            else:
                dbServices.saveDBAdapter(sourcedb,status)
                # returnResult.append(sourcedbconnection)
                # returnResult.append(form.cleaned_data['s_database'])
                dbServices.saveDBAdapter(destinationdb,status)
                # returnResult.append(destinationdbconnection)
                # returnResult.append(form.cleaned_data['d_database'])
                return status,sourcedbconnection,destinationdbconnection,form.cleaned_data['s_database'],form.cleaned_data['d_database']
        except Exception as e: 
            print(e)
            status.append("Error while validating database credentials with error message {}".format(e))
    def saveDBAdapter(self,db,status):
        try:
            status.append("Saving database credentials for '{}".format(db.username)+"'@'{}".format(db.hostname)+"' to {}".format(db.database)+" Database")
            mySql_insert_query = "INSERT INTO hostdb (db_hostname, db_port, db_name, db_username, db_password) VALUES (%s,%s,%s,%s,%s)"
            val=(db.hostname,db.port,db.database,db.username,db.password)
            connection = mysql.connector.connect(host='localhost',
                                                            database='test',
                                                            user='root',
                                                            password='Techunison@123')
            cursor = connection.cursor()
            cursor.execute(mySql_insert_query,val)
            connection.commit()
            status.append("Saved database credentials for '{}".format(db.username)+"'@'{}".format(db.hostname)+"' to {}".format(db.database)+" Database")
            cursor.close()
        except Exception as e: 
            status.append("Error while saving database credentials for '{}".format(db.username)+"'@'{}".format(db.hostname)+"' to {}".format(db.database)+" Database with Error Message{}".format(e))
    def checkDBConnectivity(self,db,status):
        try:
            connection = mysql.connector.connect(host=db.hostname,port=db.port,
                                         database=db.database,
                                         user=db.username,
                                         password=db.password)
            if connection.is_connected():
                db_Info = connection.get_server_info()
                status.append("Connected to database : "+db.hostname)
                status.append("Database information : "+db_Info)
            return connection
        except Exception as e: 
            status.append("Error while connecting to MySQL database {}".format(e))
            return ''
    def getDatabaseTableList(self,dbConnection,dbName):
        dbCursor=dbConnection.cursor()
        dbCursor.execute("select table_name from information_schema.tables WHERE table_schema='{}".format(dbName)+"' AND table_type='BASE TABLE'")
        tables=dbCursor.fetchall()
        return tables
    def getDatabaseColumnList(self,dbConnection,dbName,destinationTables):
        dbCursor=dbConnection.cursor()
        tableString=""
        destinationTablesArray=[]
        for table in destinationTables:
            destinationTablesArray.extend(table)
        print("73",destinationTablesArray)
        for table in destinationTablesArray:
            tableString="'"+table+"',"+tableString
        tableString=tableString[:-1]
        print ("tableString",tableString)        
        dbCursor.execute("select table_name,column_name,data_type from information_schema.columns WHERE table_schema='{}".format(dbName)+"' AND TABLE_NAME IN ({}".format(tableString)+")")
        column=dbCursor.fetchall()
        return column
class QueryGenerator:
    def get_new_tables(self,sourceTables,destinationTables):
        sourceTableArray=[]
        destinationTableArray=[]
        for table in sourceTables:
            sourceTableArray.extend(table)
        for table in destinationTables:
            destinationTableArray.extend(table)
        createTableArray = [ createTableArray for createTableArray in sourceTableArray if not createTableArray in destinationTableArray ]
        dropTableArray = [ dropTableArray for dropTableArray in destinationTableArray if not dropTableArray in sourceTableArray ]
        # createTableArray = set(sourceTableArray) - set(destinationTableArray)
        # dropTableArray = set(destinationTableArray) - set(sourceTableArray)
        resultArray = [createTableArray,dropTableArray]
        # print("resultArray",resultArray)
        return resultArray 
    def create_gen(self,sourcedbconnection,destinationdbconnection,destinationdb,createTables,status):
        try:
            sourcedbcursor=sourcedbconnection.cursor()
            destinationdbcursor=destinationdbconnection.cursor()
            createstatements=[]
            createTableArray=[]
            print("createtables",createTables)
            for table in createTables:
                sourcedbcursor.execute("show create table "+table)
                createquery=sourcedbcursor.fetchall()
                for query in createquery:
                    createTableArray.append(query[0])
                    createstatements.append(query[1])
            basetables=[statement for statement in createstatements if 'REFERENCES ' not in statement]
            referencetables=[statement for statement in createstatements if 'REFERENCES ' in statement]
            print("referencetables",referencetables)
            createorder = [0] * len(referencetables)
            for referencetable in referencetables:
                for table in createTableArray:
                    if table!=referencetable:
                        if table in referencetable:
                            print(table,referencetable)
                            position=createTableArray.index(table)
                            print("position",position)
                createorder[position]=referencetable
            createorder.pop(0)
            print("createorder",createorder)
            for statement in createorder:
                status.append("Executing Query : \n"+statement)
                destinationdbcursor.execute(statement)
                destinationdbconnection.commit()
                status.append("Created Table '"+destinationdb+"'.'"+table+"'")
                status.append("Executed Query : \n"+statement)
        except Exception as e:
            print(e)
            status.append(e)
    def drop_gen(self,destinationdbconnection,destinationdb,dropTables,status,index):
        destinationdbcursor=destinationdbconnection.cursor()
        # print("DropTable",dropTables)
        try:
            while len(dropTables)!=0:
                destinationdbcursor.execute("Drop Table "+destinationdb+"."+dropTables[index])
                destinationdbconnection.commit()
                status.append("Dropped Table '"+destinationdb+"'.'"+dropTables[index]+"'")
                status.append("Executed Query : \n"+"Drop Table "+destinationdb+"."+dropTables[index])
                dropTables.remove(dropTables[index])
                ++index
        except Exception as e:
            print(e)
            ++index
            self.drop_gen(destinationdbconnection,destinationdb,dropTables,status,index)
        finally:
            while(len(dropTables)>0):
                self.drop_gen(destinationdbconnection,destinationdb,dropTables,status,0)
            return status
    
    def get_new_columns(self,sourceColumn,destinationColumn):
        sourceColumnArray=[]
        destinationColumnArray=[]
        i=0
        # print("getnewcolumns",sourceColumn)
        for column in sourceColumn:
            print("126 column",column[1])
            print("127 sourcecolumn",sourceColumnArray[i][0])
            sourceColumnArray[i][0]=column[0]
            print("129 sourcecolumn",sourceColumnArray[i][0])
            sourceColumnArray[i][1]=column[1]
            sourceColumnArray[i][2]=column[2]
            i+=1
        print("test")
        print("sourcecolumn",sourceColumnArray[0][0])
        i=0
        for column in destinationColumn:
            destinationColumnArray.extend(column)
        createColumnArray = [ createColumnArray for createColumnArray in sourceColumnArray if not createColumnArray in destinationColumnArray ]
        dropColumnArray = [ dropColumnArray for dropColumnArray in destinationColumnArray if not dropColumnArray in sourceColumnArray ]
        resultColumnArray = [createColumnArray,dropColumnArray]
        print("resultColumnArray",resultColumnArray)
        return resultColumnArray 
        
    def alter_gen(self,destinationdbconnection,destinationdb,table_name,column_name,data_type,status):
        destinationdbcursor=destinationdbconnection.cursor()
        print("alter table "+ table_name +" add column "+ column_name +" "+data_type)
        #for query1 in alterquery:
            #destinationdbcursor.execute(query1[1])
            #destinationdbconnection.commit()
            #status.append("Created Table and column '"+destinationdb+"'.'"+table_name+"'"+"'.'"+column_name)
            #status.append("Executed Query : \n"+query1[1])

class PageServices:
    def init(self,form):
        try:
            status=[]
            dbServices=DatabaseServices()
            queryGen=QueryGenerator()
            pageServices=PageServices()
            status=pageServices.processRequest(dbServices,queryGen,form,status)
        except Exception as e:
            status.append(e)
        finally:
            return status
    def processRequest(self,dbServices,queryGen,form,status):
        try:
            returnResult=dbServices.validateFormDetails(form,status)
            if(len(returnResult)<3):
                # print("returnResult less than 3")
                return returnResult[0]
            status=returnResult[0]
            sourcedbconnection=returnResult[1]
            destinationdbconnection=returnResult[2]
            sourcedb=returnResult[3]
            destinationdb=returnResult[4]
            
            sourceTables=dbServices.getDatabaseTableList(sourcedbconnection,sourcedb)
            # sourceTables=returnResult[0]
            destinationTables=dbServices.getDatabaseTableList(destinationdbconnection,destinationdb)
            # print("sourceTables",sourceTables)
            # print("destinationTables",destinationTables)
            # returnResult=queryGen.get_new_tables(sourceTables,destinationTables)
            createTables=returnResult[0]
            dropTables=returnResult[1]
            # print("118",returnResult)
            # queryGen.create_gen(sourcedbconnection,destinationdbconnection,destinationdb,createTables,status)
            # queryGen.drop_gen(destinationdbconnection,destinationdb,dropTables,status,0)
            # for table in dropTables:
            #     queryGen.drop_gen(sourcedbconnection,destinationdbconnection,table,0)
            sourceColumn=dbServices.getDatabaseColumnList(sourcedbconnection,sourcedb,destinationTables)
            destinationColumn=dbServices.getDatabaseColumnList(destinationdbconnection,destinationdb,destinationTables)
            print("sourcecolumn",sourceColumn)
            print("destinationcolumn",destinationColumn)
            returnResult1=queryGen.get_new_columns(sourceColumn,destinationColumn)
            createColumn=returnResult1[0]
            dropColumns=returnResult1[1]
            print("118",returnResult1)
            status.append("All the Tables are synced")
        except Exception as e:
            # print(e)
            status.append(e)
            return status
        finally:
            return status
        