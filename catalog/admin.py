from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, PriceHistory

# ---- Category ----
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    list_display = ("name",)
    ordering = ("name",)

# ---- Actions ----
@admin.action(description="Одобрить выбранные товары")
def approve_products(modeladmin, request, queryset):
    queryset.update(is_approved=True)

@admin.action(description="Утвердить и присвоить pending_owner")
def approve_and_assign(modeladmin, request, queryset):
    for obj in queryset.select_related("pending_owner"):
        if obj.pending_owner:
            obj.created_by = obj.pending_owner
            obj.pending_owner = None
            obj.is_approved = True
            obj.save(update_fields=["created_by", "pending_owner", "is_approved"])

@admin.action(description="Отклонить изменения (снять с модерации)")
def reject_changes(modeladmin, request, queryset):
    for obj in queryset:
        obj.pending_owner = None
        obj.is_approved = False
        obj.save(update_fields=["pending_owner", "is_approved"])

# ---- Product ----
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "title", "category", "price", "stock",
        "is_approved", "created_by", "pending_owner",
        "updated_at", "thumb",
    )
    list_filter = ("is_approved", "category")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}  # убери, если slug генерируешь иначе
    list_select_related = ("category", "created_by", "pending_owner")
    autocomplete_fields = ("category", "created_by", "pending_owner")
    actions = [approve_products, approve_and_assign, reject_changes]
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (None, {
            "fields": ("title", "slug", "category", "price", "stock", "image")
        }),
        ("Контент", {
            "fields": ("description", "ascii_art"),
            "classes": ("collapse",),
        }),
        ("Модерация", {
            "fields": ("is_approved", "created_by", "pending_owner"),
        }),
        ("Служебные поля", {
            "fields": ("min_price", "max_price", "next_change_at", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def thumb(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:40px;width:40px;object-fit:cover;border-radius:6px;">',
                obj.image.url,
            )
        return "—"
    thumb.short_description = "Фото"

# ---- PriceHistory ----
@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ("product", "old_price", "new_price", "changed_at", "reason")
    list_filter = ("product", "reason")
    date_hierarchy = "changed_at"
    search_fields = ("product__title",)
    list_select_related = ("product",)
