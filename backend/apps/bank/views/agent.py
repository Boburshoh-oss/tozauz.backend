from rest_framework import generics, permissions
from django.db.models import Sum
from django_filters import rest_framework as filters
from ..models import Earning, Application
from ..serializers import EarningListSerializer, ApplicationCreateSerializer, ApplicationListSerializer, ApplicationUpdateSerializer
from ..filters import EarningFilter
from apps.utils.pagination import MyPagination

# agent earnings list
class AgentEarningListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EarningListSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = EarningFilter
    pagination_class = MyPagination
    
    def get_queryset(self):
        queryset = Earning.objects.all().order_by('-created_at')
        return queryset
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        
        # Calculate total amount for filtered results
        filtered_queryset = self.filter_queryset(self.get_queryset())
        total_amount = filtered_queryset.aggregate(
            total=Sum('amount'),
            total_penalty=Sum('penalty_amount')
        )
        
        response.data['total_amount'] = total_amount['total'] or 0
        response.data['total_penalty'] = total_amount['total_penalty'] or 0
        
        return response

class ApplicationCreateView(generics.CreateAPIView):
    serializer_class = ApplicationCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(agent=self.request.user)
    
class AgentApplicationListAPIView(generics.ListAPIView):
    serializer_class = ApplicationListSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MyPagination
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['status', 'employee', 'box']
    
    def get_queryset(self):
        queryset = Application.objects.filter(agent=self.request.user).order_by('-created_at')
        return queryset
    
class AgentApplicationUpdateAPIView(generics.UpdateAPIView):
    serializer_class = ApplicationUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Application.objects.all()
    lookup_field = 'pk'
    
    def get_queryset(self):
        queryset = Application.objects.filter(agent=self.request.user).order_by('-created_at')
        return queryset
