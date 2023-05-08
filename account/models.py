import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator, RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

from account.managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(
        _("first name"),
        max_length=30,
        validators=[MinLengthValidator(2), RegexValidator(r"^[-a-zA-ZА-Яа-я]+\Z")],
        blank=True,
    )
    last_name = models.CharField(
        _("last name"),
        max_length=30,
        validators=[MinLengthValidator(2), RegexValidator(r"^[-a-zA-ZА-Яа-я]+\Z")],
        blank=True,
    )
    email = models.EmailField(_("email address"), max_length=255, unique=True)
    email_confirm = models.BooleanField(default=False)
    username = None

    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )

    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def get_full_name(self):
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def __str__(self):
        return "{} <{}>".format(self.get_full_name(), self.email)

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


class Profile(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="profile"
    )
    phone = models.CharField(_("phone"), max_length=20, blank=True, null=True)
    street = models.CharField(_("street"), max_length=50, blank=True, null=True)
    postal_code = models.CharField(
        _("postal_code"), max_length=20, blank=True, null=True
    )
    city = models.CharField(_("city"), max_length=50, blank=True, null=True)
    region = models.CharField(_("region"), max_length=50, blank=True, null=True)
    province = models.CharField(_("province"), max_length=50, blank=True, null=True)

    def __str__(self):
        return self.user.email

    @receiver(post_save, sender=CustomUser)
    def create_or_update_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)
        instance.profile.save()
