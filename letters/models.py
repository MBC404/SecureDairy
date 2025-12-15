from django.db import models
from django.contrib.auth.models import User

class Connection(models.Model):
    requester = models.ForeignKey(
        User, related_name="sent_requests", on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        User, related_name="received_requests", on_delete=models.CASCADE
    )
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.requester} -> {self.receiver} ({self.accepted})"


class Letter(models.Model):
    sender = models.ForeignKey(
        User, related_name="sent_letters", on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        User, related_name="received_letters", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} -> {self.receiver}"


class LetterVersion(models.Model):
    letter = models.ForeignKey(
        Letter, related_name="versions", on_delete=models.CASCADE
    )
    content = models.TextField()
    approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Version of Letter {self.letter.id}"
