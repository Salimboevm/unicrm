from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from authentication.models import User, Profile, Membership
from event.models import Event
from django.utils import timezone
from datetime import timedelta

class EventManagementTestCase(APITestCase):
    def setUp(self):
        # Create admin user
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@gmail.com',
            password='admin'
        )
        
        # Create regular member with community membership
        self.member = User.objects.create_user(
            username='admin',
            email='admin@admin.com',
            password='admin'
        )
        
        self.member_profile = Profile.objects.create(
            user=self.member,
            full_name='Test Member',
            bio='Test bio',
            phone_number='1234567890',
            location='Test Location'
        )
        
        # Create membership for the member
        self.membership = Membership.objects.create(
            profile=self.member_profile,
            membership_type='community',
            is_approved=True
        )
        
        # Default event data for tests
        self.event_data = {
            'title': 'Test Workshop',
            'description': 'A test workshop for automated testing',
            'event_type': 'workshop',
            'event_date': (timezone.now() + timedelta(days=30)).date().isoformat(),
            'start_time': '10:00:00',
            'end_time': '12:00:00',
            'location': 'Test Venue',
            'capacity': 25,
            'eligible_membership_types': 'community,key_access',
            'is_active': True,
            'is_public': False,
            'registration_opens': (timezone.now() + timedelta(days=1)).isoformat(),
            'registration_closes': (timezone.now() + timedelta(days=25)).isoformat()
        }
    
    def test_event_crud_operations(self):
        """Test creating, reading, updating and deleting events by admin"""
        # Login as admin
        self.client.force_authenticate(user=self.admin)
        
        # 1. Create event
        create_url = reverse('event-list')
        response = self.client.post(create_url, self.event_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['title'], 'Test Workshop')
        
        event_id = response.data['id']
        
        # 2. Retrieve event
        detail_url = reverse('event-detail', kwargs={'pk': event_id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Test Workshop')
        
        # 3. Update event
        update_data = {
            'title': 'Updated Workshop Title',
            'capacity': 30
        }
        response = self.client.patch(detail_url, update_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Updated Workshop Title')
        self.assertEqual(response.data['capacity'], 30)
        
        # 4. Delete event
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, 204)
        
        # Verify deletion
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 404)
        
    def test_non_admin_cannot_manage_events(self):
        """Test that non-admin users cannot create/update/delete events"""
        self.client.force_authenticate(user=self.member)
        
        # Try to create event
        create_url = reverse('event-list')
        response = self.client.post(create_url, self.event_data, format='json')
        self.assertEqual(response.status_code, 403)
        
        # Create an event as admin first
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(create_url, self.event_data, format='json')
        event_id = response.data['id']
        
        # Try to modify as regular user
        self.client.force_authenticate(user=self.member)
        detail_url = reverse('event-detail', kwargs={'pk': event_id})
        update_data = {'title': 'Hacked Title'}
        response = self.client.patch(detail_url, update_data, format='json')
        self.assertEqual(response.status_code, 403)
        
        # Try to delete as regular user
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, 403)