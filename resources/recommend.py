from datetime import datetime
from flask import request
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
from flask_restful import Resource
from mysql.connector import Error

from mysql_connection import get_connection
from email_validator import validate_email, EmailNotValidError
from flask_jwt_extended import get_jwt_identity


class KmeansRecommendResource(Resource):
    @jwt_required()
    def get(self):

        user_id = get_jwt_identity()

        try : 
            connection = get_connection()
            query = '''select p.id as postingId, ui.userId, u.nickName,  p.content, p.imgUrl, p.createdAt, p.updatedAt, count(l.postingId) as likeCnt, ui.`group`,
                        if(l.userId is null, 0 , 1) as isLike 
                        from userInfo ui
                        join user u
                        on ui.userId = u.id
                        left join posting p
                        on ui.userId = p.userId
                        join likePosting l
                        on p.id = l.postingId
                        where `group` = (select `group`
                                        from user u  
                                        join userInfo ui
                                        on u.id = ui.userId
                                        where u.id = %s)
                        group by l.postingId
                        order by likeCnt desc
                        limit 1;'''

            record = (user_id, )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)

            result_list = cursor.fetchall()

            i = 0
            for row in result_list :
                result_list[i]['createdAt'] = row['createdAt'].isoformat()
                result_list[i]['updatedAt'] = row['updatedAt'].isoformat()

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

