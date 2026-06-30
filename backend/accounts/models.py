from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('caregiver', 'Caregiver'),
        ('family', 'Family'),
        ('admin', 'Admin'),
    ]

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='family')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email

    @property
    def is_caregiver(self):
        return self.role == 'caregiver'

    @property
    def is_family(self):
        return self.role == 'family'

    @property
    def is_admin_user(self):
        return self.role == 'admin'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()


def get_or_create_subclass(model, user, **defaults):
    """Promote an existing User row to a multi-table-inheritance subclass (e.g. CaregiverProfile).

    `model.objects.get_or_create(pk=user.pk)` looks like the obvious way to do
    this but is unsafe: Django's MTI save() also issues an UPDATE against the
    parent `users` table using whatever parent-field values happen to be on
    the freshly constructed (mostly-default) child instance, silently
    blanking the real user's email/password/etc. Seeding the new instance
    from the already-loaded user's own field values makes that UPDATE a
    no-op instead.
    """
    try:
        return model.objects.get(pk=user.pk), False
    except model.DoesNotExist:
        parent_values = {f.attname: getattr(user, f.attname) for f in user._meta.local_fields}
        instance = model(**parent_values, **defaults)
        instance.save()
        return instance, True
