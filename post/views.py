from typing import Generic
from django.shortcuts import render
from django.views import generic
from rest_framework import serializers, viewsets, generics
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import filters as rest_filters
from django_filters import rest_framework as filters
from rest_framework.permissions import IsAuthenticated
from likes.mixins import LikedMixin
from post.permissions import IsAuthorPermission
from .serializers import CommentSerializer, FavoriteSerializer, PostSerializer, RatingSerializer
from rest_framework.response import Response
from .models import Comment, Favorite, Post, Rating
from rest_framework import status
from rest_framework.decorators import action
from django.http import HttpResponse


class PermissionMixin:

    def get_permission(self):
        if self.action == 'create':
            permissions = [IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permissions = [IsAuthorPermission, ]
        else:
            permissions = []
        return [permission() for permission in permissions]


class PostViewset(LikedMixin, PermissionMixin, ModelViewSet):
    queryset = Post.objects.all().select_related("author")
    serializer_class = PostSerializer
    queryset_any = Favorite.objects.all()

    filter_backends = [
        filters.DjangoFilterBackend,
        rest_filters.SearchFilter
    ]
    filter_fields = ['title', ]
    search_fields = ['title', 'id']

    @action(detail=False, methods=['get'])
    def favorites(self, request):
        queryset = Favorite.objects.all()
        queryset = queryset.filter(user=request.user)
        serializer = FavoriteSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_favorites(self, request, pk=None):
        post = self.get_object()
        obj, created = Favorite.objects.get_or_create(user=request.user, post=post, )
        if not created:
            obj.favorite = not obj.favorite
            obj.save()
        favorites = 'added to favorites' if obj.favorite else 'removed to favorites'

        return Response('Successfully {} !'.format(favorites), status=status.HTTP_200_OK)

    def get_serializer_context(self):
        return {'request': self.request, 'action': self.action}


class CommentViewset(PermissionMixin, ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class RatingViewset(PermissionMixin, viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

    def get_serializer_context(self):
        return {
            'request': self.request
        }

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)
