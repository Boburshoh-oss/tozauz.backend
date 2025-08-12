from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from apps.ecopacket.models import Box
from apps.ecopacket.serializers.serializers import AgentBoxSerializer
class AgentBoxRetrieveView(generics.RetrieveAPIView):
   queryset = Box.objects.all()
   serializer_class = AgentBoxSerializer
   permission_classes = [IsAuthenticated]
#    lookup_field = 'sim_module'  # This allows us to lookup by sim_module instead of id