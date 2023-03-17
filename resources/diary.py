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

class DiaryEdaResource(Resource):
    @jwt_required()
    def get(self) :

        eda_result = []
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

            eda_result.append("가장 많이 먹은 음식 및 칼로리")
            eda_result.append(result_list)


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

            eda_result.append("가장 많이 먹은 날")
            eda_result.append(result_list)


            # 운동을 가장 많이한 날

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
            
            eda_result.append("운동을 가장 많이 한 날")
            eda_result.append(result_list)


            # 평균 음식 칼로리
            query = '''select userId , avg(kcal) as foodAvgKcal
                    from foodRecord
                    where userId = %s and date_format(date, '%Y-%m') = %s
                    group by date_format(date, '%Y-%m') = %s;'''

            record = (user_id , date, date)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()

            if len(result_list) == 0 :
                return {"error" : '해당 데이터는 존재하지 않습니다.'}, 400

            
            i = 0
            for row in result_list :
                result_list[i]['foodAvgKcal'] = float(row['foodAvgKcal'])
                i = i + 1

            eda_result.append("평균 음식 칼로리")
            eda_result.append(result_list)

            # 평균 운동 칼로리
            query = '''
                    select userId , avg(totalKcalBurn) as exerciseAvgKcal
                    from exerciseRecord
                    where userId = %s and date_format(date, '%Y-%m') = %s
                    group by date_format(date, '%Y-%m') = %s;'''

            record = (user_id , date, date)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()

            if len(result_list) == 0 :
                return {"error" : '해당 데이터는 존재하지 않습니다.'}, 400

            i = 0
            for row in result_list :
                result_list[i]['exerciseAvgKcal'] = float(row['exerciseAvgKcal'])
                i = i + 1

            eda_result.append("평균 운동 칼로리")
            eda_result.append(result_list)


            # 평균 몸무게
            query = '''select userId, avg(nowWeight) as weightAvg
                    from diary
                    where userId = %s and date_format(date, '%Y-%m') = %s
                    group by date_format(date, '%Y-%m') = %s;'''

            record = (user_id , date, date)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()

            if len(result_list) == 0 :
                return {"error" : '해당 데이터는 존재하지 않습니다.'}, 400

            i = 0
            for row in result_list :
                result_list[i]['weightAvg'] = float(row['weightAvg'])
                i = i + 1

            eda_result.append("평균 몸무게")
            eda_result.append(result_list)

            # 이달의 감량 몸무게
            query = '''select userId, max(nowWeight) - min(nowWeight) as burnKcal
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
                result_list[i]['burnKcal'] = float(row['burnKcal'])
                i = i + 1

            eda_result.append("이달의 감량 몸무게")
            eda_result.append(result_list)


            # 평균 영양소별 섭취량

            query = '''select userId, round(avg(carbs), 2) as avgCarbs, round(avg(protein), 2) as avgProtein, round(avg(fat), 2) as avgFat
                    from foodRecord
                    where userId = %s and date_format(date, '%Y-%m') = %s
                    group by date_format(date, '%Y-%m') = %s;'''

            record = (user_id , date, date)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()

            if len(result_list) == 0 :
                return {"error" : '해당 데이터는 존재하지 않습니다.'}, 400

            i = 0
            for row in result_list :
                result_list[i]['avgCarbs'] = float(row['avgCarbs'])
                result_list[i]['avgProtein'] = float(row['avgProtein'])
                result_list[i]['avgFat'] = float(row['avgFat'])

                i = i + 1

            eda_result.append("평균 영양소별 섭취량")
            eda_result.append(result_list)



            cursor.close()
            connection.close()



        except Error as e :
            print(e)            
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 500
                
        return {"result" : "success" ,
                "items" : eda_result,
                "count" : len(eda_result)}, 200


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


                