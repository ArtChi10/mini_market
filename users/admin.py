
from django.contrib import admin
from django.utils.html import format_html
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "balance", "avatar_preview", "google_doc_url")
    search_fields = ("user__username","user__last_name","user__first_name")
    readonly_fields = ("avatar_preview",)
    fields = ("user", "balance", "google_doc_url", "resume_url", "resume_example", "task_url", "avatar", "avatar_preview")

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" style="height:48px;width:48px;'
                               'object-fit:cover;border-radius:50%;">', obj.avatar.url)
        return "—"
    avatar_preview.short_description = "Превью"
