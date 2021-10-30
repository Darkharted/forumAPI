from rest_framework import serializers
from .models import Comment, Favorite, Picture, Post, Rating
from likes import services as likes_services


class PictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Picture
        fields = ('image',)


class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.email')

    class Meta:
        model = Post
        fields = ('id', 'title', 'description', 'total_likes', 'author',)

    def create(self, validated_data):
        request = self.context.get('request')
        pictures_files = request.FILES
        post = Post.objects.create(
            author=request.user,
            **validated_data
        )
        for picture in pictures_files.getlist('pictures'):
            Picture.objects.create(
                image=picture,
                post=post
            )
        return post

    def update(self, instance, validated_data):
        request = self.context.get('request')
        for key, value in validated_data.items():
            setattr(instance, key, value)
        images_data = request.FILES
        instance.pictures.all().delete()
        for image in images_data.getlist('images'):
            Picture.objects.create(
                image=image,
                post=instance
            )
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['pictures'] = PictureSerializer(
            instance.pictures.all(), many=True
        ).data
        return representation

    def get_is_fan(self, obj):
        """
        Проверяет, лайкнул ли `request.user` продукт (`obj`).
        """
        user = self.context.get('request').user
        return likes_services.is_fan(obj, user)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.email')

    class Meta:
        model = Comment
        fields = '__all__'

    def create(self, validated_data):
        request = self.context.get('request')
        comment = Comment.objects.create(
            author=request.user,
            **validated_data
        )
        return comment


class RatingSerializer(serializers.ModelSerializer):
    post_title = serializers.SerializerMethodField("get_post_title")

    class Meta:
        model = Rating
        exclude = ('author',)

    def get_post_title(self, rating):
        title = rating.post.title
        return title

    def validate_rating(self, rating):
        if rating not in range(1, 6):
            raise serializers.ValidationError(
                "Рейтинг должен быть от 1 до 5"
            )
        return rating

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if not request.user.is_anonymous:
            representation['author'] = request.user.email

        return representation


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = instance.user.email
        representation['post'] = instance.post.title
        return representation
