from django.shortcuts import get_object_or_404
from posts.models import Group, Post
from rest_framework import filters, permissions, viewsets
from rest_framework.pagination import LimitOffsetPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (CommentSerializer, FollowSerializer, GroupSerializer,
                          PostSerializer)


class PostViewSet(viewsets.ModelViewSet):
    """
    Представление для работы с постами.
    Разрешает просмотр, создание, обновление и удаление постов.
    Авторизация требуется только для создания, обновления и удаления.
    Разрешение на запись доступно только автору поста.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly,
    )
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        """
        Выполняется при создании нового поста.
        Устанавливает автора поста в текущего пользователя.
        """
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """
    Представление для работы с комментариями.
    Разрешает просмотр, создание, обновление и удаление комментариев.
    Авторизация требуется только для создания, обновления и удаления.
    Разрешение на запись доступно только автору комментария.
    """
    serializer_class = CommentSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly,
    )

    def get_queryset(self):
        """
        Получает запрос комментариев для определенного поста.
        Использует идентификатор поста из URL-параметра.
        """
        post = get_object_or_404(Post, id=self.kwargs.get("post_id"))
        return post.comments.all()

    def perform_create(self, serializer):
        """
        Выполняется при создании нового комментария.
        Устанавливает автора комментария в текущего
        пользователя и связывает его с соответствующим постом.
        """
        post = get_object_or_404(Post, id=self.kwargs["post_id"])
        serializer.save(author=self.request.user, post=post)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Представление только для чтения групп.
    Разрешает только просмотр групп.
    Авторизация требуется только для просмотра.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly,
    )


class FollowViewSet(viewsets.ModelViewSet):
    """
    Представление для работы с подписками .
    Разрешает просмотр, создание, обновление и удаление подписок.
    Требуется аутентификация пользователя.
    Поддерживает фильтрацию по имени
    пользователей, на которых подписан пользователь.
    """
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("following__username",)

    def get_queryset(self):
        """Получает запрос подписок для текущего пользователя."""
        user = self.request.user
        new_queryset = user.followers.all()
        return new_queryset

    def perform_create(self, serializer):
        """
        Выполняется при создании новой подписки.
        Устанавливает пользователя в текущего пользователя.
        """
        serializer.save(user=self.request.user)
