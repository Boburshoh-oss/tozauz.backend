from django_filters import rest_framework as filters
from .models import Earning

class EarningFilter(filters.FilterSet):
    start_date = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='created_at', lookup_expr='lte')
    min_amount = filters.NumberFilter(field_name='amount', lookup_expr='gte')
    max_amount = filters.NumberFilter(field_name='amount', lookup_expr='lte')

    class Meta:
        model = Earning
        fields = {
            'tarrif': ['exact', 'icontains'],
            'is_penalty': ['exact'],
            'box__name': ['exact', 'icontains'],
            'packet__qr_code': ['exact', 'icontains'],
            'bank_account__user__first_name': ['exact', 'icontains'],
            'bank_account__user__phone_number': ['exact', 'icontains']
        }
