from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator
from posts.models import Comment, Follow, Group, Post, User


class PostSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Post.
    Включает автора поста по имени пользователя (username).
    """
    author = SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        fields = "__all__"
        model = Post


class CommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Comment.
    Включает автора комментария по имени пользователя (username).
    """
    author = serializers.SlugRelatedField(
        read_only=True, slug_field="username"
    )

    class Meta:
        fields = "__all__"
        model = Comment
        read_only_fields = ('post',)


class GroupSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Group.
    Включает все поля модели Group.
    """
    class Meta:
        model = Group
        fields = ("__all__")


class FollowSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Follow.
    Включает пользователя и пользователя, на которого подписываются.
    Проверяет, что пользователь не может подписываться на самого себя.
    Применяет валидатор, чтобы проверить, что пользователь не подписан уже на этого пользователя.
    """
    user = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field="username",
        default=serializers.CurrentUserDefault(),
    )
    following = serializers.SlugRelatedField(
        queryset=User.objects.all(), slug_field="username"
    )

    def validate_following(self, value):
        if value == self.context["request"].user:
            raise serializers.ValidationError("Подписка на себя не возможна")
        return value

    class Meta:
        model = Follow
        fields = "__all__"
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=["user", "following"],
                message="Вы уже подписаны на этого пользователя",
            )
        ]
