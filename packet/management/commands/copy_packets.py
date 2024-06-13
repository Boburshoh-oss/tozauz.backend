# your_app/management/commands/copy_packets.py

from django.core.management.base import BaseCommand
from packet.models import Packet
from ecopacket.models import EcoPacketQrCode

class Command(BaseCommand):
    help = 'Copy all data from Packet model to EcoPacketQrCode model'

    def handle(self, *args, **kwargs):
        packets = Packet.objects.all()
        for packet in packets:
            EcoPacketQrCode.objects.create(
                qr_code=packet.qr_code,
                category=packet.category,
            )
        self.stdout.write(self.style.SUCCESS('Successfully copied all data from Packet to EcoPacketQrCode'))
