from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q # Used for OR queries

# CRITICAL FIX: Import ModificationForm
from .forms import SignupForm, LetterForm, ModificationForm 

from .models import Letter, ModificationRequest, UserConnection, LetterVersion


# ---------- AUTH ----------

def login_view(request):
    error_message = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        user = authenticate(
            request,
            username=username,
            password=password,
        )
        if user:
            login(request, user)
            return redirect("dashboard")
        else:
            # Error message for wrong password/username
            error_message = "Invalid username or password. Please try again."
            
    # Pass the error message to the template
    return render(request, "letters/login.html", {"error_message": error_message})


def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            # form.save() handles user creation, password hashing, and ensures unique username
            user = form.save()
            # Log the user in immediately after signup
            login(request, user)
            return redirect("dashboard")
    else:
        form = SignupForm()
        
    return render(request, "letters/signup.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


# ---------- DASHBOARD (CRITICAL FIX) ----------

@login_required
def dashboard(request):
    user = request.user

    # 1. Connection Requests (Incoming requests to the current user)
    pending_requests = UserConnection.objects.filter(
        receiver=user, 
        status="PENDING"
    ).select_related('requester') # Requests sent to *you*

    # 2. My Connections (Accepted connections)
    connections = UserConnection.objects.filter(
        Q(requester=user) | Q(receiver=user),
        status="ACCEPTED"
    ).select_related('requester', 'receiver') # Use Q object for OR logic

    # 3. Pending Modifications (Awaiting YOUR approval - you must be the letter's sender)
    modifications = ModificationRequest.objects.filter(
        letter__sender=user, 
        status="PENDING"
    ).select_related('letter', 'requested_by') 

    context = {
        "pending_requests": pending_requests,
        "connections": connections,
        "modifications": modifications,
    }

    return render(request, "letters/dashboard.html", context)


# ---------- CONNECTION MANAGEMENT ----------

@login_required
def search_user(request):
    users = None
    query = None
    if request.method == "POST":
        query = request.POST.get("username")
        # Find users matching the search term, excluding the current user
        users = User.objects.filter(username__icontains=query).exclude(id=request.user.id)
    
    return render(request, "letters/search.html", {"users": users, "query": query})


@login_required
def send_connection(request, user_id):
    # Ensure the target user exists
    receiver = get_object_or_404(User, id=user_id)
    requester = request.user

    # Prevent self-connection or duplicate pending requests
    if requester != receiver and not UserConnection.objects.filter(
        requester=requester, receiver=receiver
    ).exists():
        UserConnection.objects.create(requester=requester, receiver=receiver, status="PENDING")

    return redirect("dashboard")


@login_required
def accept_connection(request, conn_id):
    connection = get_object_or_404(UserConnection, id=conn_id)

    # Ensure the current user is the receiver and the status is PENDING
    if connection.receiver == request.user and connection.status == "PENDING":
        connection.status = "ACCEPTED"
        connection.save()

    return redirect("dashboard")


# ---------- CONVERSATION & LETTER SENDING ----------

@login_required
def conversation(request, user_id):
    # The other user in the conversation
    other_user = get_object_or_404(User, id=user_id)
    current_user = request.user

    # Check if a connection exists and is accepted
    connection_exists = UserConnection.objects.filter(
        Q(requester=current_user, receiver=other_user) | Q(requester=other_user, receiver=current_user),
        status="ACCEPTED"
    ).exists()

    if not connection_exists:
        # If no connection, redirect to search or dashboard
        return redirect("dashboard")

    # Get all letters between these two users, ordered by creation date
    letters = Letter.objects.filter(
        Q(sender=current_user, receiver=other_user) | Q(sender=other_user, receiver=current_user)
    ).order_by("created_at").select_related('sender', 'receiver')

    context = {
        "other_user": other_user,
        "letters": letters,
        "connection_exists": connection_exists,
    }

    return render(request, "letters/conversation.html", context)


@login_required
def send_letter(request, user_id):
    receiver = get_object_or_404(User, id=user_id)

    # Check for accepted connection before allowing a send
    connection_exists = UserConnection.objects.filter(
        Q(requester=request.user, receiver=receiver) | Q(requester=receiver, receiver=request.user),
        status="ACCEPTED"
    ).exists()

    if not connection_exists:
        return redirect("dashboard")
    
    if request.method == "POST":
        form = LetterForm(request.POST) # Use the form to validate the content
        if form.is_valid():
            content = form.cleaned_data["content"]
            
            # 1. Create the base Letter object
            letter = Letter.objects.create(
                sender=request.user,
                receiver=receiver,
            )

            # 2. Create the first LetterVersion (instantly approved)
            LetterVersion.objects.create(
                letter=letter,
                content=content,
                created_by=request.user,
                is_approved=True
            )

            return redirect("conversation", user_id=user_id)
        # If form is NOT valid, execution falls through to render the page with errors.
    
    # Handle GET request (or invalid POST request)
    else:
        # Instantiate a blank form for the GET request
        form = LetterForm() 

    # Pass both receiver and the form object to the template
    return render(request, "letters/send.html", {
        "receiver": receiver,
        "form": form,
    })


# ---------- MODIFY LETTER (CRITICAL FIX) ----------

@login_required
def modify_letter(request, letter_id):
    letter = get_object_or_404(Letter, id=letter_id)
    
    # Prevent modification request if no approved version exists yet
    if not letter.approved_version():
        recipient = letter.receiver if letter.sender == request.user else letter.sender
        return redirect("conversation", user_id=recipient.id)

    if request.method == "POST":
        # CRITICAL FIX: Instantiate the form with POST data for validation
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
        # CRITICAL FIX: Instantiate a blank form for GET requests
        form = ModificationForm()

    # The template expects both 'letter' and 'form'
    return render(request, "letters/modify.html", {
        "letter": letter,
        "form": form, # Pass the form object
    })


# ---------- APPROVE MOD ----------

@login_required
def approve_modification(request, mod_id):
    mod = get_object_or_404(ModificationRequest, id=mod_id)

    # Only the SENDER of the letter can approve the modification
    if request.user != mod.letter.sender:
        return redirect("dashboard") # Not authorized

    if request.method == "POST":
        if mod.status == 'PENDING':
            # This method in the model is expected to handle status change and new LetterVersion creation
            mod.approve() 
        return redirect("dashboard")

    # For a GET request, show the modification details for review
    return render(request, "letters/approve_mod.html", {"modification": mod})