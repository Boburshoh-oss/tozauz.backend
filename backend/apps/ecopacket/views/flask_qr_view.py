from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

from apps.ecopacket.models import Box, FlaskQrCode, EcoPacketQrCode
from apps.account.models import User
from apps.bank.models import Earning

class FlaskQrManualMultipleView(APIView):
    """
    Fandomat qutisi uchun ko'p miqdordagi flask QR kodlarini qayta ishlash API'si.
    
    Bu API bir nechta flask QR kodlarini bir vaqtda qayta ishlash imkonini beradi.
    Har bir QR kod uchun kategoriyaga qarab pul miqdori hisoblanadi va 
    foydalanuvchi hamda seller (mavjud bo'lsa) hisoblariga taqsimlanadi.
    """
    
    def post(self, request, format=None):
        """
        Ko'p miqdordagi flask QR kodlarni qayta ishlash.

        Args:
            request data:
            {
                "bar_codes": [                  # Majburiy. Flask QR kodlar ro'yxati
                    "barcode1",
                    "barcode2",
                    ...
                ],
                "sim_module": "string",         # Majburiy. Fandomat qutisining SIM moduli
                "phone_number": "string"        # Majburiy. Foydalanuvchi telefon raqami
            }

        Returns:
            {
                "total_amount": float,          # Jami hisoblangan summa
                "processed_barcodes": {
                    "success": [                # Muvaffaqiyatli qayta ishlangan QR kodlar
                        {
                            "bar_code": "string",
                            "amount": float
                        },
                        ...
                    ],
                    "error": [                  # Xatolik yuzaga kelgan QR kodlar
                        {
                            "bar_code": "string",
                            "error": "string"
                        },
                        ...
                    ]
                },
                "success_count": int,           # Muvaffaqiyatli QR kodlar soni
                "error_count": int              # Xatolik yuzaga kelgan QR kodlar soni
            }

        Raises:
            400 Bad Request:
                - bar_codes list emas
                - bar_codes bo'sh ro'yxat
            404 Not Found:
                - Fandomat topilmadi
                - Foydalanuvchi topilmadi
                - QR kod topilmadi
                - Kategoriya topilmadi
        """
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
            box = Box.objects.get(sim_module=sim_module)
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


class FlaskQrManualSingleView(APIView):
    """
    Fandomat qutisi uchun bitta flask QR kodini qayta ishlash API'si.
    
    Bu API bitta flask QR kodini qayta ishlash imkonini beradi.
    QR kod uchun kategoriyaga qarab pul miqdori hisoblanadi va 
    foydalanuvchi hamda seller (mavjud bo'lsa) hisoblariga taqsimlanadi.
    """
    
    def post(self, request, format=None):
        """
        Bitta flask QR kodini qayta ishlash.

        Args:
            request data:
            {
                "bar_code": "string",           # Majburiy. Flask QR kod
                "sim_module": "string",         # Majburiy. Fandomat qutisining SIM moduli
                "phone_number": "string"        # Majburiy. Foydalanuvchi telefon raqami
            }

        Returns:
            {
                "success": true,                # Muvaffaqiyatli bajarildi
                "amount": float,                # Hisoblangan summa
                "bar_code": "string",           # Qayta ishlangan bar code
                "filter_type": "string"         # Kategoriya filter type'i
            }

        Raises:
            400 Bad Request:
                - bar_code kiritilmagan
            404 Not Found:
                - Fandomat topilmadi
                - Foydalanuvchi topilmadi
                - QR kod topilmadi
                - Kategoriya topilmadi
        """
        bar_code = request.data.get("bar_code")
        sim_module = request.data.get("sim_module")
        phone_number = request.data.get("phone_number")

        if not bar_code:
            return Response(
                {"error": "bar_code is required"},
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

        try:
            flask_qr = FlaskQrCode.objects.get(bar_code=bar_code)
        except FlaskQrCode.DoesNotExist:
            return Response(
                {"error": "Invalid barcode!"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Kategoriyani olish
        category = flask_qr.category
        if not category:
            return Response(
                {"error": "Category not found for this barcode"},
                status=status.HTTP_404_NOT_FOUND,
            )

        client_bank_account = user.bankaccount
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


        # Client bank account'ni saqlash
        client_bank_account.save()

        return Response({
            "success": True,
            "amount": money_amount,
            "bar_code": bar_code,
            "filter_type": category.filter_type
        }, status=status.HTTP_202_ACCEPTED)


class UniversalQrManualSingleView(APIView):
    """
    Universal QR kodini qayta ishlash API'si.
    
    Bu API ham EcoPacket QR kodlar, ham Flask QR kodlar bilan ishlaydi.
    QR kod tipini avtomatik aniqlaydi va tegishli logikani qo'llaydi.
    """
    
    def post(self, request, format=None):
        """
        Bitta QR kodini qayta ishlash (EcoPacket yoki Flask).

        Args:
            request data:
            {
                "qr_code": "string",            # Majburiy. QR kod yoki bar_code
                "sim_module": "string",         # Majburiy. Box SIM moduli
                "phone_number": "string"        # Majburiy. Foydalanuvchi telefon raqami
            }

        Returns:
            {
                "success": true,                # Muvaffaqiyatli bajarildi
                "amount": float,                # Hisoblangan summa
                "qr_code": "string",            # Qayta ishlangan QR kod
                "filter_type": "string",        # Kategoriya filter type'i
                "qr_type": "string"             # QR kod tipi ("ecopacket" yoki "flask")
            }
        """
        qr_code = request.data.get("qr_code")
        sim_module = request.data.get("sim_module")
        phone_number = request.data.get("phone_number")

        if not qr_code:
            return Response(
                {"error": "qr_code is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response(
                {"error": "Phone number doesn't exist!"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Avval EcoPacket QR kodini tekshiramiz
        ecopacket_qr = EcoPacketQrCode.objects.filter(qr_code=qr_code).first()
        flask_qr = FlaskQrCode.objects.filter(bar_code=qr_code).first()

        if ecopacket_qr:
            # EcoPacket QR kod logikasi
            try:
                box = Box.objects.get(sim_module=sim_module)
            except Box.DoesNotExist:
                return Response(
                    {"error": "Box doesn't exist!"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if ecopacket_qr.scannered_at is not None:
                return Response(
                    {"error": "This QR code has already been used"},
                    status=status.HTTP_409_CONFLICT,
                )

            # QR kodini qayta ishlash
            last_lifecycle = box.lifecycle.last()
            ecopacket_qr.scannered_at = timezone.now()
            ecopacket_qr.life_cycle = last_lifecycle
            ecopacket_qr.user = user
            ecopacket_qr.save()

            money_amount = ecopacket_qr.category.summa
            category = ecopacket_qr.category
            client_bank_account = user.bankaccount

            # Kategoriya ignore_agent=True bo'lsa, hamma pul foydalanuvchiga beriladi
            if category.ignore_agent:
                client_bank_account.capital += money_amount
                
                Earning.objects.create(
                    bank_account=client_bank_account,
                    amount=money_amount,
                    tarrif=category.name,
                    box=box,
                )
            else:
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

            client_bank_account.save()

            return Response({
                "success": True,
                "amount": money_amount,
                "qr_code": qr_code,
                "filter_type": category.filter_type,
                "qr_type": "ecopacket"
            }, status=status.HTTP_202_ACCEPTED)

        elif flask_qr:
            # Flask QR kod logikasi
            try:
                box = Box.objects.get(sim_module=sim_module)
            except Box.DoesNotExist:
                return Response(
                    {"error": "Fandomat box doesn't exist!"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Kategoriyani olish
            category = flask_qr.category
            if not category:
                return Response(
                    {"error": "Category not found for this barcode"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            client_bank_account = user.bankaccount
            money_amount = category.summa

            # Kategoriya ignore_agent=True bo'lsa, hamma pul foydalanuvchiga beriladi
            if category.ignore_agent:
                client_bank_account.capital += money_amount
                
                Earning.objects.create(
                    bank_account=client_bank_account,
                    amount=money_amount,
                    tarrif=category.name,
                    box=box,
                )
            else:
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
  

            client_bank_account.save()

            return Response({
                "success": True,
                "amount": money_amount,
                "qr_code": qr_code,
                "filter_type": category.filter_type,
                "qr_type": "flask"
            }, status=status.HTTP_202_ACCEPTED)

        else:
            # QR kod topilmadi
            return Response(
                {"error": "QR code not found in any system!"},
                status=status.HTTP_404_NOT_FOUND,
            )


class UniversalQrCheckView(APIView):
    """
    QR kod yoki barcodeni bazada mavjudligini tekshirish API'si.
    
    Bu API QR kod yoki barcodeni bazada mavjudligini tekshiradi va 
    topilganda uning ma'lumotlarini qaytaradi.
    Hech qanday operatsiya bajarmaydi, faqat ma'lumot beradi.
    """
    
    def get(self, request, format=None):
        """
        QR kod yoki barcodeni bazada tekshirish.

        Query Parameters:
            qr_code (string): Tekshiriladigan QR kod yoki barcode

        Returns:
            {
                "exists": true,                 # QR kod mavjudligi
                "qr_type": "string",           # QR kod tipi ("ecopacket" yoki "flask")
                "data": {                      # QR kod ma'lumotlari
                    "qr_code": "string",       # QR kod/barcode
                    "category": {
                        "name": "string",
                        "summa": float,
                        "filter_type": "string",
                        "ignore_agent": boolean
                    },
                    "is_used": boolean         # Faqat EcoPacket uchun
                }
            }

        Raises:
            400 Bad Request:
                - qr_code kiritilmagan
            404 Not Found:
                - QR kod topilmadi
        """
        qr_code = request.query_params.get("qr_code")

        if not qr_code:
            return Response(
                {"error": "qr_code parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Avval EcoPacket QR kodini tekshiramiz
        ecopacket_qr = EcoPacketQrCode.objects.filter(qr_code=qr_code).first()
        flask_qr = FlaskQrCode.objects.filter(bar_code=qr_code).first()

        if ecopacket_qr:
            # EcoPacket QR kod topildi
            category = ecopacket_qr.category
            return Response({
                "exists": True,
                "qr_type": "ecopacket",
                "data": {
                    "qr_code": qr_code,
                    "category": {
                        "name": category.name,
                        "summa": category.summa,
                        "filter_type": category.filter_type,
                        "ignore_agent": category.ignore_agent
                    },
                    "is_used": ecopacket_qr.scannered_at is not None
                }
            }, status=status.HTTP_200_OK)

        elif flask_qr:
            # Flask QR kod topildi
            category = flask_qr.category
            if not category:
                return Response(
                    {"error": "Category not found for this barcode"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            
            return Response({
                "exists": True,
                "qr_type": "flask",
                "data": {
                    "qr_code": qr_code,
                    "category": {
                        "name": category.name,
                        "summa": category.summa,
                        "filter_type": category.filter_type,
                        "ignore_agent": category.ignore_agent
                    },
                    "is_used": False  # Flask QR kodlar uchun doimo False
                }
            }, status=status.HTTP_200_OK)

        else:
            # QR kod topilmadi
            return Response({
                "exists": False,
                "message": "QR code not found in any system"
            }, status=status.HTTP_404_NOT_FOUND)


