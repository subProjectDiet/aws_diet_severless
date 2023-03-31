from datetime import datetime
from flask import request
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
from flask_restful import Resource
from mysql.connector import Error

from mysql_connection import get_connection
from email_validator import validate_email, EmailNotValidError
from flask_jwt_extended import get_jwt_identity

# 다이어리에 유저 몸무게 입력 
# ex) 2023-03-05 , 50(kg)
class DiaryUserWeightResource(Resource):
    @jwt_required()
    def post(self) :
        
        # {
        #     "nowWeight": 50,
        #     "date": "2023-03-05"
        # }
        
        data = request.get_json()
        user_id = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''insert into diary(userId, nowWeight, date)
                    values
                    (%s, %s, %s);'''
            record = ( user_id, data['nowWeight'], data['date'] )
            
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


    @jwt_required()
    def put(self):

        # {
        #     "nowWeight": 55,
        #     "date": "2023-03-05"
        # }

        data = request.get_json()
        user_id = get_jwt_identity()

        try :
            connection = get_connection()
            query = '''
                    update diary
                    set nowWeight = %s
                    where userId = %s and date = %s;'''

            record = (data['nowWeight'], user_id ,data['date'] )            
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
    

    # 특정한 날 몸무게 데이터 가져오는 API
    @jwt_required()
    def get(self):
        date = request.args.get('date')

        user_id = get_jwt_identity()
        try : 
            connection = get_connection()

            query = '''select *
                    from diary
                    where userId = %s and date = %s;'''


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
            return {'error' : str(e)} , 500


        return {'result' : 'success',
                'items' : result_list[0] ,
                'count' : len(result_list)  }, 200

# 1  특정 달에 가장 많이 먹은 음식 및 그 음식의 칼로리 평균과 그 음식을 섭취한 수

class EatKcalAvgCountResource(Resource):
    @jwt_required()
    def get(self) :

        date = request.args.get('date')
        user_id = get_jwt_identity()

        try :
            # 특정 달에 가장 많이 먹은 음식 및 그 음식의 칼로리 평균과 그 음식을 섭취한 수
            connection = get_connection()
            query = ''' select userId, foodName, kcal, count(foodName) as cnt
                        from foodRecord
                        where userId = %s and date_format(date, '%Y-%m') = %s
                        group by foodName
                        order by cnt desc
                        limit 1;'''

            record = (user_id , date)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()

            if len(result_list) == 0 :
                return {"error" : '해당 데이터는 존재하지 않습니다.'}, 400


            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)} , 500


        return {'result' : 'success',
                'items' : result_list[0] ,
                'count' : len(result_list)  }, 200

# 2 가장 많이 먹은 날의 칼로리
class EatManyDayEdaResource(Resource):
    @jwt_required()
    def get(self) :

        date = request.args.get('date')
        user_id = get_jwt_identity()

        try :
            connection = get_connection()
            # 가장 많이 먹은 날의 칼로리
            query = ''' select userId, kcal, date
                    from foodRecord
                    where userId = %s and date_format(date, '%Y-%m') = %s
                    order by kcal desc
                    limit 1;'''

            record = (user_id , date)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()

            if len(result_list) == 0 :
                return {"error" : '해당 데이터는 존재하지 않습니다.'}, 400

            
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
            return {'error' : str(e)} , 500


        return {'result' : 'success',
                'items' : result_list[0] ,
                'count' : len(result_list)  }, 200

# 3.# 운동을 가장 많이한 날
class ExerciseManyDayEdaResource(Resource):
    @jwt_required()
    def get(self) :

        date = request.args.get('date')
        user_id = get_jwt_identity()

        try :
            connection = get_connection()
            query = '''select userId, date, sum(totalKcalBurn) as monthTotal
            from exerciseRecord
            where userId = %s and date_format(date, '%Y-%m') = %s
            group by date
            order by monthTotal desc
            limit 1;'''

            record = (user_id , date)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()

            if len(result_list) == 0 :
                return {"error" : '해당 데이터는 존재하지 않습니다.'}, 400

            
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
            return {'error' : str(e)} , 500


        return {'result' : 'success',
                'items' : result_list[0] ,
                'count' : len(result_list)  }, 200

# 4. 이달의 감량 몸무게
class MonthBurnWeightEdaResource(Resource):
    @jwt_required()
    def get(self) :

        date = request.args.get('date')
        user_id = get_jwt_identity()

        try :
            connection = get_connection()
            query = '''select userId, max(nowWeight) - min(nowWeight) as burnWeight
                    from diary
                    where userId = %s and date_format(date, '%Y-%m') = %s
                    order by date desc;'''

            record = (user_id , date)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()

            if len(result_list) == 0 :
                return {"error" : '해당 데이터는 존재하지 않습니다.'}, 400

            i = 0
            for row in result_list :
                result_list[i]['burnWeight'] = float(row['burnWeight'])
                i = i + 1


            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)} , 500


        return {'result' : 'success',
                'items' : result_list[0] ,
                'count' : len(result_list)  }, 200

# 5. # 특정달 평균 몸무게  평균 음식 칼로리, 평균 영양소 섭취량, 평균운동칼로리
class AvgGetDataEdaResource(Resource):
    @jwt_required()
    def get(self) :
        date = request.args.get('date')
        user_id = get_jwt_identity()

        try :
            connection = get_connection()
            query = '''select fr.userId, avg(kcal) as AvgKcal, avg(carbs) as AvgCarbs, avg(protein) as AvgProtein, avg(fat) as AvgFat, avg(totalKcalBurn) as AvgKcalBurn, avg(nowWeight) as AvgWeight
                        from foodRecord fr
                        left join diary d
                        on fr.userId = d.userId
                        left join exerciseRecord er
                        on fr.userId = er.userId
                        where fr.userId = %s and date_format(fr.date, '%Y-%m') = %s
                        group by fr.userId;'''

            record = (user_id , date)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()

            if len(result_list) == 0 :
                return {"error" : '해당 데이터는 존재하지 않습니다.'}, 400

            i = 0
            for row in result_list :
                result_list[i]['AvgKcal'] = float(row['AvgKcal'])
                result_list[i]['AvgCarbs'] = float(row['AvgCarbs'])
                result_list[i]['AvgProtein'] = float(row['AvgProtein'])
                result_list[i]['AvgFat'] = float(row['AvgFat'])
                result_list[i]['AvgKcalBurn'] = float(row['AvgKcalBurn'])
                result_list[i]['AvgWeight'] = float(row['AvgWeight'])

                i = i + 1


            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)} , 500


        return {'result' : 'success',
                'items' : result_list[0] ,
                'count' : len(result_list)  }, 200





class DiaryMonthListResource(Resource):
    @jwt_required()
    def get(self) :

        date = request.args.get('date')

        user_id = get_jwt_identity()

        try :
            connection = get_connection()
            query = '''select d.userId, d.nowWeight ,d.date , ifnull(sum(f.kcal), "") as foodKcal, ifnull(sum(e.totalKcalBurn),"") as exerciseKcal
                    from diary d
                    left join foodRecord f
                    on d.userId = f.userId and d.date = f.date
                    left join exerciseRecord e
                    on d.userId = e.userId and d.date = e.date
                    where d.userId = %s and date_format(d.date, '%Y-%m') = %s
                    group by d.date
                    order by d.date;'''

            record = (user_id, date)

            cursor = connection.cursor(dictionary=True)

            cursor.execute(query, record)

            result_list = cursor.fetchall()
            print(result_list)


            i = 0
            for row in result_list :
                result_list[i]['date'] = row['date'].isoformat()
                result_list[i]['nowWeight'] = float(row['nowWeight'])
                result_list[i]['foodKcal'] = str(row['foodKcal'])
                result_list[i]['exerciseKcal'] = str(row['exerciseKcal'])


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

class GetUserTargetIngoResource(Resource):
# 유저가 입력한 목표 탄단지 데이터 가져오는 API
    @jwt_required()
    def get(self):

        user_id = get_jwt_identity()
        try : 
            connection = get_connection()

            query = '''select id, userId, targetKcal, targetCarbs, targetProtein, targetFat
                        from userTarget
                        where userId = %s;'''

            record = (user_id , )

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)

            result_list = cursor.fetchall()



            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)} , 500


        return {'result' : 'success',
                'items' : result_list[0] ,
                'count' : len(result_list)  }, 200