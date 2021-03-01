
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from bbs import views
from django.conf.urls import include
from rest_framework.documentation import include_docs_urls

router = DefaultRouter()
router.register(r'users', views.UserViewSet,  )
router.register(r'usersapi', views.CreateUserViewSet, 'user_api')
router.register(r'articles', views.ArticleAPIViewSet, 'articles_list')
router.register(r'posts', views.UserPostsAPIViewSet, 'posts_list')

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    path('docs',include_docs_urls(title='BBS')),
]
