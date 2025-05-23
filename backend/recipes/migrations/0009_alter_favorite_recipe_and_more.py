# Generated by Django 5.2.1 on 2025-05-23 19:13

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_alter_subscription_options_alter_subscription_author_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='favorite',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='measurement_unit',
            field=models.CharField(help_text='Введите единицу измерения', max_length=20, verbose_name='Единица измерения'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(help_text='Введите название ингредиента', max_length=256, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(help_text='Пользователь, создавший рецепт', on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveIntegerField(help_text='Введите время приготовления', validators=[django.core.validators.MinValueValidator(1)], verbose_name='Время приготовления (в минутах)'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(blank=True, help_text='Картинка рецепта', null=True, upload_to='recipes/', verbose_name='Изображение'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(help_text='Ингредиенты, входящие в состав', related_name='recipes', through='recipes.RecipeIngredient', to='recipes.ingredient', verbose_name='Ингредиенты'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='name',
            field=models.CharField(help_text='Название рецепта', max_length=256, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='text',
            field=models.TextField(help_text='Как приготовить рецепт', verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='shoppingcart',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe'),
        ),
    ]
