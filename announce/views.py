from django.contrib import auth
from django.contrib.auth.models import User

from announce.api import APIView, validate_serializer
from announce.serializers import UserLoginSerializer


class UserLoginAPI(APIView):
    @validate_serializer(UserLoginSerializer)
    def post(self, request):
        """
        User login api
        """
        data = request.data
        user = auth.authenticate(username=data["username"], password=data["password"])
        if user:
            return self.success("Succeeded")
            user = User()
            user.groups
            group = Group()
            l = list()
            l.append()
        else:
            return self.error("Invalid username or password")


