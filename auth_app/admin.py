from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django import forms

# Change admin title, header, and index title
admin.site.site_header = "By Faith School Admins' Dashboard."
admin.site.site_title = "ByFaith Admin Portal"
admin.site.index_title = "Welcome Admins!"


class SafeUserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = "__all__"

    def clean_is_superuser(self):
        is_superuser = self.cleaned_data.get("is_superuser")
        if not self.instance.pk:  # Creating a new user
            if is_superuser and not self.current_user.is_superuser:
                raise forms.ValidationError("You are not allowed to create superusers.")
        else:  # Editing an existing user
            if self.instance.is_superuser and not self.current_user.is_superuser:
                return True  # Don't allow downgrading a superuser
            if is_superuser and not self.current_user.is_superuser:
                raise forms.ValidationError("Only superusers can promote others to superuser.")
        return is_superuser

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)

class CustomUserAdmin(UserAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        class WrappedForm(SafeUserChangeForm, form):
            pass
        return WrappedForm if obj else SafeUserChangeForm

    def get_form_kwargs(self, request, obj=None, **kwargs):
        kwargs = super().get_form_kwargs(request, obj, **kwargs)
        kwargs['current_user'] = request.user
        return kwargs

    def has_change_permission(self, request, obj=None):
        if obj and obj.is_superuser and not request.user.is_superuser:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_superuser and not request.user.is_superuser:
            return False
        return super().has_delete_permission(request, obj)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
