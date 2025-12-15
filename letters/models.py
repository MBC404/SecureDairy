from django.db import models
from django.contrib.auth.models import User

class Connection(models.Model):
    requester = models.ForeignKey(User, related_name="sent_requests", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_requests", on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.requester} -> {self.receiver}"


class Letter(models.Model):
    sender = models.ForeignKey(User, related_name="sent_letters", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_letters", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Letter {self.id}"


class LetterVersion(models.Model):
    letter = models.ForeignKey(Letter, on_delete=models.CASCADE, related_name="versions")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    
    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Version {self.id} (Letter {self.letter.id})"
