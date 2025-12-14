from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Letter, ModificationRequest
from .serializers import LetterSerializer, ModificationRequestSerializer
from .permissions import IsSenderOrReceiver


class LetterViewSet(viewsets.ModelViewSet):
    serializer_class = LetterSerializer
    permission_classes = [IsSenderOrReceiver]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Letter.objects.none()
        return Letter.objects.filter(sender=user) | Letter.objects.filter(receiver=user)

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class ModificationRequestViewSet(viewsets.ModelViewSet):
    serializer_class = ModificationRequestSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return ModificationRequest.objects.none()
        return ModificationRequest.objects.filter(
            letter__sender=user
        ) | ModificationRequest.objects.filter(
            letter__receiver=user
        )

    def perform_create(self, serializer):
        serializer.save(requested_by=self.request.user)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        mod = self.get_object()

        # Only the SENDER of the letter can approve the modification
        if request.user != mod.letter.sender: # <-- CORRECTED AUTH
            return Response(
                {"detail": "Only the letter sender can approve this modification."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Use the model's approve method to handle versioning
        if mod.status == 'PENDING':
            mod.approve() 
            return Response({'status': 'APPROVED'})

        return Response(
            {"detail": f"Modification is already {mod.status}."},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        mod = self.get_object()

        # Only the SENDER of the letter can reject the modification
        if request.user != mod.letter.sender: # <-- CORRECTED AUTH
            return Response(
                {"detail": "Only the letter sender can reject this modification."},
                status=status.HTTP_403_FORBIDDEN
            )

        if mod.status == 'PENDING':
            mod.status = 'REJECTED'
            mod.save()
            return Response({'status': 'REJECTED'})

        return Response(
            {"detail": f"Modification is already {mod.status}."},
            status=status.HTTP_400_BAD_REQUEST
        )