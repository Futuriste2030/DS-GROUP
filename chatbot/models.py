from django.db import models


class ChatbotKnowledge(models.Model):
    """Entrées de connaissance gérées via l'admin, passées au contexte Gemini."""
    name = models.CharField(max_length=200, db_index=True)
    content = models.TextField(
        help_text='Texte brut. Passé directement au prompt Gemini. Pas de HTML.',
    )
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Knowledge entry'
        verbose_name_plural = 'Knowledge entries'

    def __str__(self):
        return self.name


class Conversation(models.Model):
    """Une conversation par session navigateur."""
    session_id = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'

    def __str__(self):
        return self.session_id


class Message(models.Model):
    ROLE_CHOICES = [('user', 'User'), ('assistant', 'Assistant')]
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name='messages',
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, db_index=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'

    def __str__(self):
        return f'{self.role}: {self.content[:60]}'
