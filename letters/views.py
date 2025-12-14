from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Letter, ModificationRequest
from .serializers import LetterSerializer, ModificationRequestSerializer
from .permissions import IsSenderOrReceiver


class LetterViewSet(viewsets.ModelViewSet): # cite: uploaded:views.py
    serializer_class = LetterSerializer # cite: uploaded:views.py
    permission_classes = [IsSenderOrReceiver] # cite: uploaded:views.py

    def get_queryset(self): # cite: uploaded:views.py
        user = self.request.user
        if not user.is_authenticated:
            return Letter.objects.none()
        return Letter.objects.filter(sender=user) | Letter.objects.filter(receiver=user) # cite: uploaded:views.py

    def perform_create(self, serializer): # cite: uploaded:views.py
        serializer.save(sender=self.request.user) # cite: uploaded:views.py


class ModificationRequestViewSet(viewsets.ModelViewSet): # cite: uploaded:views.py
    serializer_class = ModificationRequestSerializer # cite: uploaded:views.py

    def get_queryset(self): # cite: uploaded:views.py
        user = self.request.user
        if not user.is_authenticated:
            return ModificationRequest.objects.none()
        return ModificationRequest.objects.filter( # cite: uploaded:views.py
            letter__sender=user
        ) | ModificationRequest.objects.filter(
            letter__receiver=user
        )

    def perform_create(self, serializer): # cite: uploaded:views.py
        serializer.save(requested_by=self.request.user) # cite: uploaded:views.py

    @action(detail=True, methods=['post']) # cite: uploaded:views.py
    def approve(self, request, pk=None): # cite: uploaded:views.py
        mod = self.get_object()

        # Only the SENDER of the letter can approve the modification
        if request.user != mod.letter.sender: # cite: uploaded:views.py
            return Response(
                {"detail": "Only the letter sender can approve this modification."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Use the model's approve method to handle versioning
        if mod.status == 'PENDING': # cite: uploaded:views.py
            mod.approve() 
            return Response({'status': 'APPROVED'})

        return Response( # cite: uploaded:views.py
            {"detail": f"Modification is already {mod.status}."},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post']) # cite: uploaded:views.py
    def reject(self, request, pk=None): # cite: uploaded:views.py
        mod = self.get_object()

        # Only the SENDER of the letter can reject the modification
        if request.user != mod.letter.sender: # cite: uploaded:views.py
            return Response(
                {"detail": "Only the letter sender can reject this modification."},
                status=status.HTTP_403_FORBIDDEN
            )

        if mod.status == 'PENDING': # cite: uploaded:views.py
            mod.status = 'REJECTED' # cite: uploaded:views.py
            mod.save()
            return Response({'status': 'REJECTED'}) # cite: uploaded:views.py

        return Response(
            {"detail": f"Modification is already {mod.status}."},
            status=status.HTTP_400_BAD_REQUEST
        )