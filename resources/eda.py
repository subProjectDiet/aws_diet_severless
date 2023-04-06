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


class DayEdaResource(Resource):
    @jwt_required()
    def get(self) :

        date = request.args.get('date')
        user_id = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''select d.userId, d.date, round(ifnull( d.nowWeight, 0),1) as nowWeight, round(ifnull(sum(f.kcal), 0),0) as totalKcal, round(ifnull(sum(e.totalKcalBurn), 0),0) as totalKcalBurn
                        from diary d
                        left join foodRecord f
                        on d.userId = f.userId and d.date = f.date
                        left join exerciseRecord e
                        on d.userId = e.userId and d.date = e.date
                        where d.userId = %s and date_format(d.date, '%Y-%m') = %s
                        group by d.date
                        order by d.date desc
                        limit 5;'''

            record = (user_id, date)

            cursor = connection.cursor(dictionary=True)

            cursor.execute(query, record)

            result_list = cursor.fetchall()
            print(result_list)

            

            i = 0
            for row in result_list :
                result_list[i]['date'] = row['date'].isoformat()
                result_list[i]['nowWeight'] = float(row['nowWeight'])
                result_list[i]['totalKcal'] = float(row['totalKcal'])

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


class WeekEdaResource(Resource):
    @jwt_required()
    def get(self) :

        user_id = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''select d.userId, round(ifnull(avg(nowWeight),0),1) as AvgWeight , round(ifnull(avg(f.kcal),0),1) as AvgKcal ,
                        round(ifnull(avg(e.totalKcalBurn), 0),0) as AvgKcalBurn,
                        date_format(DATE_SUB(d.date, interval (DAYOFWEEK(d.date)-1) day), '%Y-%m-%d') as start,
                        date_format(DATE_SUB(d.date, interval (DAYOFWEEK(d.date)-7) day), '%Y-%m-%d') as end
                        from diary d
                        left join foodRecord f
                        on d.userId = f.userId and d.date = f.date
                        left join exerciseRecord e
                        on d.userId = e.userId and d.date = e.date
                        where d.userId = %s 
                        group by start
                        order by start desc
                        limit 5;'''

            record = (user_id, )

            cursor = connection.cursor(dictionary=True)

            cursor.execute(query, record)

            result_list = cursor.fetchall()
            print(result_list)

            

            i = 0
            for row in result_list :
                # result_list[i]['date'] = row['date'].isoformat()
                result_list[i]['AvgWeight'] = float(row['AvgWeight'])
                result_list[i]['AvgKcal'] = float(row['AvgKcal'])
                result_list[i]['AvgKcalBurn'] = float(row['AvgKcalBurn'])

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

class MonthEdaResource(Resource):
    @jwt_required()
    def get(self) :
        
        user_id = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''select  d.userId,  month(d.date) as `month`, round(ifnull(avg(nowWeight),0),1) as AvgWeight,
                        round(ifnull(avg(f.kcal),0),0) as AvgKcal,
                        round(ifnull(avg(e.totalKcalBurn), 0),0) as AvgKcalBurn
                        from diary d
                        left join foodRecord f
                        on d.userId = f.userId and d.date = f.date
                        left join exerciseRecord e
                        on d.userId = e.userId and d.date = e.date
                        where d.userId = %s 
                        group by `month`
                        order by `month`
                        limit 5'''

            record = (user_id, )

            cursor = connection.cursor(dictionary=True)

            cursor.execute(query, record)

            result_list = cursor.fetchall()

            i = 0
            for row in result_list :
                # result_list[i]['start'] = row['start'].isoformat()
                # result_list[i]['end'] = row['end'].isoformat()
                result_list[i]['AvgWeight'] = float(row['AvgWeight'])
                result_list[i]['AvgKcal'] = float(row['AvgKcal'])

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
