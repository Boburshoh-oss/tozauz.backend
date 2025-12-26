"""
Payme Subscribe API Service
Documentation: https://developer.help.paycom.uz/uz/subscribe-api-yordamida-tolovlarni-qabul-qilish
"""

import requests
import logging
from typing import Optional, Dict, Any
from django.conf import settings

logger = logging.getLogger(__name__)


class PaymeException(Exception):
    """Custom exception for Payme API errors"""

    def __init__(self, message: str, code: int = None, data: dict = None):
        self.message = message
        self.code = code
        self.data = data or {}
        super().__init__(self.message)


class PaymeService:
    """
    Payme Subscribe API integration service
    """

    # Test environment
    TEST_URL = "https://checkout.test.paycom.uz/api"
    # Production environment
    PROD_URL = "https://checkout.paycom.uz/api"

    def __init__(self):
        self.merchant_id = getattr(settings, "PAYME_MERCHANT_ID", "")
        self.merchant_key = getattr(settings, "PAYME_MERCHANT_KEY", "")
        self.is_test = getattr(settings, "PAYME_TEST_MODE", True)
        self.base_url = self.TEST_URL if self.is_test else self.PROD_URL

    def _get_auth_header(self, with_key: bool = False) -> str:
        """Generate X-Auth header"""
        if with_key:
            return f"{self.merchant_id}:{self.merchant_key}"
        return self.merchant_id

    def _make_request(
        self,
        method: str,
        params: Dict[str, Any],
        with_key: bool = False,
        request_id: int = 123,
    ) -> Dict[str, Any]:
        """
        Make JSON-RPC request to Payme API
        """
        headers = {
            "X-Auth": self._get_auth_header(with_key),
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
        }

        payload = {"id": request_id, "method": method, "params": params}

        try:
            response = requests.post(
                self.base_url, json=payload, headers=headers, timeout=30
            )
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                error = data["error"]
                raise PaymeException(
                    message=error.get("message", "Unknown error"),
                    code=error.get("code"),
                    data=error.get("data", {}),
                )

            return data.get("result", {})

        except requests.RequestException as e:
            logger.error(f"Payme API request failed: {str(e)}")
            raise PaymeException(f"Network error: {str(e)}")

    # ==================== CARD METHODS ====================

    def cards_create(
        self,
        card_number: str,
        card_expire: str,
        save: bool = True,
        customer: str = None,
    ) -> Dict[str, Any]:
        """
        Create card token
        cards.create method

        Args:
            card_number: Card number (16 digits)
            card_expire: Expiry date in format MMYY (e.g., "0399")
            save: If True, token can be used for recurring payments
            customer: Customer identifier (phone, email, uid)

        Returns:
            dict: Card info with token
        """
        params = {
            "card": {"number": card_number, "expire": card_expire},
            "save": save,
        }

        if customer:
            params["customer"] = customer

        result = self._make_request("cards.create", params)
        return result.get("card", {})

    def cards_get_verify_code(self, token: str) -> Dict[str, Any]:
        """
        Request SMS verification code
        cards.get_verify_code method

        Args:
            token: Card token from cards.create

        Returns:
            dict: {sent: bool, phone: str, wait: int}
        """
        params = {"token": token}
        return self._make_request("cards.get_verify_code", params)

    def cards_verify(self, token: str, code: str) -> Dict[str, Any]:
        """
        Verify card with SMS code
        cards.verify method

        Args:
            token: Card token
            code: SMS verification code (6 digits)

        Returns:
            dict: Updated card info with verify=true
        """
        params = {"token": token, "code": code}
        result = self._make_request("cards.verify", params)
        return result.get("card", {})

    def cards_check(self, token: str) -> Dict[str, Any]:
        """
        Check card status
        cards.check method

        Args:
            token: Card token

        Returns:
            dict: Card info (number, expire, token, recurrent, verify)
        """
        params = {"token": token}
        result = self._make_request("cards.check", params)
        return result.get("card", {})

    def cards_remove(self, token: str) -> bool:
        """
        Remove/delete card token
        cards.remove method

        Args:
            token: Card token to remove

        Returns:
            bool: True if successfully removed
        """
        params = {"token": token}
        result = self._make_request("cards.remove", params, with_key=True)
        return result.get("success", False)

    # ==================== RECEIPT METHODS ====================

    def receipts_create(
        self,
        amount: int,
        order_id: str,
        description: str = "",
    ) -> Dict[str, Any]:
        """
        Create payment receipt
        receipts.create method

        Args:
            amount: Amount in tiyin (1 sum = 100 tiyin)
            order_id: Unique order identifier
            description: Payment description

        Returns:
            dict: Receipt info with _id
        """
        # Fiscal receipt detail according to Payme documentation
        # detail = {
        #     "receipt_type": 0,  # 0 = Продажа (Sale)
        #     "items": [
        #         {
        #             "title": "Автоматизированная депозитная машина",
        #             "price": amount,  # Price per unit in tiyin
        #             "count": 1,
        #             "code": "08472001009000000",  # IKPU code
        #             "vat_percent": 0,  # VAT percentage
        #             "package_code": "1495043",  # Package code
        #         }
        #     ],
        # }

        params = {
            "amount": amount,
            "account": {"order_id": str(order_id)},
        }

        if description:
            params["description"] = description

        result = self._make_request("receipts.create", params, with_key=True)
        return result.get("receipt", {})

    def receipts_pay(
        self,
        receipt_id: str,
        token: str,
        payer_phone: str = None,
        hold: bool = False,
    ) -> Dict[str, Any]:
        """
        Pay receipt with card token
        receipts.pay method

        Args:
            receipt_id: Receipt _id from receipts.create
            token: Card token
            payer_phone: Optional payer phone for antifraud
            hold: If True, use hold payment

        Returns:
            dict: Updated receipt info
        """
        params = {"id": receipt_id, "token": token}

        if payer_phone:
            params["payer"] = {"phone": payer_phone}

        if hold:
            params["hold"] = True

        result = self._make_request("receipts.pay", params, with_key=True)
        return result.get("receipt", {})

    def receipts_send(self, receipt_id: str, phone: str) -> bool:
        """
        Send receipt via SMS
        receipts.send method

        Args:
            receipt_id: Receipt _id
            phone: Phone number to send SMS

        Returns:
            bool: True if successfully sent
        """
        params = {"id": receipt_id, "phone": phone}
        result = self._make_request("receipts.send", params, with_key=True)
        return result.get("success", False)

    def receipts_check(self, receipt_id: str) -> int:
        """
        Check receipt state
        receipts.check method

        Args:
            receipt_id: Receipt _id

        Returns:
            int: Receipt state (0-input, 4-paid, 50-cancelled)
        """
        params = {"id": receipt_id}
        result = self._make_request("receipts.check", params, with_key=True)
        return result.get("state")

    def receipts_get(self, receipt_id: str) -> Dict[str, Any]:
        """
        Get receipt details
        receipts.get method

        Args:
            receipt_id: Receipt _id

        Returns:
            dict: Full receipt info
        """
        params = {"id": receipt_id}
        result = self._make_request("receipts.get", params, with_key=True)
        return result.get("receipt", {})

    def receipts_cancel(self, receipt_id: str) -> Dict[str, Any]:
        """
        Cancel receipt
        receipts.cancel method

        Args:
            receipt_id: Receipt _id

        Returns:
            dict: Cancelled receipt info
        """
        params = {"id": receipt_id}
        result = self._make_request("receipts.cancel", params, with_key=True)
        return result.get("receipt", {})

    def receipts_confirm_hold(self, receipt_id: str) -> Dict[str, Any]:
        """
        Confirm hold payment (capture funds)
        receipts.confirm_hold method

        Args:
            receipt_id: Receipt _id with hold

        Returns:
            dict: Confirmed receipt info
        """
        params = {"id": receipt_id}
        result = self._make_request("receipts.confirm_hold", params, with_key=True)
        return result.get("receipt", {})

    def receipts_get_all(
        self,
        count: int = 50,
        from_timestamp: int = None,
        to_timestamp: int = None,
        offset: int = 0,
    ) -> list:
        """
        Get all receipts
        receipts.get_all method

        Args:
            count: Number of receipts (max 50)
            from_timestamp: Start date timestamp
            to_timestamp: End date timestamp
            offset: Skip count

        Returns:
            list: List of receipts
        """
        params = {"count": min(count, 50), "offset": offset}

        if from_timestamp:
            params["from"] = from_timestamp
        if to_timestamp:
            params["to"] = to_timestamp

        return self._make_request("receipts.get_all", params, with_key=True)


# Singleton instance
payme_service = PaymeService()
