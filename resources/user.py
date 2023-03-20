from datetime import datetime
from flask import request
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
from flask_restful import Resource
from mysql.connector import Error
import boto3
from config import Config
from mysql_connection import get_connection
from email_validator import validate_email, EmailNotValidError
from flask_jwt_extended import get_jwt_identity
from utils import check_password, hash_password
import pickle
import numpy as np


# 회원가입
class UserRegisterResource(Resource) :
    def post(self) :
        # {
        #     "email": "ccc@naver.com",
        #     "nickName": "나나나"
        #     "password": "1234",
        # }

        # 1. 클라이언트가 보낸 데이터를 받아준다.
        data = request.get_json()

        # 2. 이메일 주소형식이 올바른지 확인한다.
        try :
            validate_email( data["email"] )
        except EmailNotValidError as e :
            print(str(e))
            return {"error" : str(e)}, 400

        # 3. 비밀번호의 길이가 유효한지 체크한다.
        # 만약, 비번이 4자리 이상 12자리 이하다라면, 

        if len(data['password']) < 4 or len(data['password']) > 12 :
            return {'error' : '비밀번호 길이 확인'} , 400

        # 4. 비밀번호를 암호화 한다.
        hashed_password = hash_password(data['password'])
        print(hashed_password)

        # 5. DB 에 회원정보를 저장한다.

        try :
            # 데이터베이스 연결 코드
            connection = get_connection()
            query = '''insert into user(email,nickName, password)
                    values
                    (%s, %s, %s);'''
                    
            record = (data['email'], data['nickName'], hashed_password)

            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()

            ### DB에 회원가입하여, insert 된 후에
            ### user 테이블의 id 값을 가져오는 코드
            user_id = cursor.lastrowid

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 500

        ## user_id 를 바로 클라이언트에게 보내면 안되고,
        ## JWT 로 암호화 해서, 인증토큰을 보낸다

        # expires_delta 는 만료시간 파라미터
        # create_access_token(user_id, 
        #                       expires_delta= datetime.timedelta(hours= 10))
        
        access_token = create_access_token(user_id)


        return {"result" : "success", "access_token" : access_token}, 200

# 유저 추가정보 API
class UserInfoResource(Resource):
    @jwt_required()
    def post(self) :
        data = request.get_json()
        user_id = get_jwt_identity()

        s3 = boto3.resource('s3',
                        aws_access_key_id = Config.ACCESS_KEY,
                        aws_secret_access_key = Config.SECRET_ACCESS)

        kmeans = pickle.loads(s3.Bucket(Config.S3_BUCKET).Object("pickled_kmeans.p").get()['Body'].read())
        scaler = pickle.loads(s3.Bucket(Config.S3_BUCKET).Object("pickled_scaler.p").get()['Body'].read())

        new_data = np.array([data['gender'], data['height'], data['nowWeight']])
        new_data = new_data.reshape(1, 3)
        new_data = scaler.transform(new_data)
        group = kmeans.predict(new_data)[0]

        group = int(group)
        print(group)


        # {
        #     "gender": 1,
        #     "age": 23,
        #     "height": 160.3,
        #     "nowWeight": 50.2,
        #     "hopeWeight": 47.3,
        #     "activity": 1
        # }
        


        try :
            connection = get_connection()

        

            query = '''insert into userInfo(userId, gender, age, height,nowWeight, hopeWeight, activity, `group`)
                       values
                       (%s, %s, %s,%s, %s, %s, %s, %s);'''
            record = ( user_id, data['gender'],
                        data['age'], data['height'], data['nowWeight'],data['hopeWeight'],data['activity'] ,group)
            
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


# 유저 목표 정보 입력 API
class UserTargetResource(Resource):
        # 리뷰 평가 api
    @jwt_required()
    def post(self) :

        # {
        #     "targetKcal": 1400,
        #     "targetCarbs": 100,
        #     "targetProtein": 150,
        #     "targetFat": 130
        # }
        
        data = request.get_json()
        user_id = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''insert into userTarget(userId, targetKcal, targetCarbs, targetProtein,targetFat)
                       values
                       (%s, %s, %s,%s, %s);'''
            record = ( user_id, data['targetKcal'],
                        data['targetCarbs'], data['targetProtein'], data['targetFat'])
            
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

# # 로그인
class UserLoginResource(Resource) :
    def post(self) :
        #   {"email": "qqq@naver.com",
        #     "password": "1234"}

        data = request.get_json()

        # 2. DB 로부터 해당 유저의 데이터를 가져온다.
        try :
            connection = get_connection()

            # 변수부분은 %s 처리
            query = '''select * 
                    from user
                    where email = %s;'''

            # 변수와 매칭되는 데이터를 가져온다
            record = (data['email'], )

            cursor = connection.cursor(dictionary= True)
            cursor.execute(query, record)
            
            result_list = cursor.fetchall()

            if len(result_list) == 0 :
                return {"error" : '회원가입한 사람 아닙니다.'}, 400

            i = 0
            for row in result_list :
                result_list[i]['createdAt'] = row['createdAt'].isoformat()
                i = i + 1

            cursor.close()
            connection.close()

        except Error as e :
            print(str(e))
            cursor.close()
            connection.close()
            return {'error' : str(e)}, 500


        print(result_list)

        # 3. 비밀번호가 맞는지 확인한다.
        check = check_password(data['password'], result_list[0]['password'])

        if check == False :
            return {'error' : '비밀번호가 잘못됐습니다.'}, 400
            
        # 4. jwt 토큰을 만들어서 클라이언트에게 보낸다.
        access_token = create_access_token( result_list[0]['id'] )


        return {'result' : 'success', 'access_token' : access_token}, 200


# #### 로그아웃 ####
# # 로그아웃된 토큰을 저장할 set 만든다.
jwt_blacklist = set()

class UserLogoutResource(Resource) :
    @jwt_required()
    def post(self) :
    
        jti = get_jwt()['jti']
        print(jti)
        jwt_blacklist.add(jti)

        return {'result' : 'success'}, 200


# 닉네임 변경
class UserNicknameResetResource(Resource):
    @jwt_required()
    def put(self) :
        user_id = get_jwt_identity()
        data = request.get_json() 

        if "nickName" in data:
            # 닉네임이 이미 존재하는지 확인한다.
            try:
                connection = get_connection()
                query = """
                    SELECT nickName FROM user WHERE nickName = %s;
                    """
                cursor = connection.cursor()
                cursor.execute(query, (data['nickName'], ))
                record = cursor.fetchone()
                cursor.close()
                connection.close()
                
                if record:
                    return {'error': '이미 존재하는 닉네임입니다.'}, 400
            except Error as e:
                print(e)
                cursor.close()
                connection.close()
                return {'error': str(e) }, 500 # 500은 서버에러를 리턴하는 에러코드
            
            try :
                connection = get_connection()

                query = f'''update user
                    set nickName = %s
                        where id = {user_id};'''

                record = (data['nickName'],)
                cursor = connection.cursor(dictionary= True)
                cursor.execute(query, record)

                connection.commit()

                cursor.close()
                connection.close()

            except Error as e :
                print(e)
                cursor.close()
                connection.close()
                return {'error' : str(e)}, 500

            return {'result' : 'success',}, 200

#  이메일 중복확인
class UserEmailUniqueResource(Resource) :
    def get(self) :    
        try :
            # DB에 연결
            connection = get_connection()

            # 쿼리문 만들기
            query = '''select email
                    from user;'''

            # select 문은, dictionary = True 를 해준다.
            cursor = connection.cursor(dictionary = True)

            # 실행
            cursor.execute(query,)

            # select 문은, 아래 함수를 이용해서, 데이터를 가져온다.
            result_list = cursor.fetchall()

            # 자원해제
            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            cursor.close()
            connection.close()

            return {"error" : str(e), 'error_no' : 20}, 503

        return { "result" : "success" ,
            "items" : result_list }, 200



# 닉네임 중복확인
class UserNicknameUniqueResource(Resource) :
    def get(self) :    
        try :
            # DB에 연결
            connection = get_connection()

            # 쿼리문 만들기
            query = '''select nickName
                    from user;'''

            # select 문은, dictionary = True 를 해준다.
            cursor = connection.cursor(dictionary = True)

            # 쿼리문을 커서를 이용해서 실행한다
            cursor.execute(query,)

            # select 문은, 아래 함수를 이용해서, 데이터를 가져온다.
            result_list = cursor.fetchall()

            # 자원해제
            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            cursor.close()
            connection.close()

            return {"error" : str(e), 'error_no' : 20}, 503

        return { "result" : "success" ,
            "items" : result_list }, 200


## 유저 추가정보 수정 API
class UserInfoEditResource(Resource):
    @jwt_required()
    def put(self) :
         
        data = request.get_json()
        user_id = get_jwt_identity()

        s3 = boto3.resource('s3',
                        aws_access_key_id = Config.ACCESS_KEY,
                        aws_secret_access_key = Config.SECRET_ACCESS)

        kmeans = pickle.loads(s3.Bucket(Config.S3_BUCKET).Object("pickled_kmeans.p").get()['Body'].read())
        scaler = pickle.loads(s3.Bucket(Config.S3_BUCKET).Object("pickled_scaler.p").get()['Body'].read())

        new_data = np.array([data['gender'], data['height'], data['nowWeight']])
        new_data = new_data.reshape(1, 3)
        new_data = scaler.transform(new_data)
        group = kmeans.predict(new_data)[0]

        group = int(group)
        print(group)

        # {
        #     "gender": 1,
        #     "age": 23,
        #     "height": 160.3,
        #     "nowWeight": 50.2,
        #     "hopeWeight": 47.3,
        #     "activity": 1
        # }
       

        try :
            connection = get_connection()

            query = '''update userInfo
                    set gender = %s, age= %s , height = %s, nowWeight = %s, hopeWeight = %s, activity = %s, `group`= %s
                    where userId = %s;
                    '''
            record = ( data['gender'],
                        data['age'], data['height'], data['nowWeight'],data['hopeWeight'],data['activity'] ,group ,user_id)
            
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

class UserTargetEditResource(Resource):
    @jwt_required()
    def put(self) :

        # {
        #     "targetKcal": 1400,
        #     "targetCarbs": 100,
        #     "targetProtein": 150,
        #     "targetFat": 130
        # }
        
        data = request.get_json()
        user_id = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''update userTarget
                        set targetKcal = %s, targetCarbs = %s, targetProtein = %s ,targetFat = %s
                        where userId = %s;'''
            record = ( data['targetKcal'],
                        data['targetCarbs'], data['targetProtein'], data['targetFat'], user_id)
            
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