from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserConnection(models.Model): # cite: uploaded:models.py
    STATUS_CHOICES = ( # cite: uploaded:models.py
        ("PENDING", "Pending"),
        ("ACCEPTED", "Accepted"),
    )

    requester = models.ForeignKey( # cite: uploaded:models.py
        User, related_name="sent_requests", on_delete=models.CASCADE
    )
    receiver = models.ForeignKey( # cite: uploaded:models.py
        User, related_name="received_requests", on_delete=models.CASCADE
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING") # cite: uploaded:models.py

    class Meta: # cite: uploaded:models.py
        # Ensures a user can't send the same request twice
        unique_together = ("requester", "receiver") # cite: uploaded:models.py

    def __str__(self): # cite: uploaded:models.py
        return f"{self.requester} → {self.receiver} ({self.status})" # cite: uploaded:models.py


class Letter(models.Model): # cite: uploaded:models.py
    sender = models.ForeignKey( # cite: uploaded:models.py
        User, related_name="sent_letters", on_delete=models.CASCADE
    )
    receiver = models.ForeignKey( # cite: uploaded:models.py
        User, related_name="received_letters", on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True) # cite: uploaded:models.py

    def approved_version(self): # cite: uploaded:models.py
        """
        Returns the latest approved version of this letter.
        """
        return ( # cite: uploaded:models.py
            self.versions.filter(is_approved=True)
            .order_by("-created_at")
            .first()
        )

    def pending_modifications(self): # cite: uploaded:models.py
        """
        Returns True if there are any pending modification requests for this letter.
        """
        return self.modification_requests.filter(status="PENDING").exists() # cite: uploaded:models.py

    def __str__(self): # cite: uploaded:models.py
        return f"Letter from {self.sender} to {self.receiver} ({self.created_at.date()})" # cite: uploaded:models.py


class LetterVersion(models.Model): # cite: uploaded:models.py
    letter = models.ForeignKey( # cite: uploaded:models.py
        Letter, related_name="versions", on_delete=models.CASCADE
    )
    content = models.TextField() # cite: uploaded:models.py

    created_by = models.ForeignKey( # cite: uploaded:models.py
        User, on_delete=models.CASCADE
    )

    is_approved = models.BooleanField(default=False) # cite: uploaded:models.py

    created_at = models.DateTimeField(auto_now_add=True) # cite: uploaded:models.py

    def __str__(self): # cite: uploaded:models.py
        status = "APPROVED" if self.is_approved else "PENDING"
        return f"Version of Letter #{self.letter.id} ({status})" # cite: uploaded:models.py


class ModificationRequest(models.Model): # cite: uploaded:models.py
    STATUS_CHOICES = ( # cite: uploaded:models.py
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    )

    letter = models.ForeignKey( # cite: uploaded:models.py
        Letter, related_name="modification_requests", on_delete=models.CASCADE
    )

    requested_by = models.ForeignKey(User, on_delete=models.CASCADE) # cite: uploaded:models.py

    proposed_content = models.TextField() # cite: uploaded:models.py

    status = models.CharField( # cite: uploaded:models.py
        max_length=10, choices=STATUS_CHOICES, default="PENDING"
    )

    requested_at = models.DateTimeField(auto_now_add=True) # cite: uploaded:models.py
    approved_at = models.DateTimeField(null=True, blank=True) # cite: uploaded:models.py

    def approve(self): # cite: uploaded:models.py
        """
        Approves this modification and creates a new approved LetterVersion.
        """
        self.status = "APPROVED" # cite: uploaded:models.py
        self.approved_at = timezone.now() # cite: uploaded:models.py
        self.save() # cite: uploaded:models.py
        
        LetterVersion.objects.create( # cite: uploaded:models.py
            letter=self.letter,
            content=self.proposed_content,
            created_by=self.requested_by,
            is_approved=True
        )

    def __str__(self): # cite: uploaded:models.py
        return f"Mod Request for Letter #{self.letter.id} by {self.requested_by} ({self.status})" # cite: uploaded:models.py