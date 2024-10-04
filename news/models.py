from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)



# news/models.py

class Category(models.Model):
    name = models.CharField(max_length=25, unique=True, verbose_name='Name of category')
    subscribers = models.ManyToManyField(User, related_name='categories', blank=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name



class Rating(models.Model):
    value = models.IntegerField(unique=True)  # Значение рейтинга от 1 до 5

    def __str__(self):
        return str(self.value)

# models.py

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    publication_date = models.DateField()
    author_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, default=9)
    article_type = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.ForeignKey(Rating, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_author = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


# models.py

