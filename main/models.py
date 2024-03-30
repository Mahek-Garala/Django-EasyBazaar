from django.db import models
# Create your models here.

class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length= 50)
    phone = models.CharField(max_length = 10)
    email = models.EmailField(unique = True)
    password = models.CharField(max_length = 50) 
    def __str__(self):
        return self.name
    
class Seller(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=10)
    email = models.EmailField()
    password = models.CharField(max_length=500)
    company_name = models.CharField(max_length=255,null=True)
    proof_img = models.ImageField(upload_to='uploads/Seller/',null=True)

    def __str__(self):
        return self.name




class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    photo = models.ImageField(upload_to='uploads/categories')
    description = models.TextField(max_length=200, default='', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'



class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)    
    description = models.TextField(max_length=200, default='', null=True, blank=True)
    image = models.ImageField(upload_to='uploads/products/')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    seller_id = models.ForeignKey(Seller, on_delete=models.CASCADE, default=1)
    stock = models.IntegerField()
    available = models.BooleanField(default=True)
    subcategory = models.CharField(max_length=50,null=True,blank=True)

    def __str__(self):
        return self.name
    


class Wishlist(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, default=1)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return f"Wishlist-{self.id}"


class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, default=1)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, default=1)
    quantity = models.PositiveIntegerField(default=0)
    def __str__(self):
         return f"-{self.customer.name}-{self.product.name}"




# class CartItem(models.Model):
#     cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField()

#     def total_price(self):
#         return self.quantity * self.product.price
    



class Order(models.Model):
     
    order_id = models.AutoField(primary_key= True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, default=1)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, default=1)
    quantity = models.IntegerField(default = 0)
    date = models.DateField()
    address = models.CharField(max_length=200, null=False,default="")

    def __str__(self):
         return f"-{self.order_id}{self.customer.name}-{self.product.name}"


    
# class ShippingAddress(models.Model):
#     customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
#     order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
#     address = models.CharField(max_length=200, null=False)
#     city = models.CharField(max_length=200, null=False)
#     state = models.CharField(max_length=200, null=False)
#     zipcode = models.CharField(max_length=200, null=False)
#     date_added = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         verbose_name_plural = 'ShippingAddresses'

#     def __str__(self):
#         return self.customer.name


