from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q
from .forms import SignupForm, LetterForm # cite: uploaded:views_ui.py

from .forms import SignupForm, LetterForm, ModificationForm 

from .models import Letter, ModificationRequest, UserConnection, LetterVersion




# ---------- AUTH ----------

def login_view(request):
    error_message = None # cite: uploaded:views_ui.py
    if request.method == "POST": # cite: uploaded:views_ui.py
        username = request.POST.get("username") # cite: uploaded:views_ui.py
        password = request.POST.get("password") # cite: uploaded:views_ui.py
        
        user = authenticate( # cite: uploaded:views_ui.py
            request,
            username=username,
            password=password,
        )
        if user: # cite: uploaded:views_ui.py
            login(request, user) # cite: uploaded:views_ui.py
            return redirect("dashboard") # cite: uploaded:views_ui.py
        else:
            # Error message for wrong password/username
            error_message = "Invalid username or password. Please try again." # cite: uploaded:views_ui.py
            
    # Pass the error message to the template
    return render(request, "letters/login.html", {"error_message": error_message}) # cite: uploaded:views_ui.py


def signup_view(request):
    if request.method == "POST": # cite: uploaded:views_ui.py
        form = SignupForm(request.POST) # cite: uploaded:views_ui.py
        if form.is_valid(): # cite: uploaded:views_ui.py
            # form.save() handles user creation, password hashing, and ensures unique username
            user = form.save() # cite: uploaded:views_ui.py
            login(request, user) # cite: uploaded:views_ui.py
            return redirect("dashboard") # cite: uploaded:views_ui.py
    else:
        form = SignupForm() # cite: uploaded:views_ui.py

    return render(request, "letters/signup.html", {"form": form}) # cite: uploaded:views_ui.py


@login_required
def logout_view(request):
    logout(request) # cite: uploaded:views_ui.py
    return redirect("login") # cite: uploaded:views_ui.py


# ---------- DASHBOARD / CONNECTION LOGIC ----------

@login_required
def dashboard(request):
    user = request.user

    # 1. Connection Requests (Incoming requests to the current user)
    pending_requests = UserConnection.objects.filter(
        receiver=user, 
        status="PENDING"
    ).select_related('requester') # Query for pending requests sent to *you*

    # 2. My Connections (Accepted connections where the current user is requester OR receiver)
    connections = UserConnection.objects.filter(
        Q(requester=user) | Q(receiver=user),
        status="ACCEPTED"
    ).select_related('requester', 'receiver') # Use Q object for OR logic

    # 3. Pending Modifications (Awaiting YOUR approval)
    # You only approve modifications for letters YOU SENT, which are PENDING
    modifications = ModificationRequest.objects.filter(
        # The current user must be the SENDER of the letter to approve the modification
        letter__sender=user, 
        status="PENDING"
    ).select_related('letter', 'requested_by') 

    context = {
        "pending_requests": pending_requests,
        "connections": connections,
        "modifications": modifications,
    }

    return render(request, "letters/dashboard.html", context)


@login_required
def search_user(request):
    query = None # cite: uploaded:views_ui.py
    users = [] # cite: uploaded:views_ui.py

    if request.method == "POST": # cite: uploaded:views_ui.py
        query = request.POST.get("username") # cite: uploaded:views_ui.py
        if query: # cite: uploaded:views_ui.py
            users = User.objects.filter( # cite: uploaded:views_ui.py
                username__icontains=query # cite: uploaded:views_ui.py
            ).exclude(id=request.user.id) # cite: uploaded:views_ui.py

    return render(request, "letters/search.html", {"query": query, "users": users}) # cite: uploaded:views_ui.py


@login_required
def send_connection(request, user_id):
    receiver = get_object_or_404(User, id=user_id) # cite: uploaded:views_ui.py

    # Prevent self-connection or duplicate requests (models handles unique_together check)
    if request.user != receiver: # cite: uploaded:views_ui.py
        UserConnection.objects.get_or_create( # cite: uploaded:views_ui.py
            requester=request.user, receiver=receiver # cite: uploaded:views_ui.py
        )

    return redirect("dashboard") # cite: uploaded:views_ui.py


@login_required
def accept_connection(request, conn_id):
    connection = get_object_or_404(UserConnection, id=conn_id) # cite: uploaded:views_ui.py

    # Ensure the user accepting is the receiver
    if request.user == connection.receiver: # cite: uploaded:views_ui.py
        connection.status = "ACCEPTED" # cite: uploaded:views_ui.py
        connection.save() # cite: uploaded:views_ui.py

    return redirect("dashboard") # cite: uploaded:views_ui.py


# ---------- LETTER LOGIC ----------

@login_required
def conversation(request, user_id):
    other_user = get_object_or_404(User, id=user_id) # cite: uploaded:views_ui.py
    
    # Find letters where the current user and the other user are sender/receiver
    letters = Letter.objects.filter( # cite: uploaded:views_ui.py
        Q(sender=request.user, receiver=other_user) | Q(sender=other_user, receiver=request.user) # cite: uploaded:views_ui.py
    ).order_by('created_at').select_related('approved_version') # cite: uploaded:views_ui.py

    return render(request, "letters/conversation.html", { # cite: uploaded:views_ui.py
        "other_user": other_user, 
        "letters": letters
    })


@login_required
def send_letter(request, user_id):
    # Retrieve the intended recipient
    receiver = get_object_or_404(User, id=user_id) # cite: uploaded:views_ui.py
    
    # Check for POST request
    if request.method == "POST": # cite: uploaded:views_ui.py
        form = LetterForm(request.POST) # Initialize form with submitted data # cite: uploaded:views_ui.py
        
        if form.is_valid(): # CRITICAL FIX: Only proceed if form is valid (content exists) # cite: uploaded:views_ui.py
            content = form.cleaned_data["content"] # cite: uploaded:views_ui.py
            
            # --- Database Save Logic ---
            
            # 1. Create the Letter object (the conversation container)
            letter = Letter.objects.create( # cite: uploaded:views_ui.py
                sender=request.user,
                receiver=receiver
            )

            # 2. Create the first LetterVersion
            LetterVersion.objects.create( # cite: uploaded:views_ui.py
                letter=letter,
                content=content,
                created_by=request.user,
                is_approved=True
            )

            return redirect("conversation", user_id=user_id) # cite: uploaded:views_ui.py
        # If form is NOT valid, execution falls through to render the page with errors.
    
    # Handle GET request (or invalid POST request)
    else:
        # CRITICAL: Instantiate a blank form for the GET request
        form = LetterForm() # cite: uploaded:views_ui.py

    # Pass both receiver and the form object to the template
    return render(request, "letters/send.html", {
        "receiver": receiver,
        "form": form, # <-- Fixes the missing text box
    }) # cite: uploaded:views_ui.py


# ---------- MODIFY LETTER ----------

@login_required
def modify_letter(request, letter_id):
    letter = get_object_or_404(Letter, id=letter_id)

    if request.method == "POST":
        # Instantiate the form with POST data for validation
        form = ModificationForm(request.POST) 
        if form.is_valid():
            # Create the modification request using cleaned data
            ModificationRequest.objects.create(
                letter=letter,
                requested_by=request.user,
                proposed_content=form.cleaned_data["proposed_content"] # Use cleaned data
            )
            return redirect("dashboard")
        # If form is not valid, the view falls through to render with errors
    
    else:
        # Pass a blank form for GET requests
        form = ModificationForm()

    # The template expects both 'letter' and 'form'
    return render(request, "letters/modify.html", {
        "letter": letter,
        "form": form, # <-- CRITICAL FIX: Pass the form object
    }) # cite: uploaded:views_ui.py


# ---------- APPROVE MOD ----------

@login_required
def approve_modification(request, mod_id):
    modification = get_object_or_404(ModificationRequest, id=mod_id) # cite: uploaded:views_ui.py

    # Only the original sender of the letter can approve
    if request.user == modification.letter.sender and modification.status == "PENDING": # cite: uploaded:views_ui.py
        modification.status = "APPROVED" # cite: uploaded:views_ui.py
        modification.approved_at = timezone.now() # cite: uploaded:views_ui.py
        modification.save() # cite: uploaded:views_ui.py
        
        # Create a new approved version
        LetterVersion.objects.create( # cite: uploaded:views_ui.py
            letter=modification.letter,
            content=modification.proposed_content,
            created_by=request.user,
            is_approved=True
        )

    return redirect("dashboard") # cite: uploaded:views_ui.py