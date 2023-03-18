from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from config import Config
from resources.user import UserTargetEditResource,UserInfoEditResource,UserEmailUniqueResource,UserNicknameUniqueResource,UserRegisterResource, UserInfoResource, UserTargetResource, UserLoginResource, UserLogoutResource, UserNicknameResetResource
from resources.exercise import ExerciseKcalResource, ExerciseKeywordSearchResource, ExerciseSelectSearchResource, ExerciseKcalModifyDelete,ExerciseUserDirectResource, ExerciseUserDirectModifyResource, ExerciseDateKcalSum, ExerciseDateKcalList
from resources.user import jwt_blacklist
from resources.posting import LikeResource,MyLikePostingListResource,OrderListResource,PostingEditResource,PostingClickResource, MypostingListResource, PostingResource, PostingTagResource, LikeResource, MyLikePostingListResource, OrderListResource
from resources.diary import DiaryUserWeightResource, DiaryEdaResource, DiaryMonthListResource
from resources.exercise import ExerciseKcalResource, ExerciseKeywordSearchResource, ExerciseSelectSearchResource, ExerciseKcalModifyDelete,ExerciseUserDirectResource, ExerciseUserDirectModifyResource, ExerciseDateKcalSum, ExerciseDateKcalList
from resources.calorie import FoodRecordBreakfastResource, FoodRecordDinnerResource, FoodRecordEditResource, FoodRecordLunchResource, FoodRecordResource, FoodRecordTotalBreakfast, FoodRecordTotalDinnerResource, FoodRecordTotalLunchResource, FoodRecordUserResource, FoodResource, FoodSearchResource
from resources.calorie import FoodRecordTotalCarbsResource, FoodRecordTotalDayResource, FoodRecordTotalFatResource, FoodRecordTotalProteinResource
from resources.eda import DayEdaResource, WeekEdaResource, MonthEdaResource
from resources.positng_coment import PostingComentEditResource, PostingComentResource
# from resources.recommend import KmeansRecommendResource


app = Flask(__name__)
# 환경변수 셋팅
app.config.from_object(Config)

# JWT 매니저 초기화
jwt = JWTManager(app)

# 로그아웃된 토큰으로 요청하는 경우 처리하는 코드작성.
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload) :
    jti = jwt_payload['jti']
    return jti in jwt_blacklist


api = Api(app)

# 경로와 리소스(API코드)를 연결한다.

# 회원관리부분
api.add_resource(UserRegisterResource, '/user/register')
api.add_resource(UserTargetResource, '/user/target')
api.add_resource(UserLoginResource, '/user/login')
api.add_resource(UserLogoutResource, '/user/logout')
api.add_resource(UserEmailUniqueResource, '/user/email')
api.add_resource(UserNicknameUniqueResource, '/user/nickname')



# 유저 정보 수정
api.add_resource(UserNicknameResetResource, '/user/edit/nickname')
api.add_resource(UserTargetEditResource, '/user/edit/target')




## 포스팅 작성 부분 all수정
# 포스팅 작성
api.add_resource(PostingResource, '/posting')
# 내가 작성한 포스팅 리스트 가저오기
api.add_resource(MypostingListResource,'/posting/me')
#태그로 포스트 가저오기 
# 작성한 포스팅 수정 및 삭제
api.add_resource(PostingEditResource,'/posting/edit/<int:posting_id>')
# 포스팅 한개 클릭
api.add_resource(PostingClickResource,'/posting/<int:posting_id>')
api.add_resource(PostingTagResource,'/posting/tag')


api.add_resource(LikeResource, '/posting/<int:posting_id>/like')
api.add_resource(MyLikePostingListResource, '/posting/like/me')
api.add_resource(OrderListResource, '/posting/like/list')

#포스팅 댓글
api.add_resource(PostingComentResource,'/posting/coment/<int:posting_id>')
api.add_resource(PostingComentEditResource,'/posting/<int:posting_id>/coment/<int:comment_id>')



api.add_resource(ExerciseKcalResource, '/exercise')
api.add_resource(ExerciseKcalModifyDelete, '/exercise/<int:exerciseRecord_id>')
api.add_resource(ExerciseKeywordSearchResource, '/exercise/search')
api.add_resource(ExerciseSelectSearchResource, '/exercise/search/select/<int:exercise_id>')
api.add_resource(ExerciseUserDirectResource, '/exercise/user')
api.add_resource(ExerciseUserDirectModifyResource, '/exercise/user/<int:exerciseRecord_id>')
api.add_resource(ExerciseDateKcalSum, '/exercise/date')
api.add_resource(ExerciseDateKcalList, '/exercise/datelist')


#음식(칼로리)
api.add_resource(FoodSearchResource,'/food/search')
api.add_resource(FoodResource,'/food/<int:food_id>')
api.add_resource(FoodRecordResource,'/foodrecord')
api.add_resource(FoodRecordUserResource,'/foodrecord/user')
api.add_resource(FoodRecordEditResource,'/foodrecord/<int:record_id>')
api.add_resource(FoodRecordBreakfastResource,'/foodRecord/breakfast')
api.add_resource(FoodRecordLunchResource,'/foodRecord/lunch')
api.add_resource(FoodRecordDinnerResource,'/foodRecord/dinner')
api.add_resource(FoodRecordTotalBreakfast,'/foodRecord/total/breakfast')
api.add_resource(FoodRecordTotalLunchResource,'/foodRecord/total/lunch')
api.add_resource(FoodRecordTotalDinnerResource,'/foodRecord/total/dinner')

#11.홈화면 특정날짜 먹은 탄단지칼
api.add_resource(FoodRecordTotalCarbsResource, '/foodRecord/total/carbs')
api.add_resource(FoodRecordTotalProteinResource, '/foodRecord/total/protein')
api.add_resource(FoodRecordTotalFatResource, '/foodRecord/total/fat')
api.add_resource(FoodRecordTotalDayResource, '/foodRecord/total/kcal')

# 다이어리 부분
api.add_resource(DiaryEdaResource, '/diary/eda')
api.add_resource(DiaryUserWeightResource, '/diary')
api.add_resource(DiaryMonthListResource, '/diary/month')

# 도표부분
api.add_resource(DayEdaResource, '/eda/day')
api.add_resource(WeekEdaResource, '/eda/week')
api.add_resource(MonthEdaResource, '/eda/month')

# 추천 시스템
# api.add_resource(KmeansRecommendResource, '/recommend')







if __name__ == '__main__' :
    app.run()