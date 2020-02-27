from .models import SourceForm,DatabaseModel
import mysql.connector
import login.settings as projectsettings

class DatabaseServices():
    def validateFormDetails(self,form,status):
        try:
            dbServices=DatabaseServices()
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
                dbServices.saveDBAdapter(destinationdb,status)
                return status,sourcedbconnection,destinationdbconnection,form.cleaned_data['s_database'],form.cleaned_data['d_database']
        except Exception as e: 
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
        for table in destinationTablesArray:
            tableString="'"+table+"',"+tableString
        tableString=tableString[:-1]       
        dbCursor.execute("select table_name,column_name,COLUMN_TYPE,IS_NULLABLE from information_schema.columns WHERE table_schema='{}".format(dbName)+"' AND TABLE_NAME IN ({}".format(tableString)+")")
        column=dbCursor.fetchall()
        names=[]
        for columnname in column:
            names.append(columnname[1])
        columnArray=[column,names]
        return columnArray
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
        resultArray = [createTableArray,dropTableArray]
        return resultArray 
    def create_gen(self,sourcedbconnection,destinationdbconnection,destinationdb,createTables,status):
        try:
            sourcedbcursor=sourcedbconnection.cursor()
            destinationdbcursor=destinationdbconnection.cursor()
            createstatements=[]
            createTableArray=[]
            for table in createTables:
                sourcedbcursor.execute("show create table "+table)
                createquery=sourcedbcursor.fetchall()
                for query in createquery:
                    createTableArray.append(query[0])
                    createstatements.append(query[1])
            basetables=[statement for statement in createstatements if 'REFERENCES ' not in statement]
            referencetables=[statement for statement in createstatements if 'REFERENCES ' in statement]
            createorder = [0] * len(referencetables)
            for referencetable in referencetables:
                for table in createTableArray:
                    if table in referencetable:
                        position=createTableArray.index(table)
                createorder[position]=referencetable
            if len(createorder)>1:
                createorder.pop(0)
            basetables.extend(createorder)
            for statement in basetables:
                status.append("Executing Query : \n"+statement)
                destinationdbcursor.execute(statement)
                destinationdbconnection.commit()
                status.append("Created Table '"+destinationdb+"'.'"+table+"'")
                status.append("Executed Query : \n"+statement)
        except Exception as e:
            status.append(e)
    def drop_gen(self,destinationdbconnection,destinationdb,dropTables,status,index):
        destinationdbcursor=destinationdbconnection.cursor()
        try:
            while len(dropTables)!=0:
                destinationdbcursor.execute("Drop Table "+destinationdb+"."+dropTables[index])
                destinationdbconnection.commit()
                status.append("Dropped Table '"+destinationdb+"'.'"+dropTables[index]+"'")
                status.append("Executed Query : \n"+"Drop Table "+destinationdb+"."+dropTables[index])
                dropTables.remove(dropTables[index])
                ++index
        except Exception as e:
            ++index
            self.drop_gen(destinationdbconnection,destinationdb,dropTables,status,index)
        finally:
            while(len(dropTables)>0):
                self.drop_gen(destinationdbconnection,destinationdb,dropTables,status,0)
            return status
    
    def get_new_columns(self,sourceColumn,destinationColumn,destinationColumnNames,status):
        try:
            sourceColumnArray=[]
            destinationColumnArray=[]
            createColumnIndex=[]
            createColumnArray = [ createColumnArray for createColumnArray in sourceColumn if createColumnArray not in destinationColumn  ]
            dropColumnArray = [ dropColumnArray for dropColumnArray in destinationColumn if dropColumnArray not in sourceColumn ]
            dropColumnArray = [ dropColumnArray for dropColumnArray in dropColumnArray if dropColumnArray[1] not in destinationColumnNames ]
            for column in createColumnArray:
                createColumnIndex.append(sourceColumn.index(column))
            resultColumnArray = [createColumnArray,dropColumnArray,createColumnIndex]
            return resultColumnArray
        except Exception as e:
            status.append("get_new_columns : "+e)
        
    def alter_gen(self,destinationdbconnection,destinationdb,createColumns,dropColumns,sourceColumn,destinationColumnNames,createColumnIndex,status):
        try:
            destinationdbcursor=destinationdbconnection.cursor()
            i=0
            for createColumn in createColumns:
                if str(createColumn[3])=='YES':
                    statement="alter table {}".format(createColumn[0]) +" add column {}".format(createColumn[1]) +" {}".format(createColumn[2])+" NULL AFTER {}".format(sourceColumn[createColumnIndex[i]-1][1])+""
                else:
                    statement="alter table {}".format(createColumn[0]) +" add column {}".format(createColumn[1]) +" {}".format(createColumn[2])+" NOT NULL AFTER {}".format(sourceColumn[createColumnIndex[i]-1][1])+""
                if(createColumn[1] in destinationColumnNames):
                    statement="alter table {}".format(createColumn[0]) +" change column {}".format(createColumn[1])+" {}".format(createColumn[1]) +" {}".format(createColumn[2])+" NULL AFTER {}".format(sourceColumn[createColumnIndex[i]-1][1])+""
                destinationdbcursor.execute(statement)
                destinationdbconnection.commit()
                status.append("Added column '{}".format(createColumn[1])+"' in '"+destinationdb+"'.'{}".format(createColumn[0])+"'")
                status.append("Executed Query : \n"+statement)
                i=i+1
        except Exception as e:
            status.append("alter_gen"+e)
        try:
            for dropColumn in dropColumns:
                statement="alter table {}".format(dropColumn[0]) +" drop column {}".format(dropColumn[1])
                destinationdbcursor.execute(statement)
                destinationdbconnection.commit()
                status.append("Dropped column '{}".format(dropColumn[1])+"' in '"+destinationdb+"'.'{}".format(dropColumn[0])+"'")
                status.append("Executed Query : \n"+statement)
        except Exception as e:
            status.append("alter_gen : "+e)
        finally:
            return status

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
            error=False
            returnResult=dbServices.validateFormDetails(form,status)
            if(len(returnResult)<3):
                return returnResult[0]
            status=returnResult[0]
            sourcedbconnection=returnResult[1]
            destinationdbconnection=returnResult[2]
            sourcedb=returnResult[3]
            destinationdb=returnResult[4]
            
            sourceTables=dbServices.getDatabaseTableList(sourcedbconnection,sourcedb)
            destinationTables=dbServices.getDatabaseTableList(destinationdbconnection,destinationdb)
            returnResult=queryGen.get_new_tables(sourceTables,destinationTables)
            createTables=returnResult[0]
            dropTables=returnResult[1]
            queryGen.create_gen(sourcedbconnection,destinationdbconnection,destinationdb,createTables,status)
            
            sourceTables=dbServices.getDatabaseTableList(sourcedbconnection,sourcedb)
            destinationTables=dbServices.getDatabaseTableList(destinationdbconnection,destinationdb)
            sourceColumn=dbServices.getDatabaseColumnList(sourcedbconnection,sourcedb,destinationTables)
            sourceColumnNames=sourceColumn[1]
            sourceColumn=sourceColumn[0]
            destinationColumn=dbServices.getDatabaseColumnList(destinationdbconnection,destinationdb,destinationTables)
            destinationColumnNames=destinationColumn[1]
            destinationColumn=destinationColumn[0]
            returnResult1=queryGen.get_new_columns(sourceColumn,destinationColumn,destinationColumnNames,status)
            createColumns=returnResult1[0]
            dropColumns=returnResult1[1]
            createColumnIndex=returnResult1[2]
            queryGen.alter_gen(destinationdbconnection,destinationdb,createColumns,dropColumns,sourceColumn,destinationColumnNames,createColumnIndex,status)
        except Exception as e:
            status.append(e)
            error=True
        finally:
            if error==True:
                status.append("Error while Syncing Tables please check the log for more details")
            else:
                status.append("All the Tables are synced")
            return status
        