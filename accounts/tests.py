from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AuthenticationFlowTests(TestCase):
    """Critical authentication checks using the SQLite auth database only."""

    databases = {'auth_db'}

    def test_signup_and_login_pages_load(self):
        self.assertEqual(self.client.get(reverse('accounts:signup')).status_code, 200)
        self.assertEqual(self.client.get(reverse('accounts:login')).status_code, 200)

    def test_logged_out_home_redirects_to_login(self):
        response = self.client.get(reverse('catalog:home'))
        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next=/",
            fetch_redirect_response=False,
        )

    def test_signup_creates_hashed_user_in_auth_database(self):
        response = self.client.post(
            reverse('accounts:signup'),
            {
                'form_type': 'signup',
                'username': 'test_student',
                'email': 'student@example.edu',
                'password1': 'A-secure-test-password-123',
                'password2': 'A-secure-test-password-123',
            },
        )

        self.assertRedirects(response, reverse('catalog:home'), fetch_redirect_response=False)
        user = get_user_model().objects.using('auth_db').get(username='test_student')
        self.assertTrue(user.check_password('A-secure-test-password-123'))
