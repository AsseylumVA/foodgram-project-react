from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    fields = ("username", "first_name", "last_name", "email")
    search_fields = ("username",)


admin.site.register(User, UserAdmin)
