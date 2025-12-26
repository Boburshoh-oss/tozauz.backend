import django_filters
from .models import PaymeCard, PaymeReceipt, PaymeTransaction


class PaymeCardFilter(django_filters.FilterSet):
    """Filter for PaymeCard list endpoint"""

    is_verified = django_filters.BooleanFilter(field_name="is_verified")
    is_recurrent = django_filters.BooleanFilter(field_name="is_recurrent")
    created_at_from = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_at_to = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )

    class Meta:
        model = PaymeCard
        fields = ["is_verified", "is_recurrent"]


class PaymeReceiptFilter(django_filters.FilterSet):
    """Filter for PaymeReceipt list endpoint"""

    state = django_filters.NumberFilter(field_name="state")
    order_id = django_filters.CharFilter(field_name="order_id", lookup_expr="icontains")
    amount_min = django_filters.NumberFilter(field_name="amount", lookup_expr="gte")
    amount_max = django_filters.NumberFilter(field_name="amount", lookup_expr="lte")
    created_at_from = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_at_to = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )
    is_paid = django_filters.BooleanFilter(method="filter_is_paid")

    class Meta:
        model = PaymeReceipt
        fields = ["state", "order_id"]

    def filter_is_paid(self, queryset, name, value):
        if value:
            return queryset.filter(state=4)  # PAID state
        return queryset.exclude(state=4)


class PaymeTransactionFilter(django_filters.FilterSet):
    """Filter for PaymeTransaction list endpoint"""

    transaction_type = django_filters.ChoiceFilter(
        field_name="transaction_type",
        choices=PaymeTransaction.TransactionType.choices,
    )
    is_success = django_filters.BooleanFilter(field_name="is_success")
    created_at_from = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_at_to = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )

    class Meta:
        model = PaymeTransaction
        fields = ["transaction_type", "is_success"]
