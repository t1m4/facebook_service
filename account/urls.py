from django.conf.urls import url
from rest_framework_extensions.routers import ExtendedDefaultRouter

from . import views

router = ExtendedDefaultRouter()


router.register('integration', views.FacebookIntegrationsView, base_name='facebook_integrations')

urlpatterns = [
    url(r'integration/managed/', views.FacebookManagedIntegrationView.as_view(), name='facebook_integration_managed'),
] + router.urls
