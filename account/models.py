import django.utils.timezone as timezone

from django.contrib import auth
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import GroupManager, Permission, _user_get_all_permissions, _user_has_module_perms, \
    _user_has_perm
from django.contrib.contenttypes.models import ContentType
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, date_of_birth, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            date_of_birth=date_of_birth,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, date_of_birth, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            date_of_birth=date_of_birth,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class Group(models.Model):
    name = models.CharField(max_length=80, unique=True)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name='permissions',
        blank=True,
        related_name='group_permissions',
    )

    objects = GroupManager()

    class Meta:
        verbose_name = 'group'
        verbose_name_plural = 'groups'

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)


class PermissionsMixin(models.Model):
    is_superuser = models.BooleanField(
        'superuser status',
        default=False,
        help_text=
        'Designates that this user has all permissions without '
        'explicitly assigning them.'
        ,
    )
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text=
        'The groups this user belongs to. A user will get all permissions '
        'granted to each of their groups.'
        ,
        related_name="user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="user_set",
        related_query_name="user",
    )

    class Meta:
        abstract = True

    def get_group_permissions(self, obj=None):
        permissions = set()
        for backend in auth.get_backends():
            if hasattr(backend, "get_group_permissions"):
                permissions.update(backend.get_group_permissions(self, obj))
        return permissions

    def get_all_permissions(self, obj=None):
        return _user_get_all_permissions(self, obj)

    def has_perm(self, perm, obj=None):
        if self.is_active and self.is_superuser:
            return True
        return _user_has_perm(self, perm, obj)

    def has_perms(self, perm_list, obj=None):
        return all(self.has_perm(perm, obj) for perm in perm_list)

    def has_module_perms(self, app_label):
        if self.is_active and self.is_superuser:
            return True
        return _user_has_module_perms(self, app_label)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
        db_column='email'
    )
    real_name = models.CharField(max_length=30, default='', db_column='real_name')
    avatar = models.CharField(max_length=255, default='')
    birth = models.DateField(default=timezone.now, db_column='birth')
    # is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False, db_column='is_admin')
    # is_staff = models.BooleanField(
    #     'staff status',
    #     default=False,
    #     help_text='Designates whether the user can log into this admin site.',
    # )
    is_active = models.BooleanField(
        'active',
        default=True,
        help_text=
        'Designates whether this user should be treated as active. '
        'Unselect this instead of deleting accounts.'
        , db_column='is_active'
    )
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['date_of_birth']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin
