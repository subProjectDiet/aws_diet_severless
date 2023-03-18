import json
from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from mysql.connector import Error

from flask_jwt_extended import get_jwt_identity
import boto3
from config import Config
from mysql_connection import get_connection
from datetime import datetime



#음식 검색
class FoodSearchResource(Resource):
    @jwt_required()
    def get(self):
        
        offset = request.args.get('offset')
        limit = request.args.get('limit')
        keyword = request.args.get('keyword')
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            query = """select id, foodName
           from food
           where foodName like '%""" + keyword + """%'
           limit """ + limit + """ offset """ + offset + """;"""
                    
            cursor.execute(query)
            result = cursor.fetchall()
            return {"result": result, "count" : len(result)}, 200
        
        except Exception as e:
            print(e)
            return ("errer" + str(e)), 500
        
        finally:
            conn.close()
            cursor.close()



#검색한 음식 한개띄워주기    
class FoodResource(Resource):
    @jwt_required()
    def get(self,food_id):

        try :
            connection = get_connection()

            query = '''select id,foodName,gram,kcal,carbs,protein,fat
                        from food
                        where id = %s;
                    '''

            record = (food_id, )
            cursor = connection.cursor(dictionary= True)
            cursor.execute(query,record)

            result_list = cursor.fetchall()

          

            # i = 0
            # for row in result_list :
            #     result_list[i]['createdAt'] = row['createdAt'].isoformat()
            #     result_list[i]['updatedAt'] = row['updatedAt'].isoformat()
            #     i = i + 1

            cursor.close()
            connection.close()
    
        except Error as e :
            print(e)            
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 500
                
        # print(result_list)

        return {"result" : "success" ,
                "items" : result_list , 
                "count" : len(result_list)}, 200



#먹은음식 음식테이블 데이터 가저와서 저장
class FoodRecordResource(Resource):
    @jwt_required()
    def post(self) :
    #   {
    #     "foodName" :"삼겹살",
    #     "gram" :50,
    #     "kcal":30,
    #     "carbs": 50,
    #     "protein": 20 ,
    #     "fat": 10,
    #     "mealtime" : 2
    #     }

        data = request.get_json()
        user_id = get_jwt_identity()
        recordType = request.args.get('recordType')

        try :
            connection = get_connection()
            query = '''INSERT INTO foodRecord (userId, foodName, gram, kcal, carbs, protein, fat, mealtime, date,recordType)
         VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s ,%s)
         ;'''
            record = (user_id, data['foodName'], data['gram'], data['kcal'], data['carbs'], data['protein'], data['fat'], data['mealtime'],data['date'],recordType)
            
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)}, 500
                
        return {'result' : 'success'} , 200

#먹은음식 직접작성후 저장(탄단지 자동계산)
class FoodRecordUserResource(Resource):
    @jwt_required()
    def post(self) :
    #   {
    #     "foodName" :"삼겹살",
    #     "gram" :50,
    #     "kcal":30,
    #     "carbs": 50,
    #     "protein": 20 ,
    #     "fat": 10,
    #     "mealtime" : 2
    #     }

        data = request.get_json()
        user_id = get_jwt_identity()
        recordType = request.args.get('recordType')

        try :
            kcal = data['kcal']
            carbs = round(kcal * 0.25 / 4)
            protein = round(kcal * 0.25 / 4)
            fat = round(kcal * 0.5 / 9)
            
            
            connection = get_connection()
            query = '''INSERT INTO foodRecord (userId, foodName, gram, kcal, carbs, protein, fat, mealtime, date,recordType)
         VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s ,%s)
         ;'''
            record = (user_id, data['foodName'], data['gram'], data['kcal'], carbs,protein, fat, data['mealtime'], data['date'], recordType)
            
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)}, 500
                
        return {'result' : 'success'} , 200


#작성한 음식수정(탄단지 자동계산)
class FoodRecordEditResource(Resource):
    @jwt_required()
    def put(self, record_id):
# {
#     "foodName" :"김치나베",
#     "gram" :50,
#     "kcal":400,
#     "mealtime" : 2
# }

        data = request.get_json()
        user_id = get_jwt_identity()

        try:
            connection = get_connection()
            kcal = data['kcal']
            carbs = round(kcal * 0.25 / 4)
            protein = round(kcal * 0.25 / 4)
            fat = round(kcal * 0.5 / 9)

            query = '''UPDATE foodRecord 
                    SET 
                    foodName = %s, 
                        gram = %s, 
                        kcal = %s, 
                        carbs = %s, 
                        protein = %s, 
                        fat = %s, 
                        mealtime = %s
                    WHERE id = %s AND userId = %s;'''

            record = (data['foodName'], data['gram'], kcal, carbs, protein, fat, data['mealtime'], record_id, user_id)

            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()

            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return {'error': str(e)}, 500

        return {'result': 'success'}, 200

    @jwt_required()
    def delete(self, record_id) :

        user_id = get_jwt_identity()

        try :
            connection = get_connection()
            query = '''delete from foodRecord
                    where id = %s and userId = %s;'''
            record = (record_id, user_id)
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()
            cursor.close()
            connection.close()
        
        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)} , 500


        return {'result' : 'success'}, 200    


#아침먹은 모든음식 정보  
class FoodRecordBreakfastResource(Resource):
    @jwt_required()
    def get(self):
        date_str = request.args.get('date')
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        user_id = get_jwt_identity()

        try:
            connection = get_connection()

            query = f'''SELECT *
                    FROM foodRecord
                    WHERE mealtime = 0 AND date = '{date}' AND userId = {user_id};'''

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)

            result_list = cursor.fetchall()

            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return {"error": str(e)}, 500

        return {"result": "success",
                "items": json.loads(json.dumps(result_list, default=str)),
                "count": len(result_list)}, 200
        

#점심먹은 모든음식 정보    
class FoodRecordLunchResource(Resource):
    @jwt_required()
    def get(self):
        date_str = request.args.get('date')
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        user_id = get_jwt_identity()

        try:
            connection = get_connection()

            query = f'''SELECT *
                    FROM foodRecord
                    WHERE mealtime = 1 AND date = '{date}' AND userId = {user_id};'''

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)

            result_list = cursor.fetchall()

            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return {"error": str(e)}, 500

        return {"result": "success",
                "items": json.loads(json.dumps(result_list, default=str)),
                "count": len(result_list)}, 200
    
#저녁먹은 모든음식 정보
class FoodRecordDinnerResource(Resource):
    @jwt_required()
    def get(self):
        date_str = request.args.get('date')
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        user_id = get_jwt_identity()

        try:
            connection = get_connection()

            query = f'''SELECT *
                    FROM foodRecord
                    WHERE mealtime = 2 AND date = '{date}' AND userId = {user_id};'''

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)

            result_list = cursor.fetchall()

            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return {"error": str(e)}, 500

        return {"result": "success",
                "items": json.loads(json.dumps(result_list, default=str)),
                "count": len(result_list)}, 200     
   
 #



#특정날짜 아침 kcal
class FoodRecordTotalBreakfast(Resource):
    @jwt_required()
    def get(self):
        date_str = request.args.get('date')
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        user_id = get_jwt_identity()

        try:
            connection = get_connection()

            query = f'''SELECT sum(kcal)
                    FROM foodRecord
                    WHERE mealtime = 0
                    AND date = '{date}' AND userId = {user_id}
                    group by mealtime ;'''

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)

            result_list = cursor.fetchall()

            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return {"error": str(e)}, 500

        return {"result": "success",
                "items": json.loads(json.dumps(result_list, default=str)),
                "count": len(result_list)}, 200
    
#특정날짜 점심 kcal
class FoodRecordTotalLunchResource(Resource):
    @jwt_required()
    def get(self):
        date_str = request.args.get('date')
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        user_id = get_jwt_identity()

        try:
            connection = get_connection()

            query = f'''SELECT sum(kcal)
                    FROM foodRecord
                    WHERE mealtime = 1
                    AND date = '{date}' AND userId = {user_id}
                    group by mealtime ;'''

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)

            result_list = cursor.fetchall()

            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return {"error": str(e)}, 500

        return {"result": "success",
                "items": json.loads(json.dumps(result_list, default=str)),
                "count": len(result_list)}, 200
#특정날짜 저녁 kcal
class FoodRecordTotalDinnerResource(Resource):
    @jwt_required()
    def get(self):
        date_str = request.args.get('date')
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        user_id = get_jwt_identity()

        try:
            connection = get_connection()

            query = f'''SELECT sum(kcal)
                    FROM foodRecord
                    WHERE mealtime = 2
                    AND date = '{date}' AND userId = {user_id}
                    group by mealtime ;'''

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)

            result_list = cursor.fetchall()

            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return {"error": str(e)}, 500

        return {"result": "success",
                "items": json.loads(json.dumps(result_list, default=str)),
                "count": len(result_list)}, 200

#특정날짜 탄수화물 총합
class FoodRecordTotalCarbsResource(Resource):
    @jwt_required()
    def get(self):
        date_str = request.args.get('date')
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        user_id = get_jwt_identity()

        try:
            connection = get_connection()

            query = f'''SELECT sum(carbs)
                    FROM foodRecord
                    WHERE date = '{date}' 
                    AND userId = {user_id}
                    group by date ;'''

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)

            result_list = cursor.fetchall()

            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return {"error": str(e)}, 500

        return {"result": "success",
                "items": json.loads(json.dumps(result_list, default=str)),
                "count": len(result_list)}, 200
    
#특정날짜 단백질 총합
class FoodRecordTotalProteinResource(Resource):
    @jwt_required()
    def get(self):
        date_str = request.args.get('date')
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        user_id = get_jwt_identity()

        try:
            connection = get_connection()

            query = f'''SELECT sum(protein)
                    FROM foodRecord
                    WHERE date = '{date}' 
                    AND userId = {user_id}
                    group by date ;'''

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)

            result_list = cursor.fetchall()

            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return {"error": str(e)}, 500

        return {"result": "success",
                "items": json.loads(json.dumps(result_list, default=str)),
                "count": len(result_list)}, 200
#특정날짜 지방 총합
class FoodRecordTotalFatResource(Resource):
    @jwt_required()
    def get(self):
        date_str = request.args.get('date')
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        user_id = get_jwt_identity()

        try:
            connection = get_connection()

            query = f'''SELECT sum(fat)
                    FROM foodRecord
                    WHERE date = '{date}' 
                    AND userId = {user_id}
                    group by date ;'''

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)

            result_list = cursor.fetchall()

            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return {"error": str(e)}, 500

        return {"result": "success",
                "items": json.loads(json.dumps(result_list, default=str)),
                "count": len(result_list)}, 200

#특정날짜 먹은 kcal총합
class FoodRecordTotalDayResource(Resource):
    @jwt_required()
    def get(self):
        date_str = request.args.get('date')
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        user_id = get_jwt_identity()

        try:
            connection = get_connection()

            query = f'''SELECT sum(kcal)
                    FROM foodRecord
                    WHERE date = '{date}' 
                    AND userId = {user_id}
                    group by date ;'''

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)

            result_list = cursor.fetchall()

            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return {"error": str(e)}, 500

        return {"result": "success",
                "items": json.loads(json.dumps(result_list, default=str)),
                "count": len(result_list)}, 200