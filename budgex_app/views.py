from django.shortcuts import render,redirect
import bcrypt
from django.contrib import messages
from django.http import HttpResponse
from budgex_app.models import User, Budget,Category,Transaction
from datetime import datetime
from decimal import Decimal
from django.db.models import Sum
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from .models import Transaction
from django.http import JsonResponse
from .currency_utils import get_exchange_rate 
# Create your views here.


    
#  creating currency changer :

def convert_currency_view(request):
    if request.method == 'POST':
        try:
            # Get the data from the request
            data = JsonResponse.loads(request.body)
            amount = data['amount']
            base_currency = data['base_currency']
            target_currency = data['target_currency']

            # Get the exchange rate using the utility function
            exchange_rate = get_exchange_rate(base_currency, target_currency)

            if isinstance(exchange_rate, float):
                # Convert the amount
                converted_amount = amount * exchange_rate
                return JsonResponse({"converted_amount": converted_amount})
            else:
                return JsonResponse({"error": exchange_rate}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return render(request,"changer.html")

#login page:

def login(request):
    if request.method=="POST":
        email=request.POST.get('email')
        password=request.POST.get('password')
        
        try:
            user=User.objects.get(email=email)
            if bcrypt.checkpw(password.encode(),user.password.encode()):
                request.session['userid']=user.id
                request.session['first_name']=user.first_name
                return redirect('index')
            else:
                messages.error(request,"Try Again, The Password and Email doesn't match")
        except User.DoesNotExist:

            messages.error(request,"This Email is not assigned in our database")
    return render(request,"login.html")
def register(request):

    if request.method=='POST':
        errors=User.objects.validator(request.POST)
        first_name=request.POST ['first_name']
        last_name=request.POST ['last_name']
        email=request.POST['email']
        password=request.POST['password']
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
       
        if len(errors)>0:
            for key,value in errors.items():
                messages.error(request,value)
            return render(request,"login.html")
        else:
            user=User.objects.create(first_name=first_name,last_name=last_name,email=email,password=pw_hash)
            request.session['userid'] = user.id
        return redirect('index')

    return render(request,"login.html")

def index(request):
    if 'userid' not in request.session:
        return redirect('login')

    userid = int(request.session.get('userid'))  # Ensure it's an integer
    user = User.objects.get(id=userid)  # Now define user first
    total_income = Transaction.objects.filter(transaction_type="income").aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Transaction.objects.filter(transaction_type="expense").aggregate(Sum('amount'))['amount__sum'] or 0
    remaining=total_income-total_expense
    budgets=Budget.objects.all()
    
    context = {
        'username': user.first_name,
        'userid': userid,
        'total_income':total_income,
        'total_expense':total_expense,
        'remaining':remaining,
        'budgets':budgets
    }

    return render(request, "index.html", context)

def addbudget(request):
    if 'userid' not in request.session:
        return redirect('login')
    categories=Category.objects.all()
    context={
        'categories':categories
    }
    if request.method=="POST":
        name=request.POST.get('name')
        amount=request.POST.get('amount')
        currency=request.POST.get('currency')
        category_id=request.POST.get('category')
        recurrence=request.POST.get('recurrence')
        start_date=request.POST.get('start_date')

        if not name or not amount or not category_id:
            messages.error(request, "Please fill in all required fields.")
            return redirect('addbudget')

        category = Category.objects.get(id=category_id)
        userid=request.session.get('userid')
        user=User.objects.get(id=userid)
        Budget.objects.create(name=name,
                              amount=amount,
                              currency=currency,
                              category=category,
                              recurrence=recurrence,
                              start_date=start_date,
                              user=user)
        return redirect('budget')
    return render (request,"addbudget.html",context)
    
def addtransaction(request):
    # Check if the user is logged in (if 'userid' is in session)
    userid = request.session.get('userid')
    if not userid:
        return redirect('login')  # Redirect to login if the user is not logged in

    # Ensure the 'userid' is an integer
    try:
        userid = int(userid)
    except ValueError:
        messages.error(request, "Invalid user session. Please log in again.")
        return redirect('login')  # Redirect to login if the session data is invalid

    if request.method == "POST":
        # Get form data
        budget_id = request.POST.get('budget')
        transaction_type = request.POST.get('transaction_type')
        amount = request.POST.get('amount')
        description = request.POST.get('description')

        # Validate required fields
        if not budget_id or not amount or not transaction_type:
            messages.error(request, "Please fill in all required fields.")
            return redirect('addtransaction')  # Corrected redirect to 'addtransaction'

        try:
            # Convert the amount to Decimal (you can also handle this in your form validation)
            amount = Decimal(amount)
        except ValueError:
            messages.error(request, "Invalid amount value.")
            return redirect('addtransaction')  # Redirect back to the form in case of invalid data

        # Get the selected user
        try:
            user = User.objects.get(id=userid)
        except User.DoesNotExist:
            messages.error(request, "User does not exist.")
            return redirect('login')  # Redirect to login if the user is not found

        # Get the selected budget
        try:
            budget = Budget.objects.get(id=budget_id)
            category = budget.category 
        except Budget.DoesNotExist:
            messages.error(request, "Invalid budget selected.")
            return redirect('addtransaction')

        # Create the transaction
        Transaction.objects.create(
            user=user,
            budget=budget,
            transaction_type=transaction_type,
            amount=amount,
            description=description,
            category=category 
        )

        messages.success(request, "Transaction added successfully!")
        return redirect('transactions')

    # If it's a GET request, get budgets for the logged-in user
    try:
        user = User.objects.get(id=userid)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('login')  # If the user does not exist in the session, redirect to login
    
    budgets = Budget.objects.filter(user=user)

    context = {
        'budgets': budgets
    }

    return render(request, "addtransaction.html", context)

def transactions(request):
    if 'userid' not in request.session:
        return redirect('login')
    
    user = User.objects.get(id=request.session['userid'])
    budgets = Budget.objects.filter(user=user)
    categories = Category.objects.all()
    transactions=Transaction.objects.filter(user=user)

        # Aggregate the transaction amounts by date
    transaction_data = (
        Transaction.objects
        .values('date')  # Group by the date
        .annotate(total_amount=Sum('amount'))  # Sum the transaction amounts for each date
        .order_by('date')  # Order by date to plot in the correct order
    )

    # Prepare the data for the chart
    dates = [entry['date'].strftime('%Y-%m-%d') for entry in transaction_data]
    amounts = [entry['total_amount'] for entry in transaction_data]
    
    context={
        'budgets':budgets,
        'categories':categories,
        'transactions':transactions,
        'dates':dates,
        'amounts':amounts,
        'transaction_data':transaction_data

    }

    return render(request,"transaction.html",context)
def budget(request):
    budgets=Budget.objects.all()
    context={
        'budgets':budgets
    }
    return render(request,"budget.html",context)
def reports(request):

    userid = int(request.session.get('userid'))  # Ensure it's an integer
    user = User.objects.get(id=userid)  # Now define user first
    total_income = Transaction.objects.filter(transaction_type="income").aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Transaction.objects.filter(transaction_type="expense").aggregate(Sum('amount'))['amount__sum'] or 0
    remaining=total_income-total_expense
    budgets=Budget.objects.all()
    transactions=Transaction.objects.all()
    categories=Category.objects.all()
    context = {
        'username': user.first_name,
        'userid': userid,
        'total_income':total_income,
        'total_expense':total_expense,
        'remaining':remaining,
        'budgets':budgets,
        'transactions':transactions,
        'categories':categories
    }


    return render(request, "reports.html", context)

def download_pdf(request):
    # Create a BytesIO buffer to store PDF data
    buffer = BytesIO()

    # Create a PDF object using ReportLab
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Add title to the PDF
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, 750, "Transaction Report")
    
    # Set up the table headers
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, 720, "Date")
    p.drawString(150, 720, "Description")
    p.drawString(250, 720, "Category")
    p.drawString(350, 720, "Type")
    p.drawString(450, 720, "Amount")

    # Set up the table data from the database
    p.setFont("Helvetica", 10)
    transactions = Transaction.objects.all()  # Adjust as necessary to fetch your transactions
    y_position = 700  # Start position for the rows

    # Loop through all transactions and add them to the table
    for transaction in transactions:
    # Safely handle category, description, and other fields that might be None
        category_name = transaction.category.name if transaction.category else "No Category"
        description = transaction.description if transaction.description else "No Description"
        
        # Ensure that other fields are also converted to strings, even if None
        date_str = str(transaction.date) if transaction.date else "Unknown Date"
        transaction_type = transaction.transaction_type if transaction.transaction_type else "Unknown Type"
        amount_str = f"${transaction.amount}" if transaction.amount else "$0.00"
        
        # Draw the transaction data
        p.drawString(50, y_position, date_str)
        p.drawString(150, y_position, description)
        p.drawString(250, y_position, category_name)
        p.drawString(350, y_position, transaction_type)
        p.drawString(450, y_position, amount_str)
        
        # Move to the next row
        y_position -= 20  # Adjust as needed

        # If the page is full, create a new page
        if y_position < 100:
            p.showPage()
            y_position = 750  # Reset the y_position to start from the top of the new page
    
    # Save the PDF to the buffer
    p.showPage()
    p.save()

    # Get the PDF data from the buffer
    pdf = buffer.getvalue()
    buffer.close()

    # Return the PDF as an HTTP response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="transaction_report.pdf"'
    return response

def settings(request):
    if 'userid' not in request.session:
        return redirect('login')
    #get user's data
    userid = int(request.session.get('userid'))  # Ensure it's an integer
    user = User.objects.get(id=userid)
    birthdate = user.birthdate
    
    if request.method=="POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        birthdate = request.POST.get('birthdate')
        #update data 
        user.first_name = first_name
        user.last_name = last_name
        if birthdate:
            user.birthdate = birthdate
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('settings')
    context = {
        'username': user.first_name,
        'firstname':user.first_name,
        'lastname':user.last_name,
        'useremail':user.email,
        'userid': userid,
        'birthdate':birthdate
        
    }
    return render(request, 'settings.html',context)

def logout(request):
    request.session.flush() 
    return redirect('login')
def settings_view(request,id):
    
    if request.method == 'POST':

        username = request.POST.get('username')
        email = request.POST.get('email')
        return redirect('settings')
    
    
    return render(request, 'settings.html' )