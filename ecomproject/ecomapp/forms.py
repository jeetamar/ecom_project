from django import forms
from .models import Order,Customer,Product
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm,PasswordResetForm
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox




CHOICES=(
    ("Cash On Delivery","Cash On Delivery"),
    ("Khalti","Khalti")
)

class  CheckoutForm(forms.ModelForm):
    ordered_by = forms.CharField(label='Ordered By', widget=forms.TextInput(attrs={'class': 'form-control'}))
    shipping_address = forms.CharField(label='Shipping Address', widget=forms.TextInput(attrs={'class': 'form-control'}))
    mobile = forms.CharField(label='Mobile', widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.CharField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    # payment_method = forms.ChoiceField(label='Payment Method',choices=CHOICES, widget=forms.ChoiceField(attrs={'class': 'form-control'}))
    class Meta:
        model= Order
        fields=['ordered_by','shipping_address','mobile','email','payment_method']


class CustomerRegistrationForm(forms.ModelForm):
    username=forms.CharField(label='Username',widget=forms.TextInput(attrs={'class':'form-control'}))
    password=forms.CharField(label='Password',widget=forms.PasswordInput(attrs={'class':'form-control'}))
    email=forms.CharField(label='Email',widget=forms.EmailInput(attrs={'class':'form-control'}))
    full_name=forms.CharField(label='Full Name',widget=forms.TextInput(attrs={'class':'form-control'}))
    address=forms.CharField(label='Address',widget=forms.Textarea(attrs={'class':'form-control','rows':3, 'cols':5}))

    class Meta:
        model=Customer
        fields=['username','password','email','full_name','address']

    def clean_username(self):
        uname=self.cleaned_data.get('username')
        if User.objects.filter(username=uname).exists():
            raise forms.ValidationError('Customer with this username already exists')

        return uname


class CustomerLoginForm(forms.Form):
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))





# Admin form

class AdminLoginForm(forms.Form):
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class ProductForm(forms.ModelForm):
    more_image=forms.FileField(required=False,widget=forms.FileInput(attrs={"class":"form-control","multiple":True}))
    class Meta:
        model=Product
        fields=['title','slug','category','image','marked_price','selling_price','description','warranty','return_policy']


        widgets ={
            "title":forms.TextInput(attrs={"class":"form-control","placeholder":"Enter The Product title.."}),
            "slug":forms.TextInput(attrs={"class":"form-control","placeholder":"Enter The unique Slug.."}),
            "category":forms.Select(attrs={"class":"form-control"}),
            "image":forms.ClearableFileInput(attrs={"class":"form-control"}),
            "marked_price":forms.NumberInput(attrs={"class":"form-control","Placeholder":"Enter Marked Price"}),
            "selling_price":forms.NumberInput(attrs={"class":"form-control","Placeholder":"Enter Selling Price"}),
            "description":forms.Textarea(attrs={"class":"form-control","Placeholder":"Enter Description","rows":4}),
            "warranty": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter The Product Warranty.."}),
            "return_policy": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter The Product Return Policy.."}),

        }



class ForgotPasswordForm(forms.Form):
    email=forms.CharField(widget=forms.EmailInput(attrs={"class":"form-control","placeholder":"Enter Registered Email"}))



    def clean_email(self):
        e=self.cleaned_data.get("email")
        if Customer.objects.filter(user__email=e).exists():
            pass
        else:
            raise forms.ValidationError("Customer Does not Exists for this email id..")

        return e



class PasswordResetForm(forms.Form):
    new_password=forms.CharField(widget=forms.PasswordInput(
        attrs={"class":"form-control","autocomplete":"new-password","placeholder":"Enter new Password"}),label="New Password"),
    confirm_new_password=forms.CharField(widget=forms.PasswordInput(
        attrs={"class":"form-control","autocomplete":"new-password","placeholder":"Confirm New Password"}),label="Confirm New Password"),


    def clean_confirm_new_password(self):
        new_password=self.cleaned_data.get('new_password')
        confirm_new_password=self.cleaned_data.get('confirm_new_password')
        if new_password != confirm_new_password:
            raise forms.ValidationError("New did not match! ")

        return confirm_new_password



class SetPasswordForm(SetPasswordForm,forms.ModelForm):
    new_password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={"class": "form-control", "autocomplete": "new-password", "placeholder": "Enter new Password"}),
        label="New Password"),
    new_password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={"class": "form-control", "autocomplete": "new-password", "placeholder": "Confirm New Password"}),
        label="Confirm New Password"),

    class Meta:
        model = get_user_model()
        fields = ['new_password1', 'new_password2']


