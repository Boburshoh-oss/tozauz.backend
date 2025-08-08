from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

from apps.ecopacket.models import Box, FlaskQrCode
from apps.account.models import User
from apps.bank.models import Earning

class FlaskQrManualMultipleView(APIView):
    def post(self, request, format=None):
        bar_codes = request.data.get("bar_codes", [])
        sim_module = request.data.get("sim_module")
        phone_number = request.data.get("phone_number")

        if not isinstance(bar_codes, list):
            return Response(
                {"error": "bar_codes must be a list"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not bar_codes:
            return Response(
                {"error": "bar_codes list is empty"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            box = Box.objects.get(sim_module=sim_module, fandomat=True)
        except Box.DoesNotExist:
            return Response(
                {"error": "Fandomat box doesn't exist!"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response(
                {"error": "Phone number doesn't exist!"},
                status=status.HTTP_404_NOT_FOUND,
            )

        client_bank_account = user.bankaccount
        total_amount = 0
        processed_barcodes = {"success": [], "error": []}

        for bar_code in bar_codes:
            try:
                flask_qr = FlaskQrCode.objects.get(bar_code=bar_code)
                
                # Kategoriyani olish
                category = flask_qr.category
                if not category:
                    processed_barcodes["error"].append({
                        "bar_code": bar_code,
                        "error": "Category not found"
                    })
                    continue

                # Pul hisob-kitobi
                money_amount = category.summa

                # Kategoriya ignore_agent=True bo'lsa, hamma pul foydalanuvchiga beriladi
                if category.ignore_agent:
                    client_bank_account.capital += money_amount
                    
                    # Foydalanuvchi uchun daromad yozib qo'yiladi
                    Earning.objects.create(
                        bank_account=client_bank_account,
                        amount=money_amount,
                        tarrif=category.name,
                        box=box,
                    )
                else:
                    # Agar ignore_agent=False bo'lsa, odatiy hisob-kitob
                    # seller ulushini hisoblash
                    seller_percentage = box.seller_percentage
                    if box.seller is not None:
                        seller_share = money_amount * seller_percentage / 100
                        client_share = money_amount - seller_share
                        
                        # Seller hisobiga o'tkazish
                        bank_account_seller = box.seller.bankaccount
                        bank_account_seller.capital += seller_share
                        bank_account_seller.save()
                        
                        Earning.objects.create(
                            bank_account=bank_account_seller,
                            amount=seller_share,
                            tarrif=category.name,
                            box=box,
                        )
                        
                        # Box da seller ulushini saqlash
                        box.seller_share += seller_share
                        box.save()

                        # Client hisobiga client ulushini o'tkazish
                        client_bank_account.capital += client_share
                        
                        Earning.objects.create(
                            bank_account=client_bank_account,
                            amount=client_share,
                            tarrif=category.name,
                            box=box,
                        )
                    else:
                        # Seller bo'lmasa hamma summa clientga
                        client_bank_account.capital += money_amount
                        
                        Earning.objects.create(
                            bank_account=client_bank_account,
                            amount=money_amount,
                            tarrif=category.name,
                            box=box,
                        )
                
                total_amount += money_amount
                processed_barcodes["success"].append({
                    "bar_code": bar_code,
                    "amount": money_amount
                })

            except FlaskQrCode.DoesNotExist:
                processed_barcodes["error"].append({
                    "bar_code": bar_code,
                    "error": "Invalid barcode"
                })

        # Save client bank account after all transactions
        client_bank_account.save()

        return Response({
            "total_amount": total_amount,
            "processed_barcodes": processed_barcodes,
            "success_count": len(processed_barcodes["success"]),
            "error_count": len(processed_barcodes["error"])
        }, status=status.HTTP_202_ACCEPTED)


