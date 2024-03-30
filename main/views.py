from django.shortcuts import get_object_or_404, render , redirect

from main.forms import ProductForm
from .models import Customer , Seller , Product , Category,Wishlist,Cart,Order
from django.contrib.auth import logout 
from django.contrib.auth.hashers import make_password , check_password
from django.utils import timezone
# Create your views here.

def home(request):
    categories = Category.objects.all()
    data = {
        "categories":categories
    }
    return render(request,'index.html',data)


def logoutpage(request):
    logout(request)
    request.session.flush()
    return redirect('login')

def signup(request):

    if request.method == 'POST':
        type  = request.POST.get('type')
        name = request.POST.get('name')
        email  = request.POST.get('email')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        existing_customer = None
        existing_seller = None
        if type == "Customer" : 
            existing_customer = Customer.objects.filter(email=email).first() 
        elif type == "Seller" :
            existing_seller = Seller.objects.filter(email=email).first() 

        data = {
            "error_message": "",
            "page" : "signup",
            "name" : name,
            "email" : email,
            "password" : password,
            "phone" : phone,
            "type" : type,
        }
        if existing_customer or existing_seller:
            data['error_message']= "User with the same email is already exist"
            return render(request,'login.html',data)
        if len(password) < 8:
            data["error_message"] = "Password should have at least 8 character"
            return render(request, 'login.html', data)
        if len(phone) != 10:
            data["error_message"] = "Phone number should be 10 digits"
            return render(request, 'login.html', data)
        
    
        
        if type == "Customer" :

            customer = Customer(name=name, email=email, phone=phone, password=password)
            customer.password = make_password(customer.password)
            customer.save()


        elif type == "Seller" :
            # company_name = request.POST.get('company_name')
            # data['company_name'] = company_name
            # seller = Seller(name=name, email=email, phone=phone, password=password,company_name="XYZ")
            # seller.password = make_password(seller.password)
            # seller.save()
            # data['page'] = "seller_auth"
            request.session['data'] = data 
            return redirect ('seller_auth')
            # return render(request,'company.html',data)
        

        data['page'] = "login"

    return render(request,'login.html')

def seller_auth(request):
    if request.method == 'POST':
        data = request.session.get('data')
        name = data['name']
        email  = data['email']
        password = data['password']
        phone = data['phone']
        company_name = request.POST.get('companyName')
        image = request.POST.get('companyProof')
        seller = Seller(name=name, email=email, phone=phone, password=password,company_name=company_name,proof_img=image)
        seller.password = make_password(seller.password)
        seller.save()
        request.session['id'] = seller.id
        products = Product.objects.filter(seller_id = seller.id )
        data = {
            "products":products
        }
        # request.session.pop('data', None)
        return render(request,'seller-home.html' , data)
     
    return render(request,'company.html')


def login(request):
    data = {
        "error_message": "",
        "page": "login",
        "name": "",
        "password": "",
    }
   
    if request.method == 'POST':
        type  = request.POST.get('type')
        name = request.POST.get('name')
        password = request.POST.get('password')
        flag = True
        customer = None
        seller = None
        try:
            if type == "Customer" :
                customer = Customer.objects.get(name=name)
            elif type == "Seller" :
                seller = Seller.objects.get(name=name)
        except:
            flag = False

        

        if customer and type == "Customer"  :
            flag = check_password(password,customer.password)
            if flag:
                # return render(request,'home.html')
                request.session['cust_id'] = customer.id
                return redirect('home')
            
        if seller and type == "Seller":
            flag = check_password(password,seller.password)
            if flag:
                request.session['id'] = seller.id
                products = Product.objects.filter(seller_id = seller.id )
                data = {
                    "products" : products
                }
                return redirect('seller_home')
            
        if type == "Admin":
            if name == 'admin' and password == 'admin':
                request.session['admin_id'] = 1

                return redirect('admin_home')

        
        data["error_message"] = "Invalid Username or Password"
        data["name"] = name
        data["password"] = password
    return render(request,'login.html',data)



def show_product(request, category_id):
    products = Product.objects.filter(category=category_id)
    category = get_object_or_404(Category, id=category_id)
    customer_id = request.session.get('cust_id')

    product_wishlist_info = {}

    if customer_id:
        wishlist_items = Wishlist.objects.filter(customer_id=customer_id)

        wishlist_product_ids = set(item.product.id for item in wishlist_items)

        for product in products:
            is_in_wishlist = product.id in wishlist_product_ids
            product_wishlist_info[product.id] = is_in_wishlist

    data = {
        "products": products,
        "category" : category ,
        "product_wishlist_info": product_wishlist_info
    }
    return render(request, 'products.html', data)



def show_single_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    category = product.category
    customer_id = request.session.get('cust_id')

    product_wishlist_info = {}

    # if customer_id:
        # wishlist_items = Wishlist.objects.filter(customer_id=customer_id)

        # wishlist_product_ids = set(item.product.id for item in wishlist_items)

        # for product in products:
        #     is_in_wishlist = product.id in wishlist_product_ids
        #     product_wishlist_info[product.id] = is_in_wishlist

    data = {
        "category" : category ,
        "product" : product ,
        # "product_wishlist_info": product_wishlist_info
    }
    return render(request, 'single-product.html', data)





def cart(request , product_id):
    product = get_object_or_404(Product, id=product_id)
    customer = get_object_or_404(Customer, id=request.session.get('cust_id'))
    cat=product.category
    cat_id=cat.id

    in_cart = Cart.objects.filter(product=product, customer=customer).exists()
    if not in_cart:
        new_cart = Cart(product=product, customer=customer)
        new_cart.quantity += 1 
        new_cart.save()

    products = Product.objects.filter(category=cat_id)
    data = {
        "products":products,
        "in_cart": in_cart
    }
    return render(request,'products.html',data )



def cart_view(request):

    cust_id = request.session.get('cust_id')
    customer = Customer(id = cust_id)
    products = Cart.objects.filter(customer = customer) 
    total_price = sum(item.product.price * item.quantity for item in products)
    data = { 
        
    }
   
    return render(request , 'cart.html' , {'products' : products , 'total_price' : total_price})



def remove_from_cart(request , product_id):

    cust_id = request.session.get('cust_id')
    customer = Customer(id = cust_id)
    product = Product(id = product_id)
    products = Cart.objects.filter(customer = customer , product = product)
    remaining_products = Cart.objects.filter(customer = customer)



    products.delete()
    cust_id = request.session.get('cust_id')
    customer = Customer(id = cust_id)
    products = Cart.objects.filter(customer = customer) 
    total_price = sum(item.product.price * item.quantity for item in products)
    return render(request , 'cart.html' , {'products' : remaining_products , 'total_price' : total_price})


def increase_quantity(request, product_id):
    cust_id = request.session.get('cust_id')
    product = get_object_or_404(Product, id = product_id)
    customer = get_object_or_404(Customer, id = cust_id)
    cart_item = get_object_or_404(Cart, product=product, customer = customer)
    cart_item.quantity += 1
    cart_item.save()
    print("incr")
    return redirect('cart_view')

def decrease_quantity(request, product_id):
    cust_id = request.session.get('cust_id')
    product = get_object_or_404(Product, id = product_id)
    customer = get_object_or_404(Customer, id = cust_id)
    cart_item = get_object_or_404(Cart, product=product, customer = customer)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    return redirect('cart_view')


def wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    customer = get_object_or_404(Customer, id=request.session.get('cust_id'))
    cat=product.category
    cat_id=cat.id

    in_wishlist = Wishlist.objects.filter(product=product, customer=customer).exists()
    if not in_wishlist:
        new_wishlist = Wishlist(product=product, customer=customer)
        new_wishlist.save()

    products = Product.objects.filter(category=cat_id)
    data = {
        "products":products,
        "in_wishlist": in_wishlist
    }
    return render(request,'products.html',data)


def wishlist_view(request):

    cust_id = request.session.get('cust_id')
    customer = Customer(id = cust_id)
    products = Wishlist.objects.filter(customer = customer) 
   
    return render(request , 'wishlist.html' , {'products' : products})



def remove_from_wishlist(request , product_id):

    cust_id = request.session.get('cust_id')
    customer = Customer(id = cust_id)
    product = Product(id = product_id)
    products = Wishlist.objects.filter(customer = customer , product = product)
    remaining_products = Wishlist.objects.filter(customer = customer)

    products.delete()
    return render(request , 'wishlist.html' , {'products' : remaining_products})






def buyProduct(request ):
    cust_id = request.session.get('cust_id')
    customer = get_object_or_404(Customer, id=cust_id)
    products = Cart.objects.filter(customer=customer) 

    data = { 
        "error_message": "",
        "products" : products , 
        "total_price" : ""
    }
    
    for cart_item in products:

        if cart_item.product.available != True:
            product = get_object_or_404(Product, id=cart_item.product.id)
            data['error_message'] = f"{product.name} is not available"
            return render(request, 'cart.html', data)
        elif cart_item.quantity > cart_item.product.stock:
            product = get_object_or_404(Product, id=cart_item.product.id)
            data['error_message'] = f"{product.name}'s quantity is more than available stock"
            return render(request, 'cart.html', data)
        
    
    total_price = sum(item.product.price * item.quantity for item in products)
    data['total_price'] = total_price 
    return render(request, 'payment.html' , data)  


def payment(request):

    cust_id = request.session.get('cust_id')
    customer = get_object_or_404(Customer, id=cust_id)
    products = Cart.objects.filter(customer=customer) 
    total_price = sum(item.product.price * item.quantity for item in products)
    date = timezone.now()

    for p in products:
        p.product.stock = p.product.stock -  p.quantity
        p.product.save()
        product = get_object_or_404(Product, id= p.product.id)
        address  = request.POST.get('address')
        new_order = Order(product = product , customer = customer , quantity = p.quantity ,date=date,address=address)
        new_order.save()
        p.delete()

    products = Order.objects.filter(customer=customer) 



    data = {
        "products" : products,

    }
    return render(request,'order.html', data)

def order_view(request):

    cust_id = request.session.get('cust_id')
    customer = get_object_or_404(Customer, id=cust_id)

    products = Order.objects.filter(customer=customer) 
    data = {
        "products" : products

    }
    return render(request,'order.html', data)



def seller_home(request):
    products = Product.objects.filter(seller_id = request.session.get('id') )
    data = {
            "products":products,
            "seller_id" : request.session.get('id') 
    }
    return render(request , 'seller-home.html' , data)


def add_product(request):
    if request.method == 'POST':
        # Retrieve form data
        name = request.POST.get('name')
        price = request.POST.get('price')
        description = request.POST.get('description')
        category_name = request.POST.get('category')
        stock = request.POST.get('stock')
        availability = request.POST.get('availability') == 'available'
        subcategory = request.POST.get('subcategory')
        image = request.FILES.get('image')
        

        seller_id = request.session.get('id')

        seller = Seller.objects.get(id = seller_id)
        category = Category.objects.get(name = category_name)
        # Create new Product instance
        new_product = Product(
            name=name,
            price=price,
            description=description,
            category= category,
            stock=stock,
            seller_id = seller , 
            available=availability,
            subcategory=subcategory,
            image=image
        )
        new_product.save()

        return redirect('seller_home')
    categories = Category.objects.all()
    data = {
        "categories":categories
    }
    return render(request, 'seller-addProduct.html' , data)


def update_product(request, product_id):

    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('seller_home')
    else:
        form = ProductForm(instance=product)
    return render(request, 'seller-updateProduct.html', {'form': form, 'product': product})



def delete_product(request , product_id):
   product = get_object_or_404(Product, id=product_id)
   product.delete()
   return redirect('seller_home') 







def admin_home(request):
    products = Product.objects.all()
    data = {
        "products":products    
    }
    return render(request , 'admin-home.html',data )




def category_ana(request):
    category = Category.objects.all()
    data = {
        "category":category    
    }
    return render(request , 'admin-addCategory.html' , data)


def user_ana(request):
    user = Customer.objects.all()
    data = {
        "user":user    
    }
    return render(request , 'admin-customer.html' , data)

def seller_ana(request):
    seller = Seller.objects.all()
    data = {
        "seller":seller
    }
    return render(request , 'admin-seller.html' , data)



def remove_product(request , product_id):
    product = get_object_or_404(Product, id= product_id)
    product.delete()

    products = Product.objects.all()
    data = {
        "products":products    
    }
    return render(request , 'admin-home.html' , data)

def remove_category(request , category_id):
    category = get_object_or_404(Category, id= category_id)
    category.delete()

    category = Category.objects.all()
    data = {
        "category":category    
    }
    return render(request , 'admin-addCategory.html' , data)

def remove_user(request , user_id):
    user = get_object_or_404(Customer, id= user_id)
    user.delete()
    users = Customer.objects.all()
    data = {
        "user":users   
    }
    return render(request , 'admin-customer.html' , data)

def remove_seller(request , seller_id):
    seller = get_object_or_404(Seller, id= seller_id)
    seller.delete()
    sellers = Seller.objects.all()
    data = {
        "seller":sellers   
    }
    return render(request , 'admin-seller.html' , data)

def add_category(request):
    if request.method == 'POST':
        # Retrieve form data
        name = request.POST.get('name')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        # Create new Product instance
        new_category = Category(
            name=name,
            description=description,
            photo=image
        )
        new_category.save()

        return render(request , 'admin-category.html')
    
    return render(request, 'admin-addCategory.html')








def profile_view(request):
    cust = request.session.get('cust_id')
    sell = request.session.get('id')

    data = {
        'user' : "" ,
        'type' : ""
    }
    if cust : 
        customer = get_object_or_404(Customer, id= cust)
        data['user'] = customer
        data['type'] = "Customer"

    elif sell :
        seller = get_object_or_404(Seller, id= sell)
        data['user'] = seller
        data['type'] = "Seller"

    return render(request , 'profile.html' , data)





