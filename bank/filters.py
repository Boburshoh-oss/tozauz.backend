import django_filters
from .models import Earning


class EarningFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(
        field_name='created_at', lookup_expr='gte')
    end_date = django_filters.DateFilter(
        field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Earning
        fields = ['start_date', 'end_date']
