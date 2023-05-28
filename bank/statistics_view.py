from django.db.models import Sum
from django.utils import timezone

from dateutil.relativedelta import relativedelta
from rest_framework.views import APIView
from rest_framework.response import Response

from account.models import User
from ecopacket.models import LifeCycle
from .models import Earning, PayMe, PayOut


def get_month_name(num):
    return {
        1: "Yanvar",
        2: "Fevral",
        3: "Mart",
        4: "Aprel",
        5: "May",
        6: "Iyun",
        7: "Iyul",
        8: "Avgust",
        9: "Sentabr",
        10: "Oktabr",
        11: "Noyabr",
        12: "Dekabr",
    }[num]


def sum_amount(model, datetime):
    return (
        model.objects.filter(
            created_at__year=datetime.year, created_at__month=datetime.month
        ).aggregate(total=Sum("amount"))["total"]
        or 0
    )


def get_monthly_sums():
    current_datetime = timezone.now()

    monthly_sums = []

    for sup_month in range(12):
        dt = current_datetime - relativedelta(months=sup_month)

        monthly_earning = sum_amount(Earning, dt)

        monthly_payout = sum_amount(PayOut, dt)

        monthly_payme = sum_amount(PayMe, dt)

        monthly_sums.append(
            {
                "name": get_month_name(dt.month),
                "earning": monthly_earning,
                "payout": monthly_payout,
                "payme": monthly_payme,
            }
        )

    return monthly_sums[::-1]


def get_header_info():
    pops_count = User.objects.filter(role="POP").count()
    emps_count = User.objects.filter(role="EMP").count()
    earings_amount = Earning.objects.aggregate(sum=Sum("amount"))["sum"]
    orders_count = LifeCycle.objects.filter(filled_at=None, state__gt=80).count()

    return {
        "pops": pops_count,
        "emps": emps_count,
        "earnings": earings_amount,
        "orders": orders_count,
    }


def get_featured_data():
    current_datetime = timezone.now()
    payout = PayOut.objects.filter(
        created_at__year=current_datetime.year,
        created_at__month=current_datetime.month,
    ).aggregate(sum=Sum("amount")["sum"])
    all = PayMe.objects.filter(
        created_at__year=current_datetime.year,
        created_at__month=current_datetime.month,
    ).aggregate(sum=Sum("amount")["sum"])
    payed = PayMe.objects.filter(
        payed=True,
        created_at__year=current_datetime.year,
        created_at__month=current_datetime.month,
    ).aggregate(sum=Sum("amount")["sum"])
    return {
        "payed_percentage": round(payed / all * 100),
        "needed_to_pay": all - payed,
        "target": {"payme_request": all, "payme_payed": payed, "all_payed": payout},
    }


class DashboardView(APIView):
    def get(self, request):
        return Response(
            {
                "header_cards": get_header_info(),
                "chart_data": get_monthly_sums(),
                "featured": get_featured_data(),
            }
        )
