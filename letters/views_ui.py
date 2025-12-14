from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q

from .models import Letter, ModificationRequest, UserConnection, LetterVersion
from .forms import SignupForm # <-- NEW IMPORT


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
            form.save() 
            return redirect("login")
    else:
        form = SignupForm() # Empty form for GET request

    # Pass the form (with validation errors if present) to the template
    return render(request, "letters/signup.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


# ---------- DASHBOARD ----------

@login_required
def dashboard(request):
    pending_requests = UserConnection.objects.filter(
        receiver=request.user,
        status="PENDING"
    )

    accepted_connections = UserConnection.objects.filter(
        Q(requester=request.user) | Q(receiver=request.user),
        status="ACCEPTED"
    )

    modifications = ModificationRequest.objects.filter(
        letter__receiver=request.user,
        status="PENDING"
    )

    return render(request, "letters/dashboard.html", {
        "pending_requests": pending_requests,
        "connections": accepted_connections,
        "modifications": modifications,
    })


# ---------- SEARCH ----------

@login_required
def search_user(request):
    users = []
    query = ""

    if request.method == "POST":
        query = request.POST.get("username", "").strip()

        if query:
            users = User.objects.filter(
                username__icontains=query
            ).exclude(id=request.user.id)

    return render(request, "letters/search.html", {
        "users": users,
        "query": query,
    })


# ---------- CONNECTIONS ----------

@login_required
def send_connection(request, user_id):
    receiver = get_object_or_404(User, id=user_id)

    if receiver != request.user:
        UserConnection.objects.get_or_create(
            requester=request.user,
            receiver=receiver
        )

    return redirect("search_user")


@login_required
def accept_connection(request, conn_id):
    conn = get_object_or_404(
        UserConnection,
        id=conn_id,
        receiver=request.user
    )
    conn.status = "ACCEPTED"
    conn.save()
    return redirect("dashboard")


# ---------- CONVERSATION ----------

@login_required
def conversation(request, user_id):
    other = get_object_or_404(User, id=user_id)

    letters = Letter.objects.filter(
        sender__in=[request.user, other],
        receiver__in=[request.user, other]
    ).order_by("created_at")

    return render(request, "letters/conversation.html", {
        "letters": letters,
        "other": other
    })


# ---------- SEND LETTER ----------

@login_required
def send_letter(request, user_id):
    receiver = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        content = request.POST.get("content")

        letter = Letter.objects.create(
            sender=request.user,
            receiver=receiver
        )

        LetterVersion.objects.create(
            letter=letter,
            content=content,
            created_by=request.user,
            is_approved=True
        )

        return redirect("conversation", user_id=user_id)

    return render(request, "letters/send.html", {"receiver": receiver})


# ---------- MODIFY LETTER ----------

@login_required
def modify_letter(request, letter_id):
    letter = get_object_or_404(Letter, id=letter_id)

    if request.method == "POST":
        ModificationRequest.objects.create(
            letter=letter,
            requested_by=request.user,
            proposed_content=request.POST.get("proposed_content")
        )
        return redirect("dashboard")

    return render(request, "letters/modify.html", {"letter": letter})


# ---------- APPROVE MOD ----------

@login_required
def approve_modification(request, mod_id):
    mod = get_object_or_404(ModificationRequest, id=mod_id)
    mod.approve()
    return redirect("dashboard")