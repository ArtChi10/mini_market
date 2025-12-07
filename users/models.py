from django.db import models
from django.conf import settings
from decimal import Decimal
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("1000.00"))
    created_at = models.DateTimeField(auto_now_add=True)
    google_doc_url = models.URLField("Ссылка на документ", blank=True, default="")
    resume_example = models.URLField("Примеры резюме", blank=True, default="")
    resume_url = models.URLField("Моё резюме", blank=True, default="")
    task_url = models.URLField("Ссылка на задание", blank=True, default="")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    def __str__(self):
        return f"Profile({self.user.username})"

    @property
    def avatar_url(self):
        # вернёт путь к аватарке или дефолтную иконку из static
        if self.avatar:
            return self.avatar.url
        return "/static/img/avatar_default.png"  # положи такую картинку в static

    # лёгкое авто-сжатие (чтобы не грузили огромные фото при админ-загрузке)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.avatar:
            try:
                img = Image.open(self.avatar).convert("RGB")
                img.thumbnail((256, 256))
                buf = BytesIO()
                img.save(buf, format="JPEG", quality=85)
                self.avatar.save(f"{self.user.username}_avatar.jpg",
                                 ContentFile(buf.getvalue()), save=False)
                super().save(update_fields=["avatar"])
            except Exception:
                pass

