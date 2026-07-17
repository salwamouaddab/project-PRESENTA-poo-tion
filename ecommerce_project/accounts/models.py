from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Utilisateur personnalisé avec un rôle : Vendeur ou Client."""

    class Role(models.TextChoices):
        CLIENT = "CLIENT", "Client"
        VENDEUR = "VENDEUR", "Vendeur"

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.CLIENT,
        verbose_name="Rôle",
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    address = models.CharField(max_length=255, blank=True, verbose_name="Adresse")

    @property
    def is_vendeur(self):
        return self.role == self.Role.VENDEUR

    @property
    def is_client(self):
        return self.role == self.Role.CLIENT

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class VendorProfile(models.Model):
    """Informations complémentaires pour les comptes vendeur (boutique)."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="vendor_profile"
    )
    shop_name = models.CharField(max_length=150, verbose_name="Nom de la boutique")
    description = models.TextField(blank=True, verbose_name="Description")
    logo = models.ImageField(upload_to="shop_logos/", blank=True, null=True)
    is_approved = models.BooleanField(
        default=True, verbose_name="Boutique validée par l'admin"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.shop_name
