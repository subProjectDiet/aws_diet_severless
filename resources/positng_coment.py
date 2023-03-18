from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from mysql.connector import Error

from flask_jwt_extended import get_jwt_identity
from mysql_connection import get_connection
from datetime import datetime


#포스팅 댓글 작성, 댓글조회
class PostingComentResource(Resource) :
    @jwt_required()
    def post(self,posting_id):
        data = request.get_json()

        # 유저 토큰으로부터 user_id 반환
        user_id = get_jwt_identity()

        try :
            # DB에 연결
            connection = get_connection()

            # 쿼리문 만들기
            query = '''insert into postingComment (userId , postingId , content)
                        values ( %s,%s, %s);'''

            record = (user_id, posting_id, data['content'])

            # 커서를 가져온다.
            cursor = connection.cursor()

            # 쿼리문을 커서를 이용해서 실행한다
            cursor.execute(query, record)

            # 커넥션을 커밋해줘야한다 => 디비에 영구적으로 반영하는것
            connection.commit()

            # 자원 해제
            cursor.close()
            connection.close()


        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)}, 500
                
        return {'result' : 'success'} , 200


    
    def get(self,posting_id):
        offset = request.args.get('offset')
        limit = request.args.get('limit')
        
        try :
            # DB에 연결
            connection = get_connection()

            # 쿼리문 만들기
            query = f'''select pc.id , u.nickName ,pc.content, pc.createdAt , pc.updatedAt
                            from postingComment pc
                            left join user u
                            on pc.userId = u.id
                            where postingId = %s
                            limit {limit} offset {offset};'''

            record = (posting_id, )

            # select 문은, dictionary = True 를 해준다.
            cursor = connection.cursor(dictionary = True)

            # 커서를 이용해서 쿼리문을 실행한다.
            cursor.execute(query, record )

            # select 문은, 아래 함수를 이용해서, 데이터를 가져온다.
            result_list = cursor.fetchall()

            # print(result_list)

            # 중요! 디비에서 가져온 timestamp 난
            # 파이썬의 datetime 으로 자동 변경된다.
            # json은 datetime 같은게 없다 그냥 문자열이다
            # 문제는! 이 데이터를 json 으로 바로 보낼 수 없으므로,
            # 문자열로 바꿔서 다시 저장해서 보낸다.
            i = 0
            for record in result_list :
                result_list[i]['createdAt'] = record['createdAt'].isoformat()
                result_list[i]['updatedAt'] = record['updatedAt'].isoformat()
                i = i + 1

            cursor.close()
            connection.close()    
    

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)}, 500
                
        return {"result" : "success" ,
                "items" : result_list , 
                "count" : len(result_list)}, 200    
    
    
    
#수정 및 삭제
class PostingComentEditResource(Resource) :
    @jwt_required()
    def put(self,posting_id,comment_id):
        data = request.get_json()
        user_id = get_jwt_identity()
    
        try:
            connection = get_connection()


            query = '''update postingComment set
                content = %s
                where postingId =%s  and id =%s  and  userId = %s;'''

            record = ( data['content'],posting_id,comment_id,user_id)

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
    def delete(self, posting_id,comment_id) :

        user_id = get_jwt_identity()

        try :
            connection = get_connection()
            query = '''delete from postingComment
                where id =%s and postingId = %s and userId=%s;'''
            record = (comment_id,posting_id ,user_id)
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
    
    
