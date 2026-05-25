from django.contrib import admin
from django import forms

from .models import Configuration


class ConfigurationAdminForm(forms.ModelForm):
    class Meta:
        model = Configuration
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.key == Configuration.ACTIVE_STORE_TYPE_KEY:
            self.fields["value"] = forms.ChoiceField(
                label="Active storefront",
                choices=Configuration.STORE_TYPE_CHOICES,
                help_text="Select the site customers see after refreshing the storefront.",
            )


@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    form = ConfigurationAdminForm
    list_display = ("key", "value", "description")
    search_fields = ("key",)
