from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views.generic import TemplateView, View, CreateView, FormView, DetailView, ListView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *
from .forms import CheckoutForm, CustomerRegistrationForm, CustomerLoginForm, AdminLoginForm, ProductForm
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash, get_user_model
from django.db.models import Q
from django.db.models.query_utils import Q
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import Paginator
from django.urls import reverse
from decimal import Decimal
from paypal.standard.forms import PayPalPaymentsForm
import requests
from django.shortcuts import get_object_or_404, reverse
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm, PasswordResetForm
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.views.decorators.csrf import csrf_exempt
from PayTm import Checksum
from django.conf import settings
from .utils import send_forget_password_mail
from django.core.mail import send_mail, EmailMessage


# Create your views here.


class EcomMixin(object):
    # def get_context_data(self,**kwargs):
    #     context=super().get_context_data(**kwargs)
    def dispatch(self, request, *args, **kwargs):
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            if request.user.is_authenticated and request.user.customer:
                cart_obj.customer = request.user.customer
                cart_obj.save()
        return super().dispatch(request, *args, **kwargs)


class HomeView(EcomMixin, TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['myname'] = "Amarjeet"
        # context['product_list']=Product.objects.all().order_by('-id')
        all_products = Product.objects.all().order_by('id')
        paginator = Paginator(all_products, 8)
        page_number = self.request.GET.get('page')
        product_list = paginator.get_page(page_number)
        context['product_list'] = product_list

        return context


class AllProductView(EcomMixin, TemplateView):
    template_name = "allproducts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allcategories'] = Category.objects.all()

        return context


class ProductDetailView(EcomMixin, TemplateView):
    template_name = "productdetail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        url_slug = self.kwargs['slug']
        # print(url_slug,99999999999) #This is for checking slug value
        product = Product.objects.get(slug=url_slug)
        product.view_count += 1
        product.save()
        context['product'] = product
        return context


class AddToCartView(EcomMixin, TemplateView):
    template_name = "addtocart.html"

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        # print(user)
        if user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            # print("logged user")
            pass
        else:
            # print("not logged user")
            # return redirect('ecomapp:customerlogin')
            return redirect('/login/')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get product id from requested url
        product_id = self.kwargs['pro_id']
        # print(product_id,5465) #check pro_id

        # get product
        product_obj = Product.objects.get(id=product_id)

        # check if cart exists
        cart_id = self.request.session.get('cart_id', None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            # print("old cart")
            this_product_in_cart = cart_obj.cartproduct_set.filter(product=product_obj)

            # items already exists in cart
            if this_product_in_cart.exists():
                cartproduct = this_product_in_cart.last()
                cartproduct.quantity += 1
                cartproduct.subtotal += product_obj.selling_price
                cartproduct.save()
                cart_obj.total += product_obj.selling_price
                cart_obj.save()

            # New item addes in cart
            else:
                cartproduct = CartProduct.objects.create(cart=cart_obj, product=product_obj,
                                                         rate=product_obj.selling_price, quantity=1,
                                                         subtotal=product_obj.selling_price)
                cart_obj.total += product_obj.selling_price
                cart_obj.save()


        else:
            cart_obj = Cart.objects.create(total=0)
            self.request.session['cart_id'] = cart_obj.id
            # print("new cart")
            cartproduct = CartProduct.objects.create(cart=cart_obj, product=product_obj, rate=product_obj.selling_price,
                                                     quantity=1, subtotal=product_obj.selling_price)
            cart_obj.total += product_obj.selling_price
            cart_obj.save()

        # check if product already exists in car

        return context


class MyCartView(EcomMixin, TemplateView):
    template_name = "mycart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get('cart_id', None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = None
        context['cart'] = cart
        return context


class ManageCartView(EcomMixin, View):

    def get(self, request, *args, **kwargs):
        print("this is manage cart section")
        cp_id = self.kwargs['cp_id']
        action = request.GET.get('action')
        # print(cp_id,action) # check action and cp_id
        cp_obj = CartProduct.objects.get(id=cp_id)
        cart_obj = cp_obj.cart
        # cart_id=request.session.get("cart_id",None)
        # if cart_id:
        #     cart2 = Cart.objects.get(id=cart_id)
        #     if cart1 != cart2:
        #         return redirect("ecomapp:mycart")
        #
        # else:
        #     return redirect("ecomapp:mycart")
        if action == 'inc':
            cp_obj.quantity += 1
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()
            cart_obj.total += cp_obj.rate
            cart_obj.save()

        elif action == 'dec':
            cp_obj.quantity -= 1
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.save()
            if cp_obj.quantity == 0:
                cp_obj.delete()
        elif action == 'rmv':
            cart_obj.total -= cp_obj.subtotal
            cart_obj.save()
            cp_obj.delete()
        else:
            pass

        return redirect("ecomapp:mycart")


class EmptyCartView(EcomMixin, View):

    def get(self, request, *args, **kwargs):
        cart_id = request.session.get('cart_id', None)
        cart = Cart.objects.get(id=cart_id)
        cart.cartproduct_set.all().delete()
        cart.total = 0
        cart.save()

        return redirect('ecomapp:mycart')


class CheckOutView(EcomMixin, CreateView):
    template_name = 'checkout.html'
    form_class = CheckoutForm
    success_url = reverse_lazy('ecomapp:home')

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        # print(user)
        if user.is_authenticated and request.user.customer:
            # print("logged user")
            pass
        else:
            # print("not logged user")
            # return redirect('ecomapp:customerlogin')
            return redirect('/login/?next=/checkout/')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get('cart_id', None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
        else:
            cart_obj = None
        context['cart'] = cart_obj
        return context

    def form_valid(self, form):
        cart_id = self.request.session.get('cart_id')
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            form.instance.cart = cart_obj
            form.instance.subtotal = cart_obj.total
            form.instance.discount = 0
            form.instance.total = cart_obj.total
            form.instance.order_status = 'Ordered Received'
            del self.request.session['cart_id']
            pm = form.cleaned_data.get("payment_method")
            amount = cart_obj.total
            # print(amount)
            email = form.cleaned_data.get("email")
            # print(email)

            order = form.save()
            if pm == "Paytm":
                return redirect(reverse("ecomapp:paytm-payment") + "?o_id=" + str(order.id))
            elif pm == "Cash On Delivery":
                return redirect(reverse("ecomapp:cash-on-delivery") + "?o_id=" + str(order.id))

        else:
            return redirect('ecomapp:home')
        return super().form_valid(form)


# Payment Process
def process_payment(request, host=None):
    o_id = request.GET['o_id']
    print(o_id)
    order = Order.objects.get(id=o_id)
    # cart=order.cart
    # print(order.order_status,order.total)
    # paypal_dict = {
    #     'business': settings.PAYPAL_RECEIVER_EMAIL,
    #     'amount': order.total,
    #     'item_name': 'Rolex Watch',
    #     'invoice': order.id,
    #     'notify_url': 'http://{}{}'.format(host,
    #                                        reverse('ecomapp:paypal-ipn')),
    # }
    #
    # form = PayPalPaymentsForm(initial=paypal_dict)
    # return render(request, 'process_payment.html', {'form': form,'total':order.total})


def paytm_payment_process(request):
    # o_id = request.GET['o_id']
    o_id = request.GET.get('o_id')
    # print(o_id)
    order = Order.objects.get(id=o_id)
    email = order.email
    order_id='ORDER'+str(order.id)
    print(order_id,'Orderid with string')
    # cart=order.cart
    # print(order.order_status,order.total)
    # param_dict = {
    #     "order_id":order.id,
    #     "email":email
    # }
    # return render(request, 'paytm.html', {'param_dict': param_dict})
    # paytmParams = dict()

    param_dict = {

        'MID': 'GOODEA80339035627893',
        'ORDER_ID': order_id,
        'TXN_AMOUNT': str(order.total),
        'CUST_ID': email,
        'INDUSTRY_TYPE_ID': 'Retail',
        'WEBSITE': 'WEBSTAGING',
        'CHANNEL_ID': 'WEB',
        'CALLBACK_URL': 'http://127.0.0.1:8000/paytm_status/',

    }
    from PayTm import Checksum
    param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, 'Izjmn#M5#BMlBX2L')
    return render(request, 'paytm.html', {'param_dict': param_dict})

    # paytmParams["body"] = {
    #     "mid": "GOODEA80339035627893",
    #     "orderId": str(order.id),
    #     "amount": str(order.total),
    #     "businessType": "UPI_QR_CODE",
    #     "posId": "S12_123",
    #     # 'CALLBACK_URL': 'http://127.0.0.1:7000/callback/',
    #
    # }
    # # print(paytmParams)
    # from paytmchecksum import PaytmChecksum
    # MERCHANT_KEY = 'Izjmn#M5#BMlBX2L'
    # import json
    # checksum = PaytmChecksum.generateSignature(json.dumps(paytmParams["body"]), MERCHANT_KEY)
    #
    # paytmParams["head"] = {
    #     "clientId": "C11",
    #     "version": "v1",
    #     "signature": checksum
    # }
    # post_data = json.dumps(paytmParams)
    # url = "https://securegw-stage.paytm.in/paymentservices/qr/create"
    # response = requests.post(url, data=post_data, headers={"Content-type": "application/json"}).json()
    # import base64
    # import json
    # # resp=json.dumps(response)
    # # print(resp)
    # image = response['body']['image']
    # order_id = paytmParams['body']['orderId']
    # # print(image)
    # return render(request, 'paytm2.html', {'param_dict': post_data, 'res': response, 'img': image, 'o_id': order_id})


class PaytmStatus(APIView):
    def post(self, request):
        order_id = request.data.get('order_id')
        # order=Order.objects.get(id=order_id)
        print(order_id)

        import json
        # import checksum generation utility
        # You can get this utility from https://developer.paytm.com/docs/checksum/
        from paytmchecksum import PaytmChecksum

        # initialize a dictionary
        paytmParams = dict()

        # body parameters
        paytmParams["body"] = {

            # Find your MID in your Paytm Dashboard at https://dashboard.paytm.com/next/apikeys
            "mid": "GOODEA80339035627893",

            # Enter your order id which needs to be check status for
            "orderId": str(order_id),
        }

        # Generate checksum by parameters we have in body
        # Find your Merchant Key in your Paytm Dashboard at https://dashboard.paytm.com/next/apikeys
        MERCHANT_KEY = 'Izjmn#M5#BMlBX2L'

        checksum = PaytmChecksum.generateSignature(json.dumps(paytmParams["body"]), MERCHANT_KEY)

        # head parameters
        paytmParams["head"] = {

            # put generated checksum value here
            "signature": checksum
        }

        # prepare JSON string for request
        post_data = json.dumps(paytmParams)

        # for Staging
        url = "https://securegw-stage.paytm.in/v3/order/status"

        # for Production
        # url = "https://securegw.paytm.in/v3/order/status"

        response = requests.post(url, data=post_data, headers={"Content-type": "application/json"}).json()
        print(response['body']['resultInfo']['resultStatus'])
        return Response(response['body']['resultInfo']['resultStatus'], status=status.HTTP_200_OK)


# Esewa Payment API  using------

class CashOnDeliveryView(View):
    def get(self, request, *args, **kwargs):
        o_id = request.GET.get('o_id')
        # print("order_id",o_id)
        order = Order.objects.get(id=o_id)
        cart = Cart.objects.get(id=o_id)
        # print("cart -- ",cart.customer)
        cart_obj = CartProduct.objects.get(cart=cart.id)
        # print(cart_obj.product,"product")
        context = {
            "order": order,
            "email": order.email,
            "amount": order.total,
            "item": cart_obj.product,
            "quantity": cart_obj.quantity,
            "rate": cart_obj.rate,
            "cash_on_delivery": "Cash On Delivery",
            "store_address_string": "<b>Head Office - Delhi New Delhi</b><br>"
                                    "sgfbhsjfgbhjjgb",
            "billing_address_string": "<b>Deepak Dubey</b> <br>"
                                      "Sultanpur Delhi, Akabarpur<br>"
                                      "<b>Mobile</b> 8545789489",
            "shipping_address_string": "<b>Deepak Dubey</b> <br>"
                                       "Sultanpur Delhi, Akabarpur<br>"
                                       "<b>Mobile</b> 8545789489"
        }
        return render(request, 'cashondelivery.html', context)


# ----Paytm Payment --

@csrf_exempt
def paytmCallback(request):
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]
    MERCHANT_KEY = 'Izjmn#M5#BMlBX2L'  # goodearth
    # MERCHANT_KEY='Izjmn#M5#BMlBX2L' #other
    from PayTm import Checksum
    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)

    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
    return render(request, 'paymentstatus.html', {'response': response_dict})


# paytm DQR
@csrf_exempt
def callback(request):
    import requests
    import json
    # import checksum generation utility
    # You can get this utility from https://developer.paytm.com/docs/checksum/
    from paytmchecksum import PaytmChecksum
    o_id = request.GET.get('o_id')
    print(o_id)
    # initialize a dictionary
    paytmParams = dict()

    # body parameters
    paytmParams["body"] = {
        # Find your MID in your Paytm Dashboard at https://dashboard.paytm.com/next/apikeys
        "mid": "GOODEA80339035627893",
        # Enter your order id which needs to be check status for
        "orderId": str(o_id),
    }
    # Generate checksum by parameters we have in body
    # Find your Merchant Key in your Paytm Dashboard at https://dashboard.paytm.com/next/apikeys
    MERCHANT_KEY = 'Izjmn#M5#BMlBX2L'

    checksum = PaytmChecksum.generateSignature(json.dumps(paytmParams["body"]), MERCHANT_KEY)

    # head parameters
    paytmParams["head"] = {

        # put generated checksum value here
        "signature": checksum
    }
    # prepare JSON string for request
    post_data = json.dumps(paytmParams)
    # for Staging
    url = "https://securegw-stage.paytm.in/v3/order/status"
    # for Production
    # url = "https://securegw.paytm.in/v3/order/status"

    response = requests.post(url, data=post_data, headers={"Content-type": "application/json"}).json()
    print(response,"qrrrResponse")


class CustomerRegistrationView(CreateView):
    template_name = 'customerregistration.html'
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy('ecomapp:home')

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        email = form.cleaned_data.get('email')
        user = User.objects.create_user(username=username, password=password, email=email)
        form.instance.user = user
        login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get('next')
            return next_url
        else:
            return self.success_url


class CustomerLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('ecomapp:home')


class CustomerLoginView(FormView):
    template_name = 'customerlogin.html'
    form_class = CustomerLoginForm
    success_url = reverse_lazy('ecomapp:home')

    # form_valid method is a type of post method and is available in createview formview and updateview
    def form_valid(self, form):
        uname = form.cleaned_data.get('username')
        pword = form.cleaned_data['password']
        usr = authenticate(username=uname, password=pword)
        if usr is not None and usr.customer:
            login(self.request, usr)
        else:
            return render(self.request, self.template_name, {'form': self.form_class, 'error': 'Invalid Credentials'})

        return super().form_valid(form)

    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get('next')
            return next_url
        else:
            return self.success_url


class CustomerProfileView(TemplateView):
    template_name = 'customerprofile.html'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        # print(user)
        if user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            # print("logged user")
            pass
        else:
            # print("not logged user")
            # return redirect('ecomapp:customerlogin')
            return redirect('/login/?next=/profile/')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.request.user.customer
        context['customer'] = customer
        orders = Order.objects.filter(cart__customer=customer).order_by('-id')
        context['orders'] = orders
        return context


class CustomerOrderDetailView(DetailView):
    template_name = 'customerorderdetail.html'
    model = Order
    context_object_name = "order_obj"

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        # print(user)
        if user.is_authenticated and request.user.customer:
            # print("logged user")
            order_id = self.kwargs['pk']
            # print(order_id)
            order = Order.objects.get(id=order_id)
            if request.user.customer != order.cart.customer:
                return redirect('ecomapp:customerprofile')
        else:
            # print("not logged user")
            # return redirect('ecomapp:customerlogin')
            return redirect('/login/?next=/profile/')
        return super().dispatch(request, *args, **kwargs)


# #Search class
class SearchView(TemplateView):
    template_name = 'search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kw = self.request.GET.get('keyword')
        # print(kw,'.......')
        results = Product.objects.filter(Q(title__icontains=kw) | Q(return_policy__icontains=kw))
        # print(results)
        context['results'] = results
        return context


# change pass with old password

def user_change_pass(request):
    user = request.user
    # print(user)
    if user.is_authenticated:
        # print("logged user")
        if request.method == 'POST':
            current = request.POST['cpwd']
            new_pas = request.POST['npwd']
            # print(current,new_pas)
            user = User.objects.get(id=request.user.id)
            # print(user)
            check = user.check_password(current)
            # print(check)
            if check == True:
                user.set_password(new_pas)
                user.save()
                login(request, user)
                messages.success(request, "Your password changed successfully !")
                return redirect('/profile/')
            else:
                messages.success(request, "Your Current Password Not Match- plz try again!!")
                return HttpResponseRedirect('/change-password/')
    else:
        # print("not logged user")
        # return redirect('ecomapp:customerlogin')
        return redirect('/login/')
    return render(request, 'changepassword.html')

    # use a PsswordForm then change pass

    # if request.method=='POST':
    #     form=PasswordChangeForm(user=request.user,data=request.POST)
    #     print(form)
    #     if form.is_valid():
    #         form.save()
    #         update_session_auth_hash(request,form.user)
    #         messages.success(request, "Your Password has been changed Successfully!!")
    #         return HttpResponseRedirect('/profile/')
    #     else:
    #         messages.success(request, "Your Password not changed plz try again!!")
    #         return HttpResponseRedirect('/change-password/')
    # else:
    #         # return redirect('/change-password/')
    #     form=PasswordChangeForm(user=request.user)
    # return render(request,'changepassword.html',{'form':form})


# Password change without old password entered
def user_change_pass2(request):
    user = request.user
    if user.is_authenticated:
        if request.method == 'POST':
            form = SetPasswordForm(user=request.user, data=request.POST)
            # print(form)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.user)
                messages.success(request, "Your Password has been changed Successfully!!")
                return HttpResponseRedirect('/profile/')
            else:
                messages.success(request, "Your Password not changed plz try again!!")
                return HttpResponseRedirect('/change-password2/')
    else:
        return redirect('/login/')
        # return redirect('/change-password/')
    form = SetPasswordForm(user=request.user)
    return render(request, 'changepassword2.html', {'form': form})


def forgot_pass(request):
    context = {}
    if request.method == 'POST':
        un = request.POST['username']
        pwd = request.POST['npass']
        # print(un,pwd)
        user = get_object_or_404(User, username=un)
        user.set_password(pwd)
        user.save()
        context['status'] = "Password Change Successfully"
        return redirect('/login/')

    return render(request, 'forgotpassword.html', context)


import random


# from cryptography.fernet import Fernet

def reset_password(request):
    # print("data = ",request.GET)
    un = request.GET['username']
    # print(un)
    try:
        user = get_object_or_404(User, username=un)
        # print(user.password)
        # return HttpResponse(user.email)

        otp = random.randint(1000, 9999)

        msg = "Dear {} \n {} is your One Time Password (OTP) \n Do not share it with others\n Thanks & Regards \nMysite".format(
            user.username, otp)
        try:
            email = EmailMessage("Account Verification", msg, to=[user.email])
            email.send()
            return JsonResponse({"status": "sent", "email": user.email, "password": user.password, "re_otp": otp})
        except:
            return JsonResponse({"status": "error", "email": user.email})
    except:
        # return HttpResponse("User Not Found")
        return JsonResponse({"status": "failed"})


# Send Email
def sendemail(request):
    context = {}

    if request.method == 'POST':
        to_rec = request.POST['to'].split(",")
        sub = request.POST['sub']
        msg = request.POST['msg']
        # print(to_rec,msg,sub)
        try:
            em = EmailMessage(sub, msg, to=[to_rec, ])
            em.send()
            context['status'] = 'An Email Sent Successfully'
            context['cls'] = 'alert-success'
        except:
            context['status'] = 'An Email could not sent .Plz check Internet or some issue have!'
            context['cls'] = 'alert-danger'

    return render(request, 'sendemail.html', context)


from ecomapp.credentials import Password


class AboutView(EcomMixin, TemplateView):
    pas = Password()

    # print(pas.password)
    template_name = "about.html"


class ContactView(EcomMixin, TemplateView):
    template_name = "contactus.html"


# Admin page


class AdminLoginView(FormView):
    template_name = 'adminpages/adminlogin.html'
    form_class = AdminLoginForm
    success_url = reverse_lazy('ecomapp:adminhome')

    def form_valid(self, form):
        uname = form.cleaned_data.get('username')
        pword = form.cleaned_data['password']
        usr = authenticate(username=uname, password=pword)
        if usr is not None and Admin.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name, {'form': self.form_class, 'error': 'Invalid Credentials'})
        return super().form_valid(form)


class AdminRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Admin.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect('/admin-login/')
        return super().dispatch(request, *args, **kwargs)


class AdminHomeView(AdminRequiredMixin, TemplateView):
    template_name = 'adminpages/adminhome.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pendingorders'] = Order.objects.filter(order_status="Ordered Received").order_by('-id')

        return context


class AdminOrderDetailView(AdminRequiredMixin, DetailView):
    template_name = 'adminpages/adminorderdetail.html'
    model = Order
    context_object_name = "ord_obj"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allstatus'] = ORDER_STATUS
        return context


class AdminOrderListView(AdminRequiredMixin, ListView):
    template_name = 'adminpages/adminorderlist.html'
    queryset = Order.objects.all().order_by('-id')

    context_object_name = "allorders"


class AdminOrderStatusChangeView(AdminRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        order_id = self.kwargs['pk']
        order_obj = Order.objects.get(id=order_id)
        new_status = request.POST.get('status')
        order_obj.order_status = new_status
        order_obj.save()
        return redirect(reverse_lazy('ecomapp:adminorderdetail', kwargs={'pk': order_id}))


class AdminProductListView(AdminRequiredMixin, ListView):
    template_name = "adminpages/adminproductlist.html"
    queryset = Product.objects.all().order_by('-id')

    context_object_name = 'allproducts'


class AdminProductCreateView(AdminRequiredMixin, CreateView):
    template_name = "adminpages/adminproductcreate.html"
    form_class = ProductForm
    success_url = reverse_lazy('ecomapp:adminproductlist')

    def form_valid(self, form):
        p = form.save()
        images = self.request.FILES.getlist('more_image')
        for i in images:
            ProductImage.objects.create(product=p, image=i)
        return super().form_valid(form)
