from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from mysql.connector import Error

from flask_jwt_extended import get_jwt_identity
import boto3
import requests
from config import Config
from mysql_connection import get_connection
from datetime import datetime



# 작성한 포스팅 수정 및 삭제
class PostingEditResource(Resource):
    @jwt_required()
    def put(self,posting_id):
       
        user_id = get_jwt_identity()

        if 'photo' not in request.files:

            content = request.form['content']
            # S3에 파일 업로드가 필요 없으므로, 디비에 저장한다.
            try :
                # DB에 연결
                connection = get_connection()

                # 쿼리문 만들기
                query = f'''update posting set

                        content = %s
                        where userId = {user_id} and id = {posting_id};'''

                record = (content,)

                # 커서를 가져온다.
                cursor = connection.cursor()

                # 쿼리문을 커서를 이용해서 실행한다.
                cursor.execute(query, record)

                # 커넥션을 커밋해줘야 한다 => 디비에 영구적으로 반영하라는 뜻
                connection.commit()

                # 자원 해제
                cursor.close()
                connection.close()

            except Error as e :
                print(e)
                cursor.close()
                connection.close()
                return {'error' : str(e)}, 500

            return {'result' : 'success'}, 200

        else :
            content = request.form['content']
            file = request.files['photo']
            # 파일이 있으니까, 파일명을 새로 만들어서
            # S3 에 업로드한다.

            # 2. S3 에 파일 업로드
            # 파일명을 우리가 변경해 준다.
            # 파일명은, 유니크하게 만들어야 한다.
            current_time = datetime.now()
            new_file_name = current_time.isoformat().replace(':', '_') + '.jpg'

            # 유저가 올린 파일의 이름을, 내가 만든 파일명으로 변경
            file.filename = new_file_name

            # S3 에 업로드 하면 된다.
            # AWS 의 라이브러리를 사용해야 한다.
            # 이 파이썬 라이브러리가 boto3 라이브러리다!
            # boto3 라이브러리 설치
            # pip install boto3 

            s3 = boto3.client('s3', 
                        aws_access_key_id = Config.ACCESS_KEY,
                        aws_secret_access_key = Config.SECRET_ACCESS)

            try :
                s3.upload_fileobj(file,
                                    Config.S3_BUCKET,
                                    file.filename,
                                    ExtraArgs = {'ACL':'public-read', 'ContentType':file.content_type} )                 

            except Exception as e :
                return {'error' : str(e)}, 500

            client = boto3.client('rekognition',
                        'ap-northeast-2',
                        aws_access_key_id=Config.ACCESS_KEY,
                        aws_secret_access_key = Config.SECRET_ACCESS)

            response = client.detect_labels(Image={'S3Object':{'Bucket':Config.S3_BUCKET, 'Name':new_file_name}} ,
                                MaxLabels = 5 )

            print(response)

            name_list = []
            for row in response['Labels'] :
                name  = row['Name']  
                
                # 네이버 파파고 API 호출한다.
                headers = {'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8',
                    'X-Naver-Client-Id' : Config.NAVER_CLIENT_ID,
                    'X-Naver-Client-Secret' : Config.NAVER_CLIENT_SECRET}

                data = {'source' : 'en',
                        'target' : 'ko',
                        'text' : name}

                res = requests.post(Config.NAVER_PAPAGO_URL, data, headers= headers)

                
                res = res.json()

                result_text = res['message']['result']['translatedText']
                name_list.append(result_text)



            # 데이터 베이스에 업데이트 해준다.
            imgUrl = Config.S3_LOCATION + new_file_name
            try :
                connection = get_connection()
                



               
                query=  f'''delete from t
                        using tag t
                        left join tagName tn
                        on t.tagId = tn.id
                        left join posting p
                        on p.id = t.postingId
                    where p.userId = {user_id} and t.postingId = {posting_id}'''
                cursor = connection.cursor(dictionary= True)
                cursor.execute(query, )
                connection.commit()
                cursor.close()
                connection.close()    

            except Exception as e :
                return {'error' : str(e)}, 500
                
            
            
            
            
            
            try :
                # DB에 연결
                connection = get_connection()

                # 쿼리문 만들기
                query = f'''update posting set 
                            imgUrl = %s,
                            content = %s
                            where userId = {user_id} and id = {posting_id};'''

                record = (imgUrl, content)

                for name in name_list :
                    query = '''select *
                            from tagName
                            where Name = %s;'''
                    record = (name , )
                    cursor = connection.cursor(dictionary=True)
                    cursor.execute(query, record)
                    result_list = cursor.fetchall()
                    
                    
                    if len(result_list) == 0 :
                        query = '''insert into tagName
                                (Name)
                                values
                                (%s);'''
                        record = (name, )
                        cursor.execute(query, record)
                        tag_id = cursor.lastrowid
                    else :
                        tag_id = result_list[0]['id']


                    
                    # tag테이블에 저장한다.
                    query = '''insert into tag
                            (tagId,postingId)
                            values
                            ( %s, %s);'''
                    record = (tag_id,posting_id )
                    cursor.execute(query, record)




                # 커서를 가져온다.
                cursor = connection.cursor()

                # 쿼리문을 커서를 이용해서 실행한다.
                cursor.execute(query, record)

                # 커넥션을 커밋해줘야 한다 => 디비에 영구적으로 반영하라는 뜻
                connection.commit()

                # 자원 해제
                cursor.close()
                connection.close()

            except Error as e :
                print(e)
                cursor.close()
                connection.close()
                return {'error' : str(e)}, 500

            return {'result' : 'success'}, 200
    

    @jwt_required()
    def delete(self,posting_id):
        user_id = get_jwt_identity()

        try :
            connection = get_connection()
            query = f'''delete from t ,p
                        using tag t
                        left join tagName tn
                        on t.tagId = tn.id
                        left join posting p
                        on p.id = t.postingId
                    where p.userId = {user_id} and t.postingId = {posting_id};'''
            cursor = connection.cursor()
            cursor.execute(query, )
            connection.commit()
            cursor.close()
            connection.close()
        
        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)} , 500


        return {'result' : 'success'}, 200   

    
# 포스팅 작성
class PostingResource(Resource) :
    
    @jwt_required()
    def post(self) :
        
        # 데이터 받아주기
        if 'photo' not in request.files :
            return {'error' : '파일을 업로드 하세요'},400
        if 'content' not in request.form :
            return {'error': '내용을 입력하세요'},400

        file = request.files['photo']
        content = request.form['content']
        user_id =get_jwt_identity()
    
        #파일 이름 설정
        current_time = datetime.now()
        new_file_name = str(user_id) + current_time.isoformat().replace(':','_')+'.jpg'
        
        file.filename = new_file_name
        
        #s3업로드
        client = boto3.client('s3', 
                    aws_access_key_id = Config.ACCESS_KEY,
                    aws_secret_access_key = Config.SECRET_ACCESS)    
        try :
            client.upload_fileobj(file,
                                    Config.S3_BUCKET,
                                    new_file_name,
                                    ExtraArgs = {'ACL':'public-read', 'ContentType' : file.content_type } )
        
        except Exception as e:
            return {'error' : str(e)}, 500


        client = boto3.client('rekognition',
                    'ap-northeast-2',
                    aws_access_key_id=Config.ACCESS_KEY,
                    aws_secret_access_key = Config.SECRET_ACCESS)

        response = client.detect_labels(Image={'S3Object':{'Bucket':Config.S3_BUCKET, 'Name':new_file_name}} ,
                            MaxLabels = 5 )

        print(response)

        name_list = []
        for row in response['Labels'] :
            name  = row['Name']  
              
            # 네이버 파파고 API 호출한다.
            headers = {'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Naver-Client-Id' : Config.NAVER_CLIENT_ID,
                'X-Naver-Client-Secret' : Config.NAVER_CLIENT_SECRET}

            data = {'source' : 'en',
                    'target' : 'ko',
                    'text' : name}

            res = requests.post(Config.NAVER_PAPAGO_URL, data, headers= headers)

            
            res = res.json()

            result_text = res['message']['result']['translatedText']
            name_list.append(result_text)


        # 4. 위에서 나온 결과인, imgURL 과
        #    태그로 저장할 Labels 이름을 가지고
        #    DB에 저장한다.
        imgUrl = Config.S3_LOCATION + new_file_name
        try : 
            connection = get_connection()
            # 4-1. imgUrl과 content를 posting 테이블에 인서트!
            query = '''insert into posting
                    (userId, imgUrl, content)
                    values
                    (%s, %s, %s);'''
            record = (user_id, imgUrl, content )
            cursor = connection.cursor()
            cursor.execute(query, record)
            posting_id = cursor.lastrowid
            print(posting_id)


            #태그 테이블
            for name in name_list :
                query = '''select *
                        from tagName
                        where Name = %s;'''
                record = (name , )
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, record)
                result_list = cursor.fetchall()
                
                
                if len(result_list) == 0 :
                    query = '''insert into tagName
                            (Name)
                            values
                            (%s);'''
                    record = (name, )
                    cursor.execute(query, record)
                    tag_id = cursor.lastrowid
                else :
                    tag_id = result_list[0]['id']


                 
                # tag테이블에 저장한다.
                query = '''insert into tag
                        (tagId,postingId)
                        values
                        ( %s, %s);'''
                record = (tag_id,posting_id )
                cursor.execute(query, record)


            connection.commit()
            cursor.close()
            connection.close()        
        except Error as e:
            print(e)
            cursor.close()
            connection.close()        
            return {'error' : str(e)} , 500

        # 5. 결과를 클라이언트에 보내준다

        return {'result' : 'success'}
    
    
# 포스팅 한개 클릭
class PostingClickResource(Resource):    
    @jwt_required()
    def get(self,posting_id):
        try :
            connection = get_connection()

            query = '''select p.id , u.id ,u.nickName,p.createdAt ,p.imgurl, count(lp.userId)as likeCnt ,p.content
                                from posting p
                                left join user u
                                on p.userId = u.id
                                left join likePosting lp
                                on p.id = lp.postingId
                        where p.id = %s;
                    '''

            record = (posting_id, )
            cursor = connection.cursor(dictionary= True)
            cursor.execute(query,record)

            result_list = cursor.fetchall()

          

            i = 0
            for record in result_list :
                result_list[i]['createdAt'] = record['createdAt'].isoformat()
                i = i + 1

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
        
        
# 내가 작성한 포스팅 리스트 가저오기
class MypostingListResource(Resource) :
    @jwt_required()
    def get(self) :
        offset = request.args.get('offset')
        limit = request.args.get('limit')
        user_id = get_jwt_identity()
        try : 
            connection = get_connection()
            query = '''select *
                    from posting
                    where userId = %s
                    limit ''' + offset + ''', ''' + limit + ''';'''
                    
            record = (user_id , )

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)

            result_list = cursor.fetchall()

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
            return {'error' : str(e)} , 500


        return {'result' : 'success',
                'items' : result_list ,
                'count' : len(result_list)  }, 200
        
        
        
#태그로 포스트 가저오기     
class PostingTagResource(Resource):

    @jwt_required()
    def get(self):

        Name = request.args.get('Name')
        offset = request.args.get('offset')
        limit = request.args.get('limit')


        try :
            connection = get_connection()
            query = f'''select p.id , u.id, u.nickName , p.imgurl, p.createdAt, p.content, count(lp.userId)as좋아요
                            from tagName tn
                            left join tag t
                            on tn.id = t.tagId
                            left join posting p
                            on p.id = postingId
                            left join user u 
                            on p.userId = u.id
                            left join likePosting lp
                            on lp.postingId = p.id
                            where tn.Name = %s
                            limit {limit} offset {offset};		'''
                        
            record = (Name,)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query,record )
            result_list = cursor.fetchall()
            print(result_list)

            i = 0
            for row in result_list:
                result_list[i]['createdAt'] = row['createdAt'].isoformat()
                i = i + 1


            cursor.close()
            connection.close()  

        except Error as e:
            print(e)
            cursor.close()
            connection.close()        
            return {'error' : "검색어 결과가 없습니다."} , 500
        
        return {'result' : 'success',
                'items' : result_list, 
                'count' : len(result_list)}, 200                    


# 내 좋아요 포스팅 리스트 가져오는 API
class MyLikePostingListResource(Resource):
    @jwt_required()
    def get(self):
        offset = request.args.get('offset')
        limit = request.args.get('limit')

        user_id = get_jwt_identity()
        try : 
            connection = get_connection()
            query = '''select  p.id as postingId,p.userId, u.nickName,p.content, p.imgurl, p.createdAt, p.updatedAt , count(l.postingId) as `like`, l.createdAt as likeTime
                    from posting p
                    join user u
                    on p.userId = u.id
                    left join likePosting l
                    on p.id = l.postingId
                    where l.userId = %s
                    group by l.postingId
                    order by likeTime desc
                    limit ''' + offset + ''', '''+ limit + ''';'''

            record = (user_id , )

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)

            result_list = cursor.fetchall()

            i = 0
            for row in result_list :
                result_list[i]['createdAt'] = row['createdAt'].isoformat()
                result_list[i]['updatedAt'] = row['updatedAt'].isoformat()
                result_list[i]['likeTime'] = row['likeTime'].isoformat()

                i = i + 1

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)} , 500


        return {'result' : 'success',
                'items' : result_list ,
                'count' : len(result_list)  }, 200

# 유저들이 작성한 포스팅 리스트 정렬해서 가져오는 API
# createdAt : 최신순으로 정렬,
# like : 좋아요순으로 정렬
class OrderListResource(Resource):
    @jwt_required()
    def get(self):
        order = request.args.get('order')
        offset = request.args.get('offset')
        limit = request.args.get('limit')

        user_id = get_jwt_identity()
        try : 
            connection = get_connection()
            query = '''select p.id, p.userId,p.content, p.imgurl, p.createdAt, p.updatedAt , count(l.postingId) as likeCnt
                    from posting p
                    left join likePosting l
                    on p.id = l.postingId
                    group by l.postingId
                    order by ''' + order + ''' desc
                    limit ''' + offset + ''', '''+ limit + ''';'''


            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, )

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
                'items' : result_list ,
                'count' : len(result_list)  }, 200


class LikeResource(Resource) :
    @jwt_required()
    def post(self, posting_id) :

        user_id = get_jwt_identity()

        try :
            connection = get_connection()
            query = '''insert into likePosting
                    (userId, postingId)
                    values
                    (%s, %s)'''

            record = (user_id, posting_id)
            
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


    @jwt_required()
    def delete(self, posting_id) :
        user_id = get_jwt_identity()

        try :
            connection = get_connection()
            query = '''delete from likePosting
                    where userId = %s and postingId = %s'''
            record = (user_id, posting_id)
            
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
    
    
    
    