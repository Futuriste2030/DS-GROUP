from django.db import models
from django.utils import timezone


def _unique_reference(model_cls, prefix):
    year = timezone.now().strftime('%Y')
    base = f'{prefix}-{year}'
    # Compteur basé sur le nombre existant de l'année pour rester lisible,
    # avec boucle anti-collision comme DIGI careers Application.
    count = model_cls.objects.filter(reference__startswith=base).count() + 1
    ref = f'{base}-{count:04d}'
    while model_cls.objects.filter(reference=ref).exists():
        count += 1
        ref = f'{base}-{count:04d}'
    return ref


class ContactMessage(models.Model):
    reference = models.CharField(max_length=50, unique=True, editable=False, blank=True)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    service = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.reference or "—"} — {self.name} — {self.service}'

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = _unique_reference(ContactMessage, 'MS')
        super().save(*args, **kwargs)


class QuoteRequest(models.Model):
    reference = models.CharField(max_length=50, unique=True, editable=False, blank=True)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    subject = models.CharField(max_length=300, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.reference or "—"} — {self.name} — {self.subject}'

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = _unique_reference(QuoteRequest, 'QT')
        super().save(*args, **kwargs)


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class NotifySubscriber(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
