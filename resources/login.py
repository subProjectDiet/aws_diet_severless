from datetime import datetime
from flask import request
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
from flask_restful import Resource
from mysql.connector import Error

from mysql_connection import get_connection
from email_validator import validate_email, EmailNotValidError
from flask_jwt_extended import get_jwt_identity
from utils import check_password, hash_password


    
#  이메일 중복확인
class UserEmailUniqueResource(Resource) :
    def get(self) :    
        
        email = request.args.get('email')

        try:
            # DB에 연결
            connection = get_connection()

            # 쿼리문 만들기
            query = f'''select email
                    from user  where email='{email}';'''

            # select 문은, dictionary=True를 해준다.
            cursor = connection.cursor(dictionary=True)

            # 쿼리문을 커서를 이용해서 실행한다
            cursor.execute(query)

            # 결과 가져오기
            result = cursor.fetchone()

            # 자원해제
            cursor.close()
            connection.close()

 
            if result:
                return {"error": "중복된 이메일이 존재합니다."}, 400
            else:
                return {"message": "사용 가능한 이메일입니다."}, 200

        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return {"error": str(e)}, 500




# 닉네임 중복확인
class UserNicknameUniqueResource(Resource) :
    def get(self) :    
        nickname = request.args.get('nickName')

        try:
            # DB에 연결
            connection = get_connection()

            # 쿼리문 만들기
            query = f'''select nickName
                    from user  where nickName='{nickname}';'''

            # select 문은, dictionary=True를 해준다.
            cursor = connection.cursor(dictionary=True)

            # 쿼리문을 커서를 이용해서 실행한다
            cursor.execute(query)

            # 결과 가져오기
            result = cursor.fetchone()

            # 자원해제
            cursor.close()
            connection.close()

 
            if result:
                return {"error": "중복된 닉네임이 존재합니다."}, 400
            else:
                return {"message": "사용 가능한 닉네임입니다."}, 200

        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return {"error": str(e)}, 500

        
