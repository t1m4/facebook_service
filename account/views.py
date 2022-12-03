from django.http import Http404
from rest_framework import serializers, views, viewsets
from rest_framework.response import Response

from account.selectors.integration import is_campaigns_exists

from . import constants
from . import serializers as account_serializers


class FacebookIntegrationsView(viewsets.ModelViewSet):
    serializer_class = account_serializers.FacebookIntegrationsSerializer

    @staticmethod
    def is_credentials_exists(instance):
        return is_campaigns_exists(instance)

    def get_queryset(self):
        return self.serializer_class.Meta.model.objects.filter(company_id=self.request.user.profile.company_id)

    def destroy(self, request, *args, **kwargs):
        if kwargs.get('pk'):
            try:
                instance = self.serializer_class.Meta.model.objects.get(
                    id=kwargs.get('pk'), company_id=request.user.profile.company_id
                )
            except self.serializer_class.Meta.model.DoesNotExist:
                raise Http404
            if self.is_credentials_exists(instance):
                raise serializers.ValidationError("This integration can't be removed. It's used by campaign.")
        return super(FacebookIntegrationsView, self).destroy(request, *args, **kwargs)


class FacebookManagedIntegrationView(views.APIView):
    serializer_class = account_serializers.FacebookManagedIntegrationSerializer

    def post(self, request, *args, **kwargs):
        external_data = dict(
            company_id=request.user.profile.company_id,
            name='Managed Integration',
            status=constants.PENDING,
            is_managed=True,
        )

        serializer = self.serializer_class(data=external_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
