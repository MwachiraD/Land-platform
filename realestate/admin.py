from django.contrib import admin
from .models import Buyer, Seller, Surveyor, Land


@admin.register(Land)
class LandAdmin(admin.ModelAdmin):
    list_display = ('id', 'location', 'size', 'price', 'latitude', 'longitude')
    list_filter = ('seller',)
    search_fields = ('location', 'seller__email')


admin.site.register(Buyer)
admin.site.register(Seller)
admin.site.register(Surveyor)