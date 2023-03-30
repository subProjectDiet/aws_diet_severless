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
    
    #구글 비전 api
    credentials = {
  "type": "service_account",
  "project_id": "dietvisionapp",
  "private_key_id": "eb23cb7e9292316cc80ee62d472b2b90bea32da1",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCtI131/ImE0s5h\nI8uBogKs/NOBMgedHLeqQTVy0+2trxQ6ybGEWOMbIPkVIkrYeZXCRWWJbRRpzve3\nOXrExAhhgIE2sK1GMex8L+rxtwDNxwuXxBDELANv6ouKB4yb3RPxuFFMoNtZainK\nR6IDxu9Vvz0fBDNWd77sRYAo+faxvKC7KEY9aJRrbTAZgPOAJATF7H3iAmIsgRf4\nvDOeB2UAbyQccCGtGsVus/Dbo8T2ffiJLfjahxX/uqyHPq4Y7ZfagQZhTEsIHFlh\nfGyq/265Z8JpsZ+0aQtjQKe9VFzceL3NCAKmiDyYwUyJs3uHYkGvjd0XtgvLHp4v\nUngw9ADhAgMBAAECggEAGpHhite6cuZhmDQEuFwYdQZHnv1X1cXhGaua0YhcYoRf\nt7XZcX9X5YM7NlcQ4q+l9S5D1Wx77tDoNaIIiRxcUjovmij62QQy+naQDjq7UNj0\nRSdoO0gAhF2babnxhhR4nxEIyO2r5nONqOaH98nA/jO0OYeiKT7ZzysgmSk4W9te\nr5qAx5VBhu6aAz++HLjuZEVMti7RzNNoWqKmk5GNs9HMQcT5JwWu1zVupnCppgTE\n2gOkL1nf3htcxV38C/KuUtGDYfEYkqn9Qk8fs/iHt4rydEJG2tZ90FIWGZ4Lu8QH\njfb8/GIuF9pcvfy17VD/Qm5OP/ADdVs3kFAGUF6r0QKBgQDzt8SDc8CkI/VLjnPH\nYPRux4A3gzMpWs1RxvQ2Xzgusn1SVBt1AH7iFFCNftd3IFEOgwejHB1Fb1U8kYjr\nbSIuF8Azsj6QDSJ5UKd1HC6ZB2JIW6T8h1UYdKpFxJlC7n12AcrjdnEGLH7rMgUh\nelRJtXMTh2IClGIFDgLOr8rBtwKBgQC13QrmRLvmd1GV9jgjWpGxAy6mqvIt5l/H\nmhD+nUH16/E05QuqbzWd/lbiotTJVuCmCq9bif5RDn+Qlx7VL7aEVKBJnnq2Ksxm\nN9FaLEkfIxJJ6n80CEEJdq8yvIUSAnySCPn71vRuIev9sH7oVqlB+l7Ihb/oobYg\nWqTq05tyJwKBgAW88uSBaiyzKAhSX0l3b+nXyp4D+cVkfOcK/x70mPcIfsjccBUO\nIO6juc3LCbmlSiNEVH6zn8DNwTz+1DFuzVo2dvEAplZv6LrgekDYnARAV0EK31SO\nvyMnRAcGfPFFejC4FBXM6RZTH93bvKEwJyHhIsd37YfQBIrH7Kr/Go/7AoGBAKeL\nadQ0dIthV6d5e8SOVvSmAt+HU7AXshu4g3metTrz0HczoKi25cWVoMQQ0UpgIHy4\nEU+a9NIGMl2p67zpxRNqx3SrbU/QZBizycpyTDdEXz/7qo7sH8axMbzjUxEBe3Qq\nkuuB4BRqafiBFpnD5REksRe5qNCP0rNB7vdsVaQ3AoGBAJFB3Wvf7Ugfb5MifoS2\nvJcPdVTUwQuVQaIPXWZ4pSk8FNpR+rW/RIRUUbmjDPJUQw75EMrT6dn23NAx/g50\nxRScPCAWqQfhz1P39weQ0SQ3ThsYgnyQJgAJZAIKZldE+mORP6zEssrYGPS9e3Hf\nmKb05UgUD58mm4AlmtFvc/Kt\n-----END PRIVATE KEY-----\n",
  "client_email": "dietvisionapp@dietvisionapp.iam.gserviceaccount.com",
  "client_id": "106168636917089929237",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/dietvisionapp%40dietvisionapp.iam.gserviceaccount.com"
}
    

    
    