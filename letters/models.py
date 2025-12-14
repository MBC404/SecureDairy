from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserConnection(models.Model):
    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("ACCEPTED", "Accepted"),
    )

    requester = models.ForeignKey(
        User, related_name="sent_requests", on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        User, related_name="received_requests", on_delete=models.CASCADE
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")

    class Meta:
        unique_together = ("requester", "receiver")

    def __str__(self):
        return f"{self.requester} → {self.receiver} ({self.status})"


class Letter(models.Model):
    sender = models.ForeignKey(
        User, related_name="sent_letters", on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        User, related_name="received_letters", on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def approved_version(self):
        """
        Returns the latest approved version of this letter.
        SAFE for templates.
        """
        return (
            self.versions.filter(is_approved=True)
            .order_by("-created_at")
            .first()
        )
    def has_pending_modifications(self):
        """
        Returns True if there is at least one PENDING modification request.
        """
        return self.modification_requests.filter(status="PENDING").exists()

    def __str__(self):
        return f"Letter #{self.id} from {self.sender} to {self.receiver}"


class LetterVersion(models.Model):
    letter = models.ForeignKey(
        Letter, related_name="versions", on_delete=models.CASCADE
    )

    content = models.TextField()

    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE
    )

    is_approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "APPROVED" if self.is_approved else "PENDING"
        return f"Version of Letter #{self.letter.id} ({status})"


class ModificationRequest(models.Model):
    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"), # <-- NEW: Added REJECTED status
    )

    letter = models.ForeignKey(
        Letter, related_name="modification_requests", on_delete=models.CASCADE
    )

    requested_by = models.ForeignKey(User, on_delete=models.CASCADE)

    proposed_content = models.TextField()

    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="PENDING"
    )

    requested_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    def approve(self):
        """
        Approves this modification and creates a new approved LetterVersion.
        """
        LetterVersion.objects.create(
            letter=self.letter,
            content=self.proposed_content,
            created_by=self.requested_by,
            is_approved=True,
        )

        self.status = "APPROVED"
        self.approved_at = timezone.now()
        self.save()

    def __str__(self):
        return f"Modification for Letter #{self.letter.id} ({self.status})"