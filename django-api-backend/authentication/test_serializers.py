"""
Tests for authentication serializers
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import serializers
from authentication.models import Role, CustomUser
from authentication.serializers import (
    RoleSerializer,
    CustomUserSerializer,
    CustomTokenObtainPairSerializer,
    LoginSerializer,
    ChangePasswordSerializer
)


class RoleSerializerTest(TestCase):
    """Test cases for RoleSerializer"""
    
    def setUp(self):
        """Set up test data"""
        self.role_data = {
            'nombre': 'Administrador',
            'descripcion': 'Rol con permisos completos',
            'permisos': ['create', 'read', 'update', 'delete']
        }
        self.role = Role.objects.create(**self.role_data)
    
    def test_role_serialization(self):
        """Test role serialization"""
        serializer = RoleSerializer(self.role)
        data = serializer.data
        
        self.assertEqual(data['nombre'], 'Administrador')
        self.assertEqual(data['descripcion'], 'Rol con permisos completos')
        self.assertEqual(data['permisos'], ['create', 'read', 'update', 'delete'])
        self.assertTrue(data['is_active'])
        self.assertIn('id', data)
        self.assertIn('created_at', data)
    
    def test_role_deserialization_valid(self):
        """Test valid role deserialization"""
        data = {
            'nombre': 'Nuevo Rol',
            'descripcion': 'Descripción del nuevo rol',
            'permisos': ['read', 'write']
        }
        
        serializer = RoleSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        role = serializer.save()
        self.assertEqual(role.nombre, 'Nuevo Rol')
        self.assertEqual(role.descripcion, 'Descripción del nuevo rol')
        self.assertEqual(role.permisos, ['read', 'write'])
    
    def test_role_deserialization_invalid(self):
        """Test invalid role deserialization"""
        # Missing required fields
        data = {
            'descripcion': 'Descripción sin nombre'
        }
        
        serializer = RoleSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('nombre', serializer.errors)
    
    def test_role_update(self):
        """Test role update"""
        update_data = {
            'nombre': 'Administrador Actualizado',
            'descripcion': 'Descripción actualizada',
            'permisos': ['all']
        }
        
        serializer = RoleSerializer(self.role, data=update_data)
        self.assertTrue(serializer.is_valid())
        
        updated_role = serializer.save()
        self.assertEqual(updated_role.nombre, 'Administrador Actualizado')
        self.assertEqual(updated_role.descripcion, 'Descripción actualizada')
        self.assertEqual(updated_role.permisos, ['all'])


class CustomUserSerializerTest(TestCase):
    """Test cases for CustomUserSerializer"""
    
    def setUp(self):
        """Set up test data"""
        self.role = Role.objects.create(
            nombre='Usuario',
            descripcion='Rol básico'
        )
        
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'dni': '12345678',
            'licencia': 'A12345678',
            'celular': '987654321',
            'rol': self.role.id,
            'password': 'testpassword123',
            'password_confirm': 'testpassword123'
        }
        
        self.user = CustomUser.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            dni='87654321',
            password='password123'
        )
    
    def test_user_serialization(self):
        """Test user serialization"""
        serializer = CustomUserSerializer(self.user)
        data = serializer.data
        
        self.assertEqual(data['username'], 'existinguser')
        self.assertEqual(data['email'], 'existing@example.com')
        self.assertEqual(data['dni'], '87654321')
        self.assertIn('id', data)
        self.assertIn('created_at', data)
        self.assertNotIn('password', data)  # Password should not be serialized
    
    def test_user_creation_valid(self):
        """Test valid user creation"""
        serializer = CustomUserSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        user = serializer.save()
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.dni, '12345678')
        self.assertEqual(user.licencia, 'A12345678')
        self.assertEqual(user.celular, '987654321')
        self.assertTrue(user.check_password('testpassword123'))
    
    def test_dni_validation_invalid_format(self):
        """Test DNI validation with invalid format"""
        invalid_dnis = ['1234567', '123456789', '1234567a', '']
        
        for dni in invalid_dnis:
            data = self.user_data.copy()
            data['dni'] = dni
            data['username'] = f'user_{dni}'
            
            serializer = CustomUserSerializer(data=data)
            self.assertFalse(serializer.is_valid())
            self.assertIn('dni', serializer.errors)
    
    def test_dni_validation_duplicate(self):
        """Test DNI validation with duplicate value"""
        data = self.user_data.copy()
        data['dni'] = '87654321'  # Same as existing user
        
        serializer = CustomUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('dni', serializer.errors)
    
    def test_licencia_validation_invalid_format(self):
        """Test license validation with invalid format"""
        invalid_licenses = ['12345678A', 'AA12345678', '123456789', 'A1234567']
        
        for license in invalid_licenses:
            data = self.user_data.copy()
            data['licencia'] = license
            data['username'] = f'user_{license}'
            data['dni'] = f'{license[-8:]}' if len(license) >= 8 else '11111111'
            
            serializer = CustomUserSerializer(data=data)
            self.assertFalse(serializer.is_valid())
            self.assertIn('licencia', serializer.errors)
    
    def test_licencia_validation_optional(self):
        """Test that license is optional"""
        data = self.user_data.copy()
        data['licencia'] = ''
        
        serializer = CustomUserSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
    
    def test_celular_validation_invalid(self):
        """Test phone validation with invalid values"""
        invalid_phones = ['12345678', '9876543210', '87654321', 'abcdefghi']
        
        for phone in invalid_phones:
            data = self.user_data.copy()
            data['celular'] = phone
            data['username'] = f'user_{phone}'
            data['dni'] = f'{phone[-8:]}' if len(phone) >= 8 else '11111111'
            
            serializer = CustomUserSerializer(data=data)
            self.assertFalse(serializer.is_valid())
            self.assertIn('celular', serializer.errors)
    
    def test_email_validation_duplicate(self):
        """Test email validation with duplicate value"""
        data = self.user_data.copy()
        data['email'] = 'existing@example.com'  # Same as existing user
        
        serializer = CustomUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_password_validation_mismatch(self):
        """Test password confirmation mismatch"""
        data = self.user_data.copy()
        data['password_confirm'] = 'differentpassword'
        
        serializer = CustomUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password_confirm', serializer.errors)
    
    def test_password_validation_too_short(self):
        """Test password minimum length validation"""
        data = self.user_data.copy()
        data['password'] = '123'
        data['password_confirm'] = '123'
        
        serializer = CustomUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
    
    def test_user_update_without_password(self):
        """Test user update without changing password"""
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'celular': '912345678'
        }
        
        serializer = CustomUserSerializer(self.user, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        updated_user = serializer.save()
        self.assertEqual(updated_user.first_name, 'Updated')
        self.assertEqual(updated_user.last_name, 'Name')
        self.assertEqual(updated_user.celular, '912345678')
    
    def test_user_update_with_password(self):
        """Test user update with password change"""
        update_data = {
            'first_name': 'Updated',
            'password': 'newpassword123',
            'password_confirm': 'newpassword123'
        }
        
        serializer = CustomUserSerializer(self.user, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        updated_user = serializer.save()
        self.assertEqual(updated_user.first_name, 'Updated')
        self.assertTrue(updated_user.check_password('newpassword123'))


class LoginSerializerTest(TestCase):
    """Test cases for LoginSerializer"""
    
    def setUp(self):
        """Set up test data"""
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            dni='12345678',
            password='testpassword123'
        )
    
    def test_login_valid_credentials(self):
        """Test login with valid credentials"""
        data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        
        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        validated_data = serializer.validated_data
        self.assertEqual(validated_data['user'], self.user)
    
    def test_login_invalid_username(self):
        """Test login with invalid username"""
        data = {
            'username': 'nonexistent',
            'password': 'testpassword123'
        }
        
        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    def test_login_invalid_password(self):
        """Test login with invalid password"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    def test_login_inactive_user(self):
        """Test login with inactive user"""
        self.user.is_active = False
        self.user.save()
        
        data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        
        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    def test_login_missing_fields(self):
        """Test login with missing fields"""
        # Missing password
        data = {'username': 'testuser'}
        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
        
        # Missing username
        data = {'password': 'testpassword123'}
        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)


class ChangePasswordSerializerTest(TestCase):
    """Test cases for ChangePasswordSerializer"""
    
    def setUp(self):
        """Set up test data"""
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            dni='12345678',
            password='oldpassword123'
        )
    
    def test_change_password_valid(self):
        """Test valid password change"""
        data = {
            'old_password': 'oldpassword123',
            'new_password': 'newpassword123',
            'new_password_confirm': 'newpassword123'
        }
        
        serializer = ChangePasswordSerializer(data=data)
        serializer.context = {'request': type('obj', (object,), {'user': self.user})}
        
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        updated_user = serializer.save()
        self.assertTrue(updated_user.check_password('newpassword123'))
        self.assertFalse(updated_user.check_password('oldpassword123'))
    
    def test_change_password_wrong_old_password(self):
        """Test password change with wrong old password"""
        data = {
            'old_password': 'wrongpassword',
            'new_password': 'newpassword123',
            'new_password_confirm': 'newpassword123'
        }
        
        serializer = ChangePasswordSerializer(data=data)
        serializer.context = {'request': type('obj', (object,), {'user': self.user})}
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('old_password', serializer.errors)
    
    def test_change_password_mismatch_confirmation(self):
        """Test password change with mismatched confirmation"""
        data = {
            'old_password': 'oldpassword123',
            'new_password': 'newpassword123',
            'new_password_confirm': 'differentpassword'
        }
        
        serializer = ChangePasswordSerializer(data=data)
        serializer.context = {'request': type('obj', (object,), {'user': self.user})}
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('new_password_confirm', serializer.errors)
    
    def test_change_password_weak_password(self):
        """Test password change with weak password"""
        data = {
            'old_password': 'oldpassword123',
            'new_password': '123',  # Too short
            'new_password_confirm': '123'
        }
        
        serializer = ChangePasswordSerializer(data=data)
        serializer.context = {'request': type('obj', (object,), {'user': self.user})}
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('new_password', serializer.errors)
    
    def test_change_password_missing_fields(self):
        """Test password change with missing fields"""
        data = {
            'old_password': 'oldpassword123',
            'new_password': 'newpassword123'
            # Missing new_password_confirm
        }
        
        serializer = ChangePasswordSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('new_password_confirm', serializer.errors)


class CustomTokenObtainPairSerializerTest(APITestCase):
    """Test cases for CustomTokenObtainPairSerializer"""
    
    def setUp(self):
        """Set up test data"""
        self.role = Role.objects.create(
            nombre='Usuario',
            descripcion='Rol básico'
        )
        
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            dni='12345678',
            password='testpassword123',
            rol=self.role
        )
    
    def test_token_obtain_valid_credentials(self):
        """Test token obtain with valid credentials"""
        data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        
        serializer = CustomTokenObtainPairSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        validated_data = serializer.validated_data
        self.assertIn('access', validated_data)
        self.assertIn('refresh', validated_data)
        self.assertIn('user', validated_data)
        
        user_data = validated_data['user']
        self.assertEqual(user_data['id'], self.user.id)
        self.assertEqual(user_data['username'], 'testuser')
        self.assertEqual(user_data['email'], 'test@example.com')
        self.assertEqual(user_data['rol_nombre'], 'Usuario')
    
    def test_token_obtain_invalid_credentials(self):
        """Test token obtain with invalid credentials"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        serializer = CustomTokenObtainPairSerializer(data=data)
        self.assertFalse(serializer.is_valid())
    
    def test_token_obtain_inactive_user(self):
        """Test token obtain with inactive user"""
        self.user.is_active = False
        self.user.save()
        
        data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        
        serializer = CustomTokenObtainPairSerializer(data=data)
        self.assertFalse(serializer.is_valid())
    
    def test_custom_token_claims(self):
        """Test custom token claims"""
        token = CustomTokenObtainPairSerializer.get_token(self.user)
        
        # Check custom claims
        self.assertEqual(token['user_id'], self.user.id)
        self.assertEqual(token['username'], self.user.username)
        self.assertEqual(token['email'], self.user.email)
        self.assertEqual(token['rol_nombre'], 'Usuario')
        self.assertEqual(token['full_name'], self.user.get_full_name())