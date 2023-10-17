
from django.contrib.auth.models import User
from durin.models import Client as APIClient
from durin.views import LoginView as DurinLoginView
from rest_framework.exceptions import ValidationError

from sigint.models import AccessPlan


class LoginView(DurinLoginView):

    @staticmethod
    def get_client_obj(request):
        """
        Checks if User can access this client
        """
        user: User = request.user

        client_name = request.data.get("client", None)
        if not client_name:
            raise ValidationError({"detail": "No client specified."})

        try:
            client: APIClient = APIClient.objects.get(name=client_name)
            plan: AccessPlan = AccessPlan.objects.get(client=client)
            if not plan.check_user_allowed(user=user):
                 raise ValidationError({"detail": "No client with that name."})
            return client
        except APIClient.DoesNotExist:
            raise ValidationError({"detail": "No client with that name."})
