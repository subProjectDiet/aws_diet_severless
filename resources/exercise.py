from datetime import datetime
from flask import request
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
from flask_restful import Resource
from mysql.connector import Error

from mysql_connection import get_connection
from email_validator import validate_email, EmailNotValidError
from flask_jwt_extended import get_jwt_identity
from utils import check_password, hash_password


class ExerciseKcalResource(Resource):
    # (운동 테이블에 있는 데이터로)운동 칼로리 입력 API
    @jwt_required()
    def post(self) :
    
        recordType = request.args.get('recordType')
        
        #    {
        #     "exerciseName": "사이클링 느리게",
        #     "exerciseTime": 15,
        #     "date": "2023-03-05"
        #     }

        data = request.get_json()
        user_id = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''insert into exerciseRecord(userId, exerciseName, exerciseTime, totalKcalBurn, date, recordType)
                        values
                        (%s, %s, %s,
                        round((select kcalBurn 
                        from exercise 
                        where exercise = %s) *
                        (select nowWeight 
                        from diary 
                        where userId = %s and date = %s) * %s, 2)
                        , %s, %s);'''

            record = ( user_id, data['exerciseName'], data['exerciseTime'], 
                        data['exerciseName'], user_id, data['date'], data['exerciseTime'], data['date'] , recordType)
            
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



    # 특정날짜에 작성한 운동 칼로리 가져오는 api
    @jwt_required()
    def get(self) :
        date = request.args.get('date')

        user_id = get_jwt_identity()

        try :
            connection = get_connection()
            query = ''' select d.userId, d.date, d.nowWeight,  er.exerciseId , e.exercise 
                        ,er.exerciseTime, round(nowWeight*kcalBurn, 2) as totalKcalBurn
                        from diary d
                        join exerciseRecord er
                        on d.userId = er.userId
                        join exercise e
                        on e.id = er.exerciseId
                        where d.userId = %s and d.date = %s;'''

            record = (user_id, date)

            cursor = connection.cursor(dictionary=True)

            cursor.execute(query, record)

            result_list = cursor.fetchall()

            i = 0
            for row in result_list :
                result_list[i]['date'] = row['date'].isoformat()
                i = i + 1

            cursor.close()
            connection.close()

        except Error as e :
            print(e)            
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 500
                
        return {"result" : "success" ,
                "items" : result_list , 
                "count" : len(result_list)}, 200

class ExerciseKcalModifyDelete(Resource):
    # (운동 테이블에서 가져온) 운동 칼로리 (운동한 시간) 수정하는 API
    @jwt_required()
    def put(self, exerciseRecord_id):

        recordType = request.args.get('recordType')
        # {
        #     "exerciseName": "사이클링, 산악 자전거, BMX",
        #     "exerciseTime": 30,
        #     "date": "2023-03-05"
        # }

        data = request.get_json()
        user_id = get_jwt_identity()

        try :
            connection = get_connection()
            query = '''update exerciseRecord
                    set exerciseTime = %s,
                    totalKcalBurn = %s * 
                    (select kcalBurn from exercise
                    where exercise = %s)*
                    (select nowWeight from diary
                    where date = %s and userId = %s)
                    where userId = %s and id = %s and recordType = %s;'''

            record = (data['exerciseTime'], data['exerciseTime'], data['exerciseName'],
                        data['date'], user_id, user_id, exerciseRecord_id, recordType)            
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

        return {'result' : 'success'} , 200


    # 운동 레코드에서 항목 삭제하는 api
    @jwt_required()
    def delete(self, exerciseRecord_id) :
        user_id = get_jwt_identity()

        try :
            connection = get_connection()
            query = '''delete from exerciseRecord
                    where userId = %s and id = %s;'''
            
            record = (user_id, exerciseRecord_id)

            cursor = connection.cursor()
            cursor.execute(query, record)

            connection.commit()

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"result" : "fail", "error" : str(e)}, 500

        return {'result' : 'success'}, 200

class ExerciseKeywordSearchResource(Resource):
    # 키워드로 운동 데이터 검색하는 api
    @jwt_required()
    def get(self) :

        keyword = request.args.get('keyword')
        offset = request.args.get('offset')
        limit = request.args.get('limit')

        try :
            connection = get_connection()

            query = '''select * from exercise
                    where exercise like '%''' + keyword + '''%'
                    limit ''' + offset + ''', '''+ limit + ''';'''


            # record = (user_id, )

            cursor = connection.cursor(dictionary=True)

            cursor.execute(query,)

            result_list = cursor.fetchall()

            # i = 0
            # for row in result_list :
            #     result_list[i]['avg'] = float(row['avg'])
            #     i = i + 1


            cursor.close()
            connection.close()


        except Error as e :
            print(e)            
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 500


        return {"result" : "success" ,
                "items" : result_list , 
                "count" : len(result_list)}, 200

class ExerciseSelectSearchResource(Resource):
    # 검색한 결과에서 클릭한 운동의 데이터를 가지고 오는 API
    # 30분 운동한 kcal 를 default 값으로
    @jwt_required()
    def get(self, exercise_id):
        
        date = request.args.get('date')

        user_id = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''select id, exercise ,round( kcalBurn * (select nowWeight 
                    from diary 
                    where userId = %s and date = %s) * 30, 2) as totalKcalBurn
                    from exercise
                    where id = %s;'''


            record = (user_id, date, exercise_id)

            cursor = connection.cursor(dictionary=True)

            cursor.execute(query,record)

            result_list = cursor.fetchall()

            cursor.close()
            connection.close()


        except Error as e :
            print(e)            
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 500


        
        return {"result" : "success" ,
                "items" : result_list , 
                "count" : len(result_list)}, 200

# 유저가 직접 운동 칼로리 입력하고 수정하는 API 부분
class ExerciseUserDirectResource(Resource):
   # 유저가 직접 운동 칼로리 입력하는 API
    @jwt_required()
    def post(self) :
        # {
        # "exerciseName": "줄넘기",
        # "exerciseTime": 30,
        # "totalKcalBurn": 200,
        # "date": "2023-03-05"
        # }
        recordType = request.args.get('recordType')

        data = request.get_json()
        user_id = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''insert into exerciseRecord(userId, exerciseName, exerciseTime, totalKcalBurn, date, recordType)
                        values
                        (%s, %s, %s, %s, %s,%s );'''

            record = ( user_id, data['exerciseName'], data['exerciseTime'], 
                        data['totalKcalBurn'], data['date'], recordType)
            
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


class ExerciseUserDirectModifyResource(Resource):
    # 유저가 직접 입력한 운동 칼로리 수정하는 API
    @jwt_required()
    def put(self, exerciseRecord_id):

        recordType = request.args.get('recordType')
    
        # {
        #     "exerciseName": "사이클링, 산악 자전거, BMX",
        #     "exerciseTime": 30,
        #     "date": "2023-03-05"
        # }

        data = request.get_json()
        user_id = get_jwt_identity()

        try :
            connection = get_connection()
            query = '''update exerciseRecord
                    set
                    exerciseName =%s, exerciseTime = %s, totalKcalBurn = %s, date=%s
                    where userId = %s and id = %s and recordType = %s;
                    '''

            record = (data['exerciseName'], data['exerciseTime'], data['totalKcalBurn'],
            data['date'], user_id, exerciseRecord_id,recordType )            
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

        return {'result' : 'success'} , 200


class ExerciseDateKcalSum(Resource):
    @jwt_required()
    def get(self) :
        date = request.args.get('date')

        user_id = get_jwt_identity()

        try :
            connection = get_connection()
            query = ''' select userId, date, round(sum(totalKcalBurn), 2) as exerciseDateKcal
                    from exerciseRecord
                    where userId = %s and date = %s
                    group by date;
                    '''

            record = (user_id , date)

            cursor = connection.cursor(dictionary=True)

            cursor.execute(query, record)

            result_list = cursor.fetchall()

            i = 0
            for row in result_list :
                result_list[i]['date'] = row['date'].isoformat()
                i = i + 1

            cursor.close()
            connection.close()

        except Error as e :
            print(e)            
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 500
                
        return {"result" : "success" ,
                "item" : result_list[0]}, 200


class ExerciseDateKcalList(Resource):
    @jwt_required()
    def get(self) :
        date = request.args.get('date')
        offset = request.args.get('offset')
        limit = request.args.get('limit')

        user_id = get_jwt_identity()

        try :
            connection = get_connection()
            query = f''' select * from
                    exerciseRecord
                    where userId = %s and date = %s
                    limit {limit} offset {offset};'''

            record = (user_id, date)

            cursor = connection.cursor(dictionary=True)

            cursor.execute(query, record)

            result_list = cursor.fetchall()

            i = 0
            for row in result_list :
                result_list[i]['date'] = row['date'].isoformat()
                i = i + 1

            cursor.close()
            connection.close()

        except Error as e :
            print(e)            
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 500
                
        return {"result" : "success" ,
                "items" : result_list,
                "count" : len(result_list)}, 200

                