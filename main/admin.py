from django.contrib import admin
from .models import Category,Product,Customer,Seller,Wishlist,Cart,Order

# Register your models here.
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(Seller)
admin.site.register(Wishlist)
admin.site.register(Cart)
admin.site.register(Order)

