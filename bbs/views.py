from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions
from django.contrib.auth import get_user_model
from django.urls import reverse
User = get_user_model()
from rest_framework.response import Response
from .models import Articles, Posts, ProfileAPI
from .serializers import CreateUserSerializer, UserSerializer, ArticlesSerializer, PostsSerializer, ProfileAPISerializer
from bbs.permissions import IsOwnerOrReadOnly
from rest_framework.decorators import api_view
from rest_framework import filters
from django_filters import rest_framework as rf_filters
from .filter import ArticlesFilters
from rest_framework import serializers

from django.forms.models import model_to_dict

class CreateUserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = CreateUserSerializer

    def create(self, request, *args, **kwargs):
        serializer = CreateUserSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

class ProfileAPIViewSet(viewsets.ModelViewSet):

    queryset = ProfileAPI.objects.all()
    serializer_class = ProfileAPISerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):

    url = serializers.HyperlinkedIdentityField(view_name="myapp:user-detail")
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def retrieve(self, request, pk=None):

        user = self.get_object()
        serializer = self.get_serializer(user)
        data = serializer.data

        user_notify = User.objects.get(pk=user.pk)
        
        new_dict= {}
        for obj in user_notify.notifications.unread():
            notify_dict = model_to_dict(obj, fields=["verb",])
            new_dict.setdefault("verb", []).append(notify_dict["verb"])
        
        return Response(dict(data, **new_dict))

class ArticleAPIViewSet(viewsets.ModelViewSet):

    queryset = Articles.objects.all()
    serializer_class = ArticlesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly]
    
    filter_backends = (rf_filters.DjangoFilterBackend, filters.SearchFilter,)

    filter_fields = ('content',)
    filter_class = ArticlesFilters
    search_fields = ['title', 'body']

    def perform_create(self, serializer):
        serializer.save(author_id=self.request.user)

class UserPostsAPIViewSet(viewsets.ModelViewSet):
    
    queryset = Posts.objects.all()
    serializer_class = PostsSerializer

    def retrieve(self, request, pk=None):

        postsall = self.get_object()
        serializer = self.get_serializer(postsall)
        return Response(serializer)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = serializer.data["user_id"]
        user = User.objects.get(pk=user_id)
        recipient_id = serializer.data["article_id"]
        recipient_user = Articles.objects.filter(id=recipient_id).values('author_id').first()['author_id']
        recipient = User.objects.get(pk=recipient_user)
        posts_content = serializer.data["content"]
        return Response(serializer.data)


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user_detail', request=request, format=format),
        'userapi': reverse('user_api', request=request, format=format),
        'articles': reverse('article_list', request=request, format=format),
        'posts': reverse('posts_list', request=request, format=format),
    })


