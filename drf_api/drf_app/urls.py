from django.conf.urls import url, include
from . import views
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter

# 对应views中的第一种/第二种方法
# urlpatterns = [
#     url(r'^snippets/$', views.snippet_list),
#     url(r'^snippets/(?P<pk>[0-9]+)/$', views.snippet_detail),
# ]

# 对应views中第三/四种方法
# 说明：django的URL解析器需要将request和相应的参数传递给一个可调用的函数，而不是一个类。所以class-based view提供一个类方法：
# as_view()来解决这个问题，as_view()方法让你可以把类当做函数来调用。as_view创建一个类实例，然后调用它的dispatch方法，
# dispatch分析出request是GET、POST或者其他，然后将request匹配给相应的函数，比如将POST请求匹配给post()函数，
# 如果给函数没有定义的话，将引发HttpResponseNotAllowed错误。
# urlpatterns = [
#     url(r'^snippets/$', views.SnippetList.as_view(), name='snippet-list'),
#     url(r'^snippets/(?P<pk>[0-9]+)/$', views.SnippetDetail.as_view()),
#     url(r'^users/$', views.UserList.as_view(), name='user-list'),  # api权限认证
#     url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view()),  # api权限认证
#     url(r'^$', views.api_root, name='api_index'),
# ]
# 方法二
# 说明：register(prefix, viewset, base_name)  ---prefix 该视图集的路由前缀\viewset 视图集\base_name 路由名称的前缀
# 如果views中包含action的话，那就会生成类似的链接^snippets/action的方法名/$
router = DefaultRouter()
router.register(r'snippets', views.SnippetViewSet)
router.register(r'users', views.UserViewSet)
urlpatterns = [
    url(r'^', include(router.urls))
]


# urlpatterns = format_suffix_patterns(urlpatterns)  # 请求过来时，参数可能会使用很多格式，这里我们这里需要交给drf处理下
