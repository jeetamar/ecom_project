from django.urls import path,include
from .views import *
from ecomapp import views
# from .views import ChangePassword
app_name="ecomapp"

urlpatterns =[
    path('',HomeView.as_view(), name="home"),
    path('about/',AboutView.as_view(), name="about"),
    path('contact-us/',ContactView.as_view(), name="contact"),
    path('all-products/',AllProductView.as_view(), name="allproducts"),
    path('product/<slug:slug>/',ProductDetailView.as_view(), name="productdetail"),
    path('product<int:pro_id>/',AddToCartView.as_view(), name="addtocart"),
    path('my-cart/',MyCartView.as_view(), name="mycart"),
    path('manage-cart/<int:cp_id>/',ManageCartView.as_view(), name="managecart"),
    path('empty-cart/',EmptyCartView.as_view(), name="emptycart"),
    path('checkout/',CheckOutView.as_view(), name="checkout"),
    path('paytm_status/',views.paytmCallback, name="handlerequest"),
    path('callback/', views.callback, name='callback'),

    path('cash-on-delivery/',CashOnDeliveryView.as_view(), name="cash-on-delivery"), #Cash On Delivery




    path('register/',CustomerRegistrationView.as_view(), name="customerregistration"),
    path('logout/',CustomerLogoutView.as_view(), name="customerlogout"),
    path('login/',CustomerLoginView.as_view(), name="customerlogin"),
    path('profile/',CustomerProfileView.as_view(), name="customerprofile"),
    path('profile/order-<int:pk>/',CustomerOrderDetailView.as_view(), name="customerorderdetail"),
    path('search/',SearchView.as_view(), name="search"),
    path('change-password/',views.user_change_pass, name="changepassword"),
    path('change-password2/',views.user_change_pass2, name="changepassword2"),
    path('forgot_pass/',views.forgot_pass, name="forgot-password"),
    path('reset_password/',views.reset_password, name="reset_password"),
    path('sendemail/',views.sendemail, name="sendemail"),
    path('process_payment/',views.process_payment,name='process-payment'),
    path('paytm_payment/',views.paytm_payment_process,name='paytm-payment'),
    path('paytmqr_status/',PaytmStatus.as_view(),name='paytm-qr-status'),

    #admin-pages
    path('admin-login/',AdminLoginView.as_view(), name="adminlogin"),
    path('admin-home/',AdminHomeView.as_view(), name="adminhome"),
    path('admin-order/<int:pk>/',AdminOrderDetailView.as_view(), name="adminorderdetail"),
    path('admin-all-order/',AdminOrderListView.as_view(), name="adminorderlist"),
    path('admin-order/<int:pk>-change/',AdminOrderStatusChangeView.as_view(), name="adminorderstatuschange"),
    path('admin-product/list/',AdminProductListView.as_view(), name="adminproductlist"),
    path('admin-product/add/',AdminProductCreateView.as_view(), name="adminproductcreate"),
]