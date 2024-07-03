from django.db import IntegrityError
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.ecopacket.models import EcoPacketQrCode
from apps.packet.models import Category, Packet
from .qr_code_generator import get_uid

def create_ecopacket_qr_codes(num_of_qrcodes, category):
    # create a list of EcopacketQrCodes objects
    cat = Category.objects.get(id=category)
    qrcodes = [EcoPacketQrCode() for _ in range(num_of_qrcodes)]

    # set the created_at field to the current time for all objects
    now = timezone.now()
    for qr in qrcodes:
        qr.created_at = now
        qr.category = cat
        qr.qr_code = get_uid("eco")
    try:
        # use bulk_create to create all the objects in a single query
        qr_codes = EcoPacketQrCode.objects.bulk_create(qrcodes)
        return qr_codes
    except (IntegrityError, ValidationError):
        return []


def create_packet_qr_codes(num_of_qrcodes, category):
    # create a list of EcopacketQrCodes objects
    cat = Category.objects.get(id=category)
    qrcodes = [Packet() for _ in range(num_of_qrcodes)]

    start_with = cat.name
    
    # set the created_at field to the current time for all objects
    now = timezone.now()
    for qr in qrcodes:
        qr.created_at = now
        qr.category = cat
        qr.qr_code = get_uid(start_with[0:3])

    try:
        # use bulk_create to create all the objects in a single query
        qr_codes = Packet.objects.bulk_create(qrcodes)
        return qr_codes
    except (IntegrityError, ValidationError):
        return []
