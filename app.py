import json
from flask import Flask, jsonify, request
import requests
import sqlite3

app = Flask(__name__)

def verificacion(key):
    sqliteConnection = sqlite3.connect('tarea.db')
    cursor = sqliteConnection.cursor()
    sqlite_select_Query = "select company_api_key from Company;"
    cursor.execute(sqlite_select_Query)
    record = cursor.fetchall()
    for elemento in record:
            if str(elemento[0])==key:
                return True
                cursor.close()
    cursor.close()
    return False


#----------------------------------GET MULTIPLE----------------------------------------------------------------------------
@app.route("/api/v1/<tabla>&company_api_key=<key>",methods=["GET"])
def apiget(tabla,key):
    try:
        bandera=verificacion(key)
        if tabla=='Admin' or tabla=="Company":
            return jsonify({"mensaje":"Error, tabla incorrecta"}),400
        else:        
            if bandera==True:
               sqliteConnection = sqlite3.connect('tarea.db')
               cursor = sqliteConnection.cursor()
               print("conexión exitosa")
               sqlite_select_Query = "select * from "+tabla+";"
               cursor.execute(sqlite_select_Query)
               record = cursor.fetchall()
               cursor.close()
               return jsonify({"resultados":record})
            else:
                return jsonify({"mensaje":"Error, api key incorrecto"})

    except:
            return('error')
            
@app.route("/api/v1/SensorData&sensor_api_key=<api_key>&from=<timefrom>&to=<timeto>&sensor_id=<ids>",defaults={'timefrom': None,'timeto': None},methods=["GET", "POST"])
def apigetsensorData(api_key,timefrom,timeto,ids):
    try:
        bandera=verificacion(api_key)
        if bandera==True:
            sqliteConnection = sqlite3.connect('tarea.db')
            print("conexión exitosa")
            arreglo=[]
            for elemento in ids:
                if elemento!='[' and elemento!=']' and elemento!=',':
                    print(elemento)
                    sqlite_select_Query = "select * from 'Sensor Data' where sensor_id="+str(elemento.strip())+";"
                    cursor = sqliteConnection.cursor()
                    cursor.execute(sqlite_select_Query)
                    print('ioasfijoasfojik')
                    resultado=cursor.fetchall()
                    arreglo.append({str(elemento):resultado})
            print(arreglo)
            cursor.close()
            return jsonify({"resultados":arreglo}),200
        else:
            return jsonify({"mensaje":"Error, api key incorrecto"}),400
    
    except:
            return('error')

#----------------------------------GET--------------------------------------------------------------------------------------------

@app.route("/api/v1/<tabla>&company_api_key=<key>&id=<id>",methods=["GET"])
def apigetid(tabla,key,id):
    try:
        bandera=verificacion(key)
        if bandera==True:
           sqliteConnection = sqlite3.connect('tarea.db')
           cursor = sqliteConnection.cursor()
           print("conexión exitosa")
           if tabla=='Location':
                sqlite_select_Query = "select * from "+tabla+" where id="+id+";"
                cursor.execute(sqlite_select_Query)
                record = cursor.fetchall()
                cursor.close()
                return jsonify({"resultados":record})
           elif tabla=='Sensor':
                sqlite_select_Query = "select * from "+tabla+" where sensor_id="+id+";"
                cursor.execute(sqlite_select_Query)
                record = cursor.fetchall()
                cursor.close()
                return jsonify({"resultados":record})
        else:
            return jsonify({"mensaje":"Error, api key incorrecto"})

    except:
            return('error')

#-------------------------------------- POST COMPANY ---------------------------------------------------------------------------------
@app.route("/api/v1/admin/createCompany", methods=['POST'])
def createCompany():
    if request.method == 'POST':
        data= request.get_json()
        bandera=verificacion(data['company_api_key'])
        if bandera==True:      
            validate= validate_admin(data['Username'], data['Password'])
            if validate == True:
                sqliteConnection = sqlite3.connect('tarea.db')
                cursor = sqliteConnection.cursor()
                query = 'select * from Company'
                cursor.execute(query)
                record = cursor.fetchall()
                newcompany = False
                for company in record:
                    print(company[1])
                    if company[1] ==  data['company_name']:
                        newcompany = False
                        return jsonify({"mensaje":"Error! Compañia existente, compruebe con otro"})
                    else: 
                        newcompany = True
                if newcompany == True: 
                    employee = (data['company_name'] ,  data['company_api_key'])
                    sql = """insert into Company(company_name, company_api_key) values(?,?);"""
                    cursor.execute(sql, employee)
                    sqliteConnection.commit()
                    cursor.close()
                    return jsonify({"mensaje":"Compañia creada éxitosamente!"})
            else:
                return jsonify({"mensaje": 'Usuario y/o contraseña incorrecto'})
        else:
            return jsonify({"mensaje":"Error, api key incorrecto"})      


#----------------------------------------------- POST LOCATION -----------------------------------------------------------------------
@app.route("/api/v1/admin/createLocation", methods=['POST'])
def createLocation():
    if request.method == 'POST':
        data= request.get_json()
        bandera=verificacion(data['company_api_key'])
        if bandera==True:            
            validate= validate_admin(data['Username'], data['Password'])
            if validate == True:
                sqliteConnection = sqlite3.connect('tarea.db')
                cursor = sqliteConnection.cursor()
                employee = (data['company_id'] ,  data['location_name'], data['location_country'], data['location_city'], data['location_meta'])
                sql = """insert into Location(company_id, location_name, location_country, location_city, location_meta) values(?, ?, ?, ?, ?);"""
                cursor.execute(sql, employee)
                sqliteConnection.commit()
                cursor.close()
                return jsonify({"mensaje":"Locación creada éxitosamente!"})
            else:
                return jsonify({"mensaje": 'Usuario y/o contraseña incorrecto'})
        else:
            return jsonify({"mensaje":"Error, api key incorrecto"}) 

#-------------------------------------------- POST SENSOR---------------------------------------------------------------------------
@app.route("/api/v1/admin/create_sensor", methods=['POST'])
def createSensor():
    if request.method == 'POST':
        data= request.get_json()  
        bandera=verificacion(data['company_api_key'])
        if bandera==True:                
            validate= validate_admin(data['Username'], data['Password'])
            if validate == True:
                sqliteConnection = sqlite3.connect('tarea.db')
                cursor = sqliteConnection.cursor()
                employee = (data['location_id'] ,  data['sensor_id'], data['sensor_name'], data['sensor_category'], data['sensor_meta'], data['sensor_api_key'])
                sql = """insert into Sensor(location_id, sensor_id, sensor_name, sensor_category, sensor_meta, sensor_api_key) values(?, ?, ?, ?, ?, ?);"""
                cursor.execute(sql, employee)
                sqliteConnection.commit()
                cursor.close()
                return jsonify({"mensaje":"Sensor creado éxitosamente!"})
            else:
                return jsonify({"mensaje": 'Usuario y/o contraseña incorrecto'})
        else:
            return jsonify({"mensaje":"Error, api key incorrecto"}) 

@app.route("/api/v1/sensor_data", methods=['POST'])
def sensor_data():
    if request.method == 'POST':
        data= request.get_json()
        sensor_key = authorization_sensor(data['api_key'])
        if sensor_key == True:    
            sqliteConnection = sqlite3.connect('tarea.db')
            cursor = sqliteConnection.cursor()
            employee = (data['json_data'][0]['sensor_id'], data['json_data'][1]['dato1'] ,  data['json_data'][2]['dato2'])
            sql = """insert into 'Sensor Data'(sensor_id, dato1, dato2) values(?, ?, ?);"""
            cursor.execute(sql, employee)
            sqliteConnection.commit()
            cursor.close()
            return jsonify({"mensaje":"Datos de sensor data creados exitosamente!"}),201
        else: 
            return jsonify({"mensaje":"api key incorrecto"})

#--------------------------------------------DELETE COMPANY---------------------------------------------------------------------------

@app.route("/api/v1/admin/deleteCompany", methods=['DELETE'])
def eliminateCompany():
    if request.method == 'DELETE':
        data= request.get_json()      
        validate= validate_admin(data['Username'], data['Password'])
        if validate == True:
            sqliteConnection = sqlite3.connect('tarea.db')
            cursor = sqliteConnection.cursor()
            query = 'select * from Company'
            cursor.execute(query)
            record = cursor.fetchall()
            deleteCompany = False
            for company in record:
                print(company[2])
                if company[2] ==  data['company_api_key']:
                    deleteCompany = True
                    employee = (data['company_api_key'])
                    sql = """DELETE FROM Company WHERE  company_api_key=?"""
                    cursor.execute(sql, (employee,))
                    sqliteConnection.commit()
                    cursor.close()
                    return jsonify({"mensaje":"Operación exitosa, compañia eliminada"})
                    
            if deleteCompany == False: 
                return jsonify({"mensaje":"Error! Compañia no encontrada"})
        else:
            return jsonify({"mensaje": 'Usuario y/o contraseña incorrecto'})

#--------------------------------------------DELETE LOCATION---------------------------------------------------------------------------
@app.route("/api/v1/deleteLocation", methods=['DELETE'])
def deleteLocation():
    if request.method == 'DELETE':
        data= request.get_json()      
        bandera = verificacion(data['company_api_key'])
        if bandera == True:
            sqliteConnection = sqlite3.connect('tarea.db')
            cursor = sqliteConnection.cursor()
            query = ''' select * from Location '''
            cursor.execute(query)
            record = cursor.fetchall()
            eliminateLocation = False
            for i in record:
                if i[2] == data['location_name'] :
                    eliminateLocation = True
            if eliminateLocation == True:
                employee = (data['location_name'])
                sql = """DELETE FROM Location WHERE  location_name=?"""
                cursor.execute(sql, (employee,))
                sqliteConnection.commit()
                cursor.close()
                return jsonify({"mensaje":"Operación exitosa, location eliminada"})
            else:
                return jsonify({"mensaje":"Error! Location no encontrado"})
        else:
            return jsonify({"mensaje":"Error, api key incorrecto"})


#--------------------------------------------DELETE SENSOR---------------------------------------------------------------------------
@app.route("/api/v1/deleteSensor", methods=['DELETE'])
def deleteSensor():
    if request.method == 'DELETE':
        data= request.get_json()      
        bandera = verificacion(data['company_api_key'])
        if bandera == True:
            sqliteConnection = sqlite3.connect('tarea.db')
            cursor = sqliteConnection.cursor()
            query = ''' select * from Sensor '''
            cursor.execute(query)
            record = cursor.fetchall()
            eliminateSensor = False
            for i in record:
                if i[1] == data['sensor_id'] :
                    eliminateSensor = True
            if  eliminateSensor == True:
                employee = (data['sensor_id'])
                sql = """DELETE FROM Sensor WHERE  sensor_id=?"""
                cursor.execute(sql, (employee,))
                sqliteConnection.commit()
                cursor.close()
                return jsonify({"mensaje":"Operación exitosa, Sensor eliminado"})
            else:
                return jsonify({"mensaje":"Error! Sensor no encontrado"})
        
        else:
            return jsonify({"mensaje":"Error, api key incorrecto"})


#--------------------------------------------DELETE SENSOR DATA---------------------------------------------------------------------------
@app.route("/api/v1/delete/sensor_data", methods=['DELETE'])
def deleteSensorD():
    if request.method == 'DELETE':
        data= request.get_json()      
        bandera = authorization_sensor(data['sensor_api_key'])
        if bandera == True:
            sqliteConnection = sqlite3.connect('tarea.db')
            cursor = sqliteConnection.cursor()
            query = ''' select * from "Sensor Data" '''
            cursor.execute(query)
            record = cursor.fetchall()
            eliminateSensor = False
            for i in record:
                if i[1] == data['sensor_id'] :
                    eliminateSensor = True
            if  eliminateSensor == True:
                employee = (data['sensor_id'])
                sql = """DELETE FROM "Sensor Data" WHERE  sensor_id=?"""
                cursor.execute(sql, (employee,))
                sqliteConnection.commit()
                cursor.close()
                return jsonify({"mensaje":"Operación exitosa, Sensor Data eliminado"})
            else:
                return jsonify({"mensaje":"Error! Sensor Data no encontrado"})
        
        else: 
            return jsonify({"mensaje":"Error! sensor_api_key es incorrecto"})


#--------------------------------------------PUT---------------------------------------------------------------------------
@app.route("/api/v1/<tabla>&company_api_key=<key>&id=<id>", methods=['PUT'])
def updateCompany(tabla,key,id):
        data= request.get_json()
        bandera=verificacion(key)
        if bandera==True:
            if tabla=='Admin' or tabla=="Company":
                return jsonify({"mensaje":"Error, tabla incorrecta"}),400
            sqliteConnection = sqlite3.connect('tarea.db')
            cursor = sqliteConnection.cursor()
            if tabla=='Location':
                print("iujasjfajioasjiasfojisjaoiioj")
                company=data['company_id']
                name=data['location_name']
                country=data['location_country']
                city=data['location_city']
                meta=data['location_meta']
                employee = (company,name,country,city,meta,id)
                sql = """UPDATE Location SET company_id= ?, location_name = ?, location_country = ?, location_city = ?, location_meta = ? WHERE  id=?"""
                cursor.execute(sql,employee)
                sqliteConnection.commit()
                cursor.close()
                return jsonify({"mensaje":"Operación exitosa, location actualizada"})
            
            elif tabla=='Sensor':
                location=data["location_id"]
                name=data['sensor_name']
                category=data['sensor_category']
                meta=data['sensor_meta']
                apikey=data['sensor_api_key']
                employee = (location,name,category,meta, apikey,id)
                sql = """UPDATE Sensor SET location_id= ?,sensor_name = ?, sensor_category = ?, sensor_meta = ?, sensor_api_key = ? WHERE  sensor_id=?"""
                cursor.execute(sql,employee)
                sqliteConnection.commit()
                cursor.close()
                return jsonify({"mensaje":"Operación exitosa, Sensor actualizada"})
            elif tabla=='Sensor Data':
                dato1=data['dato1']
                dato2=data['dato2']
                print("fjiafsuijisaufujasusaiuifsajfsuisaujfsauifsaju")
                employee = (dato1,dato2,id)
                sql = """UPDATE Sensor SET dato1 = ?, dato2 = ? WHERE sensor_id= ?"""
                cursor.execute(sql,employee)
                sqliteConnection.commit()
                cursor.close()
                return jsonify({"mensaje":"Operación exitosa, Sensor Data actualizada"})    
        else:
            return jsonify({"mensaje":"Error, api key incorrecto"})

#--------------------------------------------METHODS---------------------------------------------------------------------------

def validate_admin(user, password):
    sqliteConnection = sqlite3.connect('tarea.db')
    cursor = sqliteConnection.cursor()
    query = "select * from Admin;"
    cursor.execute(query)
    record = cursor.fetchall()
    for i in record:
        if i[0] == user and i[1] == password:
            cursor.close()
            return True
      
    cursor.close()
    return False
 
def authorization_sensor(sensor_api_key):
    sqliteConnection = sqlite3.connect('tarea.db')
    cursor = sqliteConnection.cursor()
    query = "select * from Sensor;"
    cursor.execute(query)
    record = cursor.fetchall()
    for i in record:
        print(i[5])
        if i[5] == sensor_api_key:
            cursor.close()
            return True
        
    cursor.close()
    return False


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)