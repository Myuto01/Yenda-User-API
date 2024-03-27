from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework import status



class ContactTestCase(APITestCase):

    """
    Test suite for Contact
    """
    def setUp(self):
        self.client = APIClient()
        self.data = {
            "username": "Mutale",
            "password": "M@gna2020",
        }
        self.url = "/user_login/"