from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from .models import Snippet
from .serializers import SnippetSerializer, UserSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import Http404
from rest_framework import mixins
from rest_framework import generics
from rest_framework import viewsets
from django.contrib.auth.models import User
from rest_framework import permissions
from .permissions import IsOwnerOrReadOnly
from rest_framework.reverse import reverse
from rest_framework.decorators import action


# 总结：
# 一 view
# 1)不通过drf框架，只是加了序列化
# 2)ApiView，通过drf的Request，Response去处理
# 3)使用class view，增加复用性
# 3)GenericAPIView和mixin混合使用，引入了queryset 、serializer_class、lookup_field、pagination_class、filter_backend,
#    并提供了get_object，get_queryset方法
#    1 get_queryset(self)返回视图使用的查询集，是列表视图与详情视图获取数据的基础，默认返回queryset属性，可以重写
#    2 get_serializer_class(self)返回序列化器类，默认返回serializer_class，可以重写
#    3 get_object(self) 返回详情视图所需的模型类数据对象，默认使用lookup_field参数来过滤queryset
# 4)ListAPIView,其实就继承GenericAPIView加xxxMixin,重写了下get/post/put等方法,让你不用去写像get/post等这样的方法了，没干其它事了
# 5)ModelViewSet和ReadOnlyModelViewSet
#   1 ModelViewSet：继承自GenericAPIVIew,绑定方法发生了变化，同时包括了ListModelMixin、RetrieveModelMixin、
#     CreateModelMixin、UpdateModelMixin、DestoryModelMixin等
#   2 ReadOnlyModelViewSet：继承自GenericAPIVIew，同时包括了ListModelMixin、RetrieveModelMixin
# 二 登录权限
# 1)ListAPIView
# 2)ReadOnlyModelViewSet

# # 第四种方法的更加简洁的写法：ListCreateAPIView/RetrieveUpdateDestroyAPIView
# # 说明：
# # 在generics除了GenericAPIView还包括了其他几个View: CreateAPIView、ListAPIView、RetrieveAPIView、
# # ListCreateAPIView之类，因此也就有了第四种更加简洁的写法了
# class SnippetList(generics.ListCreateAPIView):
#     queryset = Snippet.objects.all()
#     serializer_class = SnippetSerializer
#     # permission_classes = (permissions.IsAuthenticatedOrReadOnly,)  # api权限控制
#     # api权限控制,先判断IsAuthenticatedOrReadOnly，再判断自定义的方法IsOwnerOrReadOnly
#     permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
#
#     # api权限控制,重写perform_create（作用：添加记录时带上创建者的用户id）
#     def perform_create(self, serializer):
#         serializer.save(owner=self.request.user)
#
#
# # 第四种方法的更加简洁的写法,ListCreateAPIView/RetrieveUpdateDestroyAPIView
# class SnippetDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Snippet.objects.all()
#     serializer_class = SnippetSerializer
#     # permission_classes = (permissions.IsAuthenticatedOrReadOnly,)  # api权限控制
#     permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)


# 第五种写法，利用viewset
class SnippetViewSet(viewsets.ModelViewSet):
    """
    list:
       GET url: /snippets/   分类列表数据
    create:
       POST url: /snippets/  创建分类详情
    retrieve:
       GET url: /snippets/1/  获取分类详情
    update:
       PUT url: /snippets/1/  修改分类详情
    delete:
       DELETE url: /snippets/1/  删除分类详情
    """
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)  # api权限控制

    # # 目前没有用到
    # @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    # def highlight(self, request, *args, **kwargs):
    #     snippet = self.get_object()
    #     return Response(snippet.highlighted)

    # 因为需要创建时，添加创建人，所以要重写下perform_create方法
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

# # api权限认证,方法一(利用genericsapiview)
# class UserList(generics.ListAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#
#
# # api权限认证,方法一(利用genericsapiview)
# class UserDetail(generics.RetrieveAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer


# api权限认证，方法二（利用viewsets）
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# 增加Api Root这个超链接，点击后展示所有的api（需要在urls.py中定义对应url的name,不然没法reverse）
# 说明：如果用了viewset，这个方法就不需要了，因为DefaultRouter class会给我们自动创建api root
# @api_view(['GET'])
# def api_root(request, format=None):
#     return Response({
#         'users': reverse('user-list', request=request, format=format),
#         'snippets': reverse('snippet-list', request=request, format=format)
#     })
# # 第四种方法,使用mixins
# 说明：
# 1)加入queryset属性，可以直接设置这个属性，不必再将实例化的courses，再次传给seriliazer,系统会自动检测到。除此之外，
# 可以重载get_queryset()，这样就不必设置'queryset=*'，这样就变得更加灵活，可以进行完全的自定义
# 2)加入serializer_class属性与实现get_serializer_class()方法。两者的存在一个即可，通过这个，在返回时，
# 不必去指定某个serilizer
# 3)设置过滤器模板：filter_backends、设置分页模板：pagination_class、加入 lookup_field="pk"
# class SnippetList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
#     queryset = Snippet.objects.all()
#     serializer_class = SnippetSerializer
#
#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)
#
#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)
#
#
# # 第四种方法,使用mixins
# class SnippetDetail(mixins.RetrieveModelMixin,mixins.UpdateModelMixin,
#                     mixins.DestroyModelMixin,generics.GenericAPIView):
#     queryset = Snippet.objects.all()
#     serializer_class = SnippetSerializer
#
#     def get(self, request, *args, **kwargs):
#         return self.retrieve(request, *args, **kwargs)
#
#     def put(self, request, *args, **kwargs):
#         return self.update(request, *args, **kwargs)
#
#     def delete(self, request, *args, **kwargs):
#         return self.destroy(request, *args, **kwargs)

# # 第三种方法，class based views(主要是让代码能够复用)
# # 说明：一般而言，如果要对不同的HTTP请求做出不同的相应的话，function-based views会在单一的函数中采用判断分支的方法
# # 而在class-based views中，你可以用不同的类实例的方法来响应不同的HTTP request
# class SnippetList(APIView):
#     def get(self, request, format=None):
#         snippets = Snippet.objects.all()
#         serializer = SnippetSerializer(snippets, many=True)
#         return Response(serializer.data)
#
#     def post(self, request, format=None):
#         serializer = SnippetSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# # 第三种方法，class based views(主要是让代码能够复用)
# class SnippetDetail(APIView):
#     def get_object(self, pk):
#         try:
#             return Snippet.objects.get(pk=pk)
#         except Snippet.DoesNotExist:
#             raise Http404
#
#     def get(self, request, pk, format=None):
#         snippet = self.get_object(pk)
#         serializer = SnippetSerializer(snippet)
#         return Response(serializer.data)
#
#     def put(self, request, pk, format=None):
#         snippet = self.get_object(pk)
#         serializer = SnippetSerializer(snippet, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
#
#     def delete(self, request, pk, format=None):
#         snippet = self.get_object(pk)
#         snippet.delete()
#         return Response(status.HTTP_204_NO_CONTENT)


# # 第二种方法(使用了request/response/status，必须加上@api_view装饰才可以用，因为@api_view是让请求经过rest框架处理)
# @api_view(['GET', 'POST'])
# def snippet_list(request, format=None):
#     if request.method == 'GET':
#             snippets = Snippet.objects.all()
#             serializer = SnippetSerializer(snippets, many=True)
#             return Response(serializer.data)
#     elif request.method == 'POST':
#             # data = JSONParser().parse(request)  # 使用这种方法不需要将请求的数据格式转换成可序列化的类型
#             serializer = SnippetSerializer(data=request.data)  # 直接将之前的data=data改成data=request.data即可被我们序列化
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# # 第二种方法(使用了request/response/status，必须加上@api_view装饰才可以用)
# @api_view(['GET', 'PUT', 'DELETE'])
# def snippet_detail(request, pk, format=None):
#     try:
#         snippet = Snippet.objects.get(pk=pk)
#     except Snippet.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
#
#     if request.method == 'GET':
#         serializer = SnippetSerializer(snippet)
#         return Response(serializer.data)
#
#     elif request.method == 'PUT':
#         # data = JSONParser().parse(request)
#         serializer = SnippetSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     elif request.method == 'DELETE':
#         snippet.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

# # 第一种方法(没有使用drf的requests/responses/@api_view/状态码)
# @csrf_exempt  # 加上这个的话，客户端请求就不需要进行token校验了
# def snippet_list(request):
#     if request.method == 'GET':
#         snippets = Snippet.objects.all()
#         serializer = SnippetSerializer(snippets, many=True)
#         return JsonResponse(serializer.data, safe=False)
#     elif request.method == 'POST':
#         data = JSONParser().parse(request)  # post的数据是json格式的，由于后续需要调用SnippetSerializer，因此必须要反序列化一下
#         serializer = SnippetSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return JsonResponse(serializer.data, status=201)
#         return JsonResponse(serializer.errors, status=400)
#
#
# # 第一种方法(没有使用drf的requests/responses/@api_view/状态码)
# @csrf_exempt
# def snippet_detail(request, pk):
#     try:
#         snippet = Snippet.objects.get(pk=pk)
#     except Snippet.DoesNotExist:
#         return HttpResponse(status=404)
#
#     if request.method == 'GET':
#         serializer = SnippetSerializer(snippet)
#         return JsonResponse(serializer.data)
#
#     elif request.method == 'PUT':
#         data = JSONParser().parse(request)
#         serializer = SnippetSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return JsonResponse(serializer.data)
#         return JsonResponse(serializer.errors, status=400)
#
#     elif request.method == 'DELETE':
#         snippet.delete()
#         return HttpResponse(status=204)
