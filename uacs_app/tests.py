from django.test import TestCase
from .models import Tribe, ServiceProvider
from django.urls import reverse

# Create your tests here.

#models test
class UacsAppTest(TestCase):

    def create_tribe(self, name="TestTribe", description="Testing Tribe creation"):
        return Tribe.objects.create(name=name, description=description)
    
    def create_service_provider(self, name="afex-sp", website_url="https://afex-sp.com"):
        return ServiceProvider.objects.create(name=name, website_url=website_url)

    def test_tribe_creation(self):
        tribe = self.create_tribe()
        self.assertTrue(isinstance(tribe, Tribe))
        self.assertEqual(tribe.__str__(), tribe.name)

    def test_service_provider_list_view(self):
        sp = self.create_service_provider()
        url = reverse('uacs:sp_list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn(sp.name, response.content)
        
