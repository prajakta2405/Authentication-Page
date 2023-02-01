from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from myproject import settings
from django.core.mail import EmailMessage, send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from . tokens import generate_token
import mysql.connector as sql


# Create your views here.
def home(request):
    return render(request, "authenticate/index.html")


username =''
fname =''
lname = ''
email = ''
pass1 =''
pass2 = ''



def signup(request):
    global username,fname,lname,email,pass1,pass2

    if request.method == "POST":
        m = sql.connect(host="localhost",user="root",password="prajakta1925",database='website')   
        cursor=m.cursor()
        d = request.POST
        for key,value in d.items():
            
            if key=="username":
                username=value
            
            if key=="fname":
                fname=value
            
            if key=="lname":
                lname=value

            if key=="email":
                email=value

            if key=="pass1":
                pass1=value

            if key=="pass2":
                pass2=value
        c="insert into users values('{}','{}','{}','{}','{}','{}')".format(username,fname,lname,email,pass1,pass2)
        cursor.execute(c)
        m.commit()
    

            
            
       

        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try some other username")
            return redirect('home')
        

        if User.objects.filter(email=email):
            messages.error(request, "Email already registerd!")
            return redirect('home')
        

        if len(username)>10:
            messages.error(request,"Username must be under 10 characters")
        
        if pass1!=pass2:
            messages.error(request, "Password didn't match!")

        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!")
            return redirect('home')

        myuser = User.objects.create_user(username,email,pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False
        myuser.save()

        messages.success(request,"Your Account has been successfully created.\n We have also send confirmation email,please confirm your email address in order to activate your account. ")

        #sending email 

        subject ="Welcome to Django Login"
        message = "Hello "+ myuser.first_name+"!\n"+"Welcome to our website!\n"+"Thank you for visiting to our website\n We have also send confirmation email. \n Please confirm your email address in order to activate your account.\n\n Thank you!\n Prajakta Surve"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)


        #sendig confirmation email

        current_site = get_current_site(request)
        email_subject = "Confirm your email"
        message2 = render_to_string('email_confirmation.html',{
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],


        )
        email.fail_silently = True
        email.send()





        return redirect('signin')

    return render(request, "authenticate/signup.html")


def signin(request):
    

    if request.method =='POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']
        user = authenticate(username =username,password=pass1)

        if user is not None:
            login(request,user)
            fname=user.first_name
            return render(request,"authenticate/index.html",{'fname':fname})
        else:
             messages.error(request,"Bad credentials!")
             return redirect('home')

    return render(request, "authenticate/signin.html")



def signout(request):
    logout(request)
    messages.success(request,"Logged out Successfully!")
    return redirect('home')

def activate(request,uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None
    
    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect('home')
    else:
        return render(request, 'activation_failed.html')

