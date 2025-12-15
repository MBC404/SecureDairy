from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q

from .models import Connection, Letter, LetterVersion


def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST["username"],
            password=request.POST["password"]
        )
        if user:
            login(request, user)
            return redirect("dashboard")
    return render(request, "letters/login.html")


def signup_view(request):
    if request.method == "POST":
        User.objects.create_user(
            username=request.POST["username"],
            password=request.POST["password"]
        )
        return redirect("login")
    return render(request, "letters/signup.html")


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def dashboard(request):
    user = request.user

    pending_requests = Connection.objects.filter(
        receiver=user, accepted=False
    ).select_related("requester")

    connections = Connection.objects.filter(
        accepted=True
    ).filter(
        Q(requester=user) | Q(receiver=user)
    ).select_related("requester", "receiver")

    return render(request, "letters/dashboard.html", {
        "pending_requests": pending_requests,
        "connections": connections,
    })


@login_required
def search_user(request):
    users = []
    if request.method == "POST":
        users = User.objects.filter(
            username__icontains=request.POST["username"]
        ).exclude(id=request.user.id)
    return render(request, "letters/search.html", {"users": users})


@login_required
def connect_user(request, user_id):
    other = get_object_or_404(User, id=user_id)
    Connection.objects.get_or_create(
        requester=request.user,
        receiver=other
    )
    return redirect("dashboard")


@login_required
def accept_request(request, conn_id):
    conn = get_object_or_404(Connection, id=conn_id, receiver=request.user)
    conn.accepted = True
    conn.save()
    return redirect("dashboard")


@login_required
def conversation(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    letters = Letter.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).prefetch_related("versions")

    return render(request, "letters/conversation.html", {
        "other_user": other_user,
        "letters": letters,
    })


@login_required
def send_letter(request, user_id):
    receiver = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        letter = Letter.objects.create(
            sender=request.user,
            receiver=receiver
        )
        LetterVersion.objects.create(
            letter=letter,
            content=request.POST["content"],
            approved=True
        )
        return redirect("conversation", user_id=receiver.id)

    return render(request, "letters/send.html", {"receiver": receiver})


@login_required
def modify_letter(request, letter_id):
    letter = get_object_or_404(
        Letter,
        id=letter_id,
        receiver=request.user
    )

    if request.method == "POST":
        LetterVersion.objects.create(
            letter=letter,
            content=request.POST["proposed_content"],
            approved=False
        )
        return redirect("conversation", user_id=letter.sender.id)

    return render(request, "letters/modify.html", {"letter": letter})

@login_required
def approve_modification(request, version_id):
    version = get_object_or_404(LetterVersion, id=version_id)

    letter = version.letter

    # ONLY sender can approve
    if request.user != letter.sender:
        return redirect("conversation", user_id=letter.receiver.id)

    # approve this version
    version.approved = True
    version.save()

    return redirect(
        "conversation",
        user_id=letter.receiver.id
    )
