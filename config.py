# 노출이 되면 안되는 정보들은 config 파일에 변수로 저장을 한다.
class Config :
    # AWS RDS 주소를 넣어준다
    HOST = 'yhdb.cph4at3bysok.ap-northeast-2.rds.amazonaws.com'
    # database 이름을 넣어준다
    DATABASE = 'diet_db'
    # 설정한 user 이름을 넣어준다
    DB_USER = 'diet_db_user'
    # 설정한 패스워드를 넣어준다.
    DB_PASSWORD = 'dt1234'

    SALT = 'dskj29jkdsld'

    # JWT 관련 변수 셋팅
    JWT_SECRET_KEY = 'cocopig20230105##hello'
    JWT_ACCESS_TOKEN_EXPIRES = False
    PROPAGATE_EXCEPTIONS = True
    
    
    # AWS 관련 변수 셋팅
    ACCESS_KEY = 'AKIARGFHINKNFNCRQL6E'
    SECRET_ACCESS = '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'
    
    # S3 관련 변수 셋팅
    S3_BUCKET= 'diet-health-app'
    # S3 Location
    S3_LOCATION = 'http://{}.s3.ap-northeast-2.amazonaws.com/'.format(S3_BUCKET)
    
    # naver 파파고
    NAVER_CLIENT_ID = 'SsXlK1CajeNgadOJrYsm'
    NAVER_CLIENT_SECRET = 'cta8DxGeJh'
    NAVER_PAPAGO_URL = 'https://openapi.naver.com/v1/papago/n2mt'
    
    