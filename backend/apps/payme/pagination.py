from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict


class PaymePagination(PageNumberPagination):
    """
    Professional pagination class for Payme API endpoints.

    Features:
    - Customizable page size via query parameter
    - Detailed pagination metadata in response
    - Ordering support
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100
    page_query_param = "page"

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("success", True),
                    ("count", self.page.paginator.count),
                    ("total_pages", self.page.paginator.num_pages),
                    ("current_page", self.page.number),
                    ("page_size", self.get_page_size(self.request)),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            )
        )

    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "properties": {
                "success": {
                    "type": "boolean",
                    "example": True,
                },
                "count": {
                    "type": "integer",
                    "example": 100,
                    "description": "Jami elementlar soni",
                },
                "total_pages": {
                    "type": "integer",
                    "example": 10,
                    "description": "Jami sahifalar soni",
                },
                "current_page": {
                    "type": "integer",
                    "example": 1,
                    "description": "Hozirgi sahifa raqami",
                },
                "page_size": {
                    "type": "integer",
                    "example": 10,
                    "description": "Har sahifadagi elementlar soni",
                },
                "next": {
                    "type": "string",
                    "nullable": True,
                    "format": "uri",
                    "example": "http://api.example.org/accounts/?page=2",
                    "description": "Keyingi sahifa URL",
                },
                "previous": {
                    "type": "string",
                    "nullable": True,
                    "format": "uri",
                    "example": "http://api.example.org/accounts/?page=1",
                    "description": "Oldingi sahifa URL",
                },
                "results": schema,
            },
        }


class SmallPagination(PaymePagination):
    """Small pagination for limited results"""

    page_size = 5
    max_page_size = 20


class LargePagination(PaymePagination):
    """Large pagination for bulk results"""

    page_size = 25
    max_page_size = 200
