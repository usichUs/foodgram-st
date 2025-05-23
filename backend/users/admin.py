from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from recipes.models import Subscription
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'id',
        'username',
        'full_name',
        'email',
        'avatar_tag',
        'recipe_count',
        'subscriptions_count',
        'subscribers_count',
    )
    list_display_links = ('username', 'email')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    ordering = ('username',)

    @admin.display(description=_('ФИО'))
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    @admin.display(description=_('Аватар'))
    @mark_safe
    def avatar_tag(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" width="40" height="40" style="border-radius:50%;" />', obj.avatar.url)
        return "—"

    @admin.display(description=_('Рецептов'))
    def recipe_count(self, obj):
        return obj.recipes.count()

    @admin.display(description=_('Подписок'))
    def subscriptions_count(self, obj):
        return Subscription.objects.filter(user=obj).count()

    @admin.display(description=_('Подписчиков'))
    def subscribers_count(self, obj):
        return Subscription.objects.filter(author=obj).count()

    fieldsets = (
        (None, {
            'fields': ('email', 'username', 'password')
        }),
        (_('Персональная информация'), {
            'fields': ('first_name', 'last_name', 'avatar')
        }),
        (_('Права доступа'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Даты'), {
            'fields': ('last_login', 'date_joined')
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )
