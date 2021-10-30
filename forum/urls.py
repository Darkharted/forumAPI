from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from post.views import CommentViewset, PostViewset, RatingViewset
from .yasg import urlpatterns as doc_urls

router = DefaultRouter()

router.register('post', PostViewset)
router.register('comments', CommentViewset)
router.register('rating', RatingViewset)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v2/', include(router.urls)),
    path('api/v2/', include('account.urls')),
    path('chat/', include('chat.urls')),

]

urlpatterns += doc_urls
