from rest_framework import routers

from payments.views import PaymentListRetrieveViewSet

app_name = "payments"

router = routers.DefaultRouter()
router.register("", PaymentListRetrieveViewSet, basename="payments")

urlpatterns = router.urls
