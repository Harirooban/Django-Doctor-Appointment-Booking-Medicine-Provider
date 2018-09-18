import hashlib
from django.http import HttpResponse
from django.shortcuts import render, HttpResponseRedirect
import sqlite3
from .models import products, categories, Doctor ,Patient
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from .forms import EmployeeForm, DoctorForm


def detail(request):
    db = sqlite3.connect('db.sqlite3')
    cursor = db.cursor()
    if 'email' not in request.session:
        loggedIn = False
        firstName = ''
        noOfItems = 0
    else:
        loggedIn = True
        cursor.execute("SELECT userId, firstName FROM app_users WHERE email = '" + request.session['email'] + "'")
        userId, firstName = cursor.fetchone()
        cursor.execute('SELECT count(productId_id) FROM app_kart WHERE userId_id = ' + str(userId))
        noOfItems = cursor.fetchone()[0]
    db.commit()
    return loggedIn, firstName, noOfItems


def index(request):
    loggedIn, firstName, noOfItems = detail(request)
    db = sqlite3.connect('db.sqlite3')
    cursor = db.cursor()
    cursor.execute('SELECT productId, name, price, description, image  FROM app_products')
    itemData = cursor.fetchall()
    cursor.execute('SELECT categoryId, name FROM app_categories')
    categoryData = cursor.fetchall()
    itemData = parse(itemData)
    return render(request, 'index.html',
                  {'itemData': itemData, 'loggedIn': loggedIn, 'firstName': firstName, 'noOfItems': noOfItems,
                   'categoryData': categoryData})


def product(request):
    loggedIn, firstName, noOfItems = detail(request)
    db = sqlite3.connect('db.sqlite3')
    cursor = db.cursor()
    cursor.execute('SELECT productId, name, price, description, image FROM app_products')
    itemData = cursor.fetchall()
    cursor.execute('SELECT categoryId, name, image FROM app_categories')
    catData = cursor.fetchall()
    return render(request, 'product.html',
                  {'loggedIn': loggedIn, 'catData': catData, 'firstName': firstName, 'noOfItems': noOfItems,
                   'itemData': itemData})


def book(request):
    DoctorId = request.GET.get('DoctorId')
    db = sqlite3.connect('db.sqlite3')
    cursor = db.cursor()
    cursor.execute(
        'SELECT DoctorId, DoctorName, SpecilistIn, EmailId FROM app_doctor WHERE DoctorId = ' + str(DoctorId))
    DoctorData = cursor.fetchone()
    return render(request, 'appointment.html', {'DoctorData': DoctorData})


def appoint(request):
    loggedIn, firstName, noOfItems = detail(request)
    if request.method == 'POST':
        name = request.POST.get("name")
        phone = request.POST.get("phonenumber")
        Email = request.POST.get("Email")
        gender = request.POST.get("gender")
        DoctorName = request.POST.get("dname")
        Spec = request.POST.get("digo")
        EmailId = request.POST.get("long")
        time = request.POST.get("time")
        date = request.POST.get("date")
        visit = request.POST.get("visit")
        db = sqlite3.connect('db.sqlite3')
        try:
            cursor = db.cursor()
            cursor.execute(
                'INSERT INTO app_patient (name, phone, Email, gender, DoctorName, Spec, EmailId, time, visit, date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (name, phone, Email, gender, DoctorName, Spec, EmailId, time, visit, date))
            cursor.execute("SELECT * FROM app_patient ORDER BY id DESC LIMIT 1")
            problem = cursor.fetchall()
            mail = get_template('mail1.html')
            subject, from_email, to = 'Appointment for you', 'harirooban43@gmail.com', EmailId
            text_content = 'This is an important message.'
            html_content = mail.render({'problem': problem, 'firstName': firstName})
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            db.commit()
        except:
            db.rollback()
            db.close()
        return HttpResponseRedirect('/app/')


def contact(request):
    loggedIn, firstName, noOfItems = detail(request)

    return render(request, 'contact.html', {'loggedIn': loggedIn, 'firstName': firstName, 'noOfItems': noOfItems})


def loginForm(request):
    if 'email' in request.session:
        return request('/index')
    else:
        return render(request, 'login.html')


def login(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        password = request.POST.get("password")
        if is_valid(email, password):
            request.session['email'] = email
            return HttpResponseRedirect('/app/')
        else:
            return HttpResponse("Invalid")
    return render(request, 'login.html')


def registerForm(request):
    return render(request, 'register.html')


def register(request):
    if request.method == 'POST':
        password = request.POST.get("password")
        email = request.POST.get("email")
        firstName = request.POST.get("firstName")
        lastName = request.POST.get("lastName")
        db = sqlite3.connect('db.sqlite3')
        try:
            cursor = db.cursor()
            # p = users(password=hashlib.md5(password.encode()).hexdigest(), email=email, firstname=firstName, lastName=lastName)
            # p.save()
            cursor.execute('INSERT INTO app_users (password, email, firstname, lastname) VALUES (?, ?, ?, ?)',
                           (hashlib.md5(password.encode()).hexdigest(), email, firstName, lastName))
            db.commit()
        except:
            db.rollback()
            db.close()
    return render(request, 'login.html')


def addToCart(request):
    if 'email' not in request.session:
        return HttpResponseRedirect('/app/login')
    else:
        productId = request.GET.get('productId')
        db = sqlite3.connect('db.sqlite3')
        cursor = db.cursor()
        cursor.execute("SELECT userId FROM app_users WHERE email = '" + request.session['email'] + "'")
        userId = cursor.fetchone()[0]
        try:
            cursor.execute("INSERT INTO app_kart (userId_id, productId_id) VALUES (?, ?)", (userId, productId))
            db.commit()
            msg = "Added successfully"
        except:
            db.rollback()
            msg = "Error occured"
        print (msg)
    db.close()
    return HttpResponseRedirect('/app/')


def cart(request):
    if 'email' not in request.session:
        return HttpResponseRedirect('/app/login')
    loggedIn, firstName, noOfItems = detail(request)
    email = request.session['email']
    db = sqlite3.connect('db.sqlite3')
    cursor = db.cursor()
    cursor.execute("SELECT userId FROM app_users WHERE email = '" + email + "'")
    userId = cursor.fetchone()[0]
    cursor.execute(
        "SELECT app_products.productId, app_products.name, app_products.price, app_products.image FROM app_products, app_kart WHERE app_products.productId = app_kart.productId_id AND app_kart.userId_id = " + str(
            userId))
    products = cursor.fetchall()
    totalPrice = 0
    for row in products:
        totalPrice += row[2]
    return render(request, "kart.html",
                  {'products': products, 'totalPrice': totalPrice, 'loggedIn': loggedIn, 'firstName': firstName,
                   'noOfItems': noOfItems})


def clearcart(request):
    loggedIn, firstName, noOfItems = detail(request)
    email = request.session['email']
    db = sqlite3.connect('db.sqlite3')
    cursor = db.cursor()
    cursor.execute("SELECT userId,email FROM app_users WHERE email = '" + email + "'")
    userId = cursor.fetchone()[0]
    if noOfItems == 0:
        return HttpResponseRedirect('/app/')
    else:
        cursor.execute(
            "SELECT app_products.productId, app_products.name, app_products.price, app_products.image FROM app_products, app_kart WHERE app_products.productId = app_kart.productId_id AND app_kart.userId_id = " + str(
                userId))
        products = cursor.fetchall()
        mail = get_template('mail.html')
        subject, from_email, to = 'Product Confirm', 'harirooban43@gmail.com', email
        text_content = 'This is an important message.'
        html_content = mail.render({'products': products, 'firstName': firstName})
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        cursor.execute(
            "INSERT into app_order SELECT NULL, app_products.name, app_products.price, app_products.description, app_products.image, app_products.productId, app_kart.userId_id FROM app_products, app_kart WHERE app_products.productId = app_kart.productId_id AND app_kart.userId_id = " + str(
                userId))
        cursor.execute("DELETE FROM app_kart WHERE userId_id = " + str(userId))
    db.commit()
    return HttpResponseRedirect('/app/', {'loggedIn': loggedIn, 'firstName': firstName, 'noOfItems': noOfItems})


def category(request):
    loggedIn, firstName, noOfItems = detail(request)
    categoryId = request.GET.get("categoryId")
    db = sqlite3.connect('db.sqlite3')
    cursor = db.cursor()
    cursor.execute(
        "SELECT app_products.productId, app_products.name, app_products.price, app_products.image, app_categories.name FROM app_products, app_categories WHERE app_products.categoryId_id = app_categories.categoryId AND app_categories.categoryId = " + categoryId)
    data = cursor.fetchall()
    db.close()
    categoryName = data[0][4]
    data = parse(data)
    return render(request, 'product_detail.html',
                  {'data': data, 'loggedIn': loggedIn, 'firstName': firstName, 'noOfItems': noOfItems,
                   'categoryName': categoryName})


def aboutproduct(request):
    loggedIn, firstName, noOfItems = detail(request)
    productId = request.GET.get('productId')
    db = sqlite3.connect('db.sqlite3')
    cursor = db.cursor()
    cursor.execute('SELECT productId, name, price, description, image FROM app_products WHERE productId = ' + productId)
    productData = cursor.fetchone()
    db.close()
    return render(request, 'aboutproduct.html',
                  {'data': productData, 'loggedIn': loggedIn, 'firstName': firstName, 'noOfItems': noOfItems})


def addItem(request):
    if request.method == "POST":
        name = request.POST.get("name", False)
        price = float(request.POST.get("price", False))
        description = request.POST.get("description", False)
        categoryId_id = int(request.POST.get("category", False))
        image = request.FILES.get("image", False)
        db = sqlite3.connect('db.sqlite3')
        try:
            p = products(name=name, price=price, description=description, categoryId_id=categoryId_id, image=image)
            p.save()
            db.commit()
            msg = "added successfully"
        except:
            msg = "error occurred"
            db.rollback()
        db.close()
        print(msg)
        return HttpResponseRedirect('/app/remove/')


def removeFromCart(request):
    if 'email' not in request.session:
        return render(request, 'login.html')
    email = request.session['email']
    productId = int(request.GET.get('productId'))
    db = sqlite3.connect('db.sqlite3')
    cursor = db.cursor()
    cursor.execute("SELECT userId FROM app_users WHERE email = '" + email + "'")
    userId = cursor.fetchone()[0]
    try:
        cursor.execute(
            "DELETE FROM app_kart WHERE userId_id = " + str(userId) + " AND productId_id = " + str(productId))
        db.commit()
        msg = "removed successfully"
    except:
        db.rollback()
        msg = "error occured"
    db.close()
    print(msg)
    return HttpResponseRedirect('/app/')


def remove(request):
    if not request.session.get('logged_in'):
        return render(request, 'alogin.html')
    else:
        email = request.session['logged_in']
        db = sqlite3.connect('db.sqlite3')
        cursor = db.cursor()
        cursor.execute('SELECT productId, name, price, description,CategoryId_id,image FROM app_products')
        data = cursor.fetchall()
        cursor.execute('SELECT categoryId,name,image FROM app_categories')
        catData = cursor.fetchall()
        cursor.execute("SELECT email,firstName,lastName FROM app_admin WHERE email = '" + email + "'")
        tata = cursor.fetchall()
        return render(request, 'admin.html', {'data': data, 'catData': catData, 'product': product, 'tata': tata})


def removeItem(request):
    productId = request.GET.get('productId')
    db = sqlite3.connect('db.sqlite3')
    categoryId = request.GET.get('categoryId')
    try:
        cursor = db.cursor()
        cursor.execute('DELETE FROM app_products WHERE productId = ' + productId)
        db.commit()
        msg = "Deleted successfully"
    except:
        cursor = db.cursor()
        cursor.execute('DELETE FROM app_categories WHERE categoryId = ' + categoryId)
        db.commit()
    db.close()
    return HttpResponseRedirect('/app/remove/')


def logout(request):
    request.session.pop('email', None)
    return HttpResponseRedirect('/app/')


def parse(data):
    ans = []
    i = 0
    while i < len(data):
        curr = []
        for j in range(7):
            if i >= len(data):
                break
            curr.append(data[i])
            i += 1
        ans.append(curr)
    return ans


def is_valid(email, password):
    db = sqlite3.connect('db.sqlite3')
    cursor = db.cursor()
    cursor.execute('SELECT email, password FROM app_users')
    data = cursor.fetchall()
    for row in data:
        if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
            return True
    return False


# admin

def caddItem(request):
    if request.method == "POST":
        name = request.POST.get("name", False)
        image = request.FILES.get("image", False)
        db = sqlite3.connect('db.sqlite3')
        try:
            p = categories(name=name, image=image)
            p.save()
            db.commit()
            msg = "added successfully"
        except:
            msg = "error occurred"
            db.rollback()
        db.close()
        print(msg)
        return HttpResponseRedirect('/app/')


def aloginForm(request):
    if 'email' in request.session:
        return request('/app/remove/')
    else:
        return render(request, 'alogin.html')


def alogin(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        password = request.POST.get("password")
        if is_valid1(email, password):
            request.session['logged_in'] = email
            request.session.set_expiry(550)
            return HttpResponseRedirect('/app/remove/')
        else:
            return HttpResponse("Invalid")
    return render(request, 'alogin.html')


def aregisterForm(request):
    return render(request, 'aregister.html')


def aregister(request):
    if request.method == 'POST':
        password = request.POST.get("password")
        email = request.POST.get("email")
        firstName = request.POST.get("firstName")
        lastName = request.POST.get("lastName")
        db = sqlite3.connect('db.sqlite3')
        try:
            cursor = db.cursor()
            # p = users(password=hashlib.md5(password.encode()).hexdigest(), email=email, firstname=firstName, lastName=lastName)
            # p.save()
            cursor.execute('INSERT INTO app_admin (password, email, firstname, lastname) VALUES (?, ?, ?, ?)',
                           (hashlib.md5(password.encode()).hexdigest(), email, firstName, lastName))
            db.commit()
        except:
            db.rollback()
            db.close()
    return render(request, 'alogin.html')


def is_valid1(email, password):
    db = sqlite3.connect('db.sqlite3')
    cursor = db.cursor()
    cursor.execute('SELECT email, password FROM app_admin')
    data = cursor.fetchall()
    for row in data:
        if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
            return True
    return False


def update(request, productId):
    product = products.objects.get(productId=productId)
    form = EmployeeForm(request.POST or None, instance=product)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect('/app/remove/')
    return render(request, 'update.html', {'form': form, 'product': product})


def alogout(request):
    request.session.pop('logged_in', None)
    return HttpResponseRedirect('/app/alogin/')


def DoctorRegister(request):
    form = DoctorForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            password = request.POST.get("password")
            PhoneNumber = request.POST.get("PhoneNumber")
            DoctorName = request.POST.get("DoctorName")
            SpecilistIn = request.POST.get("SpecilistIn")
            EmailId = request.POST.get("EmailId")
            form = Doctor(password=hashlib.md5(password.encode()).hexdigest(), PhoneNumber=PhoneNumber,
                          DoctorName=DoctorName, SpecilistIn=SpecilistIn, EmailId=EmailId)
            form.save()
            return HttpResponseRedirect('/app/DoctorLoginForm')
    return render(request, 'DoctorRegister.html', {'form': form})


def DoctorLogin(request):
    if request.method == 'POST':
        EmailId = request.POST.get("EmailId")
        password = request.POST.get("password")
        if is_valid2(EmailId, password):
            request.session['firstName'] = EmailId
            request.session.set_expiry(550)
            return HttpResponseRedirect('/app/DoctorPage/')
        else:
            return HttpResponse("Invalid")
    return render(request, 'DoctorLogin.html')


def DoctorLoginForm(request):
    if 'EmailId' in request.session:
        return request('/app/DoctorPage/')
    else:
        return render(request, 'DoctorLogin.html')


def is_valid2(EmailId, password):
    db = sqlite3.connect('db.sqlite3')
    cursor = db.cursor()
    cursor.execute('SELECT EmailId, password FROM app_doctor')
    data = cursor.fetchall()
    for row in data:
        if row[0] == EmailId and row[1] == hashlib.md5(password.encode()).hexdigest():
            return True
    return False


def DoctorLogout(request):
    request.session.pop('firstName', None)
    return HttpResponseRedirect('/app/DoctorLoginForm/')


def DoctorPage(request):
    if not request.session.get('firstName'):
        return render(request, 'DoctorLogin.html')
    else:
        EmailId = request.session['firstName']
        db = sqlite3.connect('db.sqlite3')
        cursor = db.cursor()
        cursor.execute("SELECT DoctorName FROM app_doctor WHERE EmailId = '" + EmailId + "'")
        tata = cursor.fetchall()
        cursor.execute("SELECT EmailId FROM app_doctor WHERE EmailId = '" + EmailId + "'")
        EmailId = cursor.fetchone()[0]
        cursor.execute("SELECT id, name, phone, Email, visit, Time,date FROM app_patient WHERE app_patient.EmailId = '" + EmailId + "'")
        PatientData = cursor.fetchall()
        cursor.execute("SELECT name,phone,gender,email,visit,date,time FROM app_confirm WHERE EmailId = '" + EmailId + "'")
        History = cursor.fetchall()
        cursor.execute("SELECT count(id) FROM app_patient WHERE EmailId = '" + EmailId + "'")
        noOfAppoint = cursor.fetchone()[0]
        cursor.execute("SELECT count(id) FROM app_confirm WHERE EmailId = '" + EmailId + "'")
        noOfHistory = cursor.fetchone()[0]
        return render(request, 'Doctor.html', {'tata': tata, 'PatientData': PatientData, 'History': History, 'noOfAppoint': noOfAppoint,'noOfHistory': noOfHistory})


def DoctorDetail(request):
    db = sqlite3.connect('db.sqlite3')
    cursor = db.cursor()
    cursor.execute("SELECT DoctorId, DoctorName,SpecilistIn FROM app_doctor")
    data = cursor.fetchall()
    return render(request, 'DoctorDetail.html', {'data': data})


def YourCart(request):
    if 'email' not in request.session:
        return render(request, 'login.html')
    loggedIn, firstName, noOfItems = detail(request)
    email = request.session['email']
    db = sqlite3.connect('db.sqlite3')
    cursor = db.cursor()
    cursor.execute("SELECT userId FROM app_users WHERE email = '" + email + "'")
    userId = cursor.fetchone()[0]
    cursor.execute("SELECT productId, name, price, image FROM app_order WHERE  app_order.userId_id = '" + str(userId)+"'")
    products = cursor.fetchall()
    return render(request, "YourCart.html",{'products': products, 'loggedIn': loggedIn, 'firstName': firstName, 'noOfItems': noOfItems})


def CancelAppointment(request):
    id = request.GET.get('id')
    db = sqlite3.connect('db.sqlite3')
    cursor = db.cursor()
    email = Patient.objects.get(id=id)
    cursor.execute("SELECT name FROM app_patient WHERE id = '" + str(id) + "'")
    PatientData = cursor.fetchall()
    mail = get_template('Cancel.html')
    subject, from_email, to = 'Appointment Cancel', 'harirooban43@gmail.com', email
    text_content = 'This is an important message.'
    html_content = mail.render({'PatientData': PatientData})
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    cursor.execute("DELETE FROM app_patient WHERE id = '" + str(id) + "'")
    db.commit()
    return HttpResponseRedirect('/app/DoctorPage')


def ConfirmAppointment(request):
    id = request.GET.get('id')
    db = sqlite3.connect('db.sqlite3')
    cursor = db.cursor()
    email = Patient.objects.get(id=id)
    cursor.execute("SELECT name ,date,time,gender FROM app_patient WHERE id = '" + str(id) + "'")
    PatientData = cursor.fetchall()
    mail = get_template('Confirm.html')
    subject, from_email, to = 'Appointment confirmation mail', 'harirooban43@gmail.com', email
    text_content = 'This is an important message.'
    html_content = mail.render({'PatientData': PatientData})
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    cursor.execute("INSERT INTO app_confirm SELECT NULL,name, phone,email,gender,date,time,visit,EmailId FROM app_patient WHERE id ='" + str(id)+"'")
    cursor.execute("DELETE FROM app_patient WHERE id = '" + str(id)+"'")
    db.commit()
    return HttpResponseRedirect('/app/DoctorPage/')

