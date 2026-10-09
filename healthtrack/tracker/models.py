from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Measurement(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='measurements',
        verbose_name='Пользователь',
    )
    measured_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата и время измерения',
    )
    systolic = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(50), MaxValueValidator(300)],
        verbose_name='Верхнее (систолическое)',
    )
    diastolic = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(30), MaxValueValidator(200)],
        verbose_name='Нижнее (диастолическое)',
    )
    pulse = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(30), MaxValueValidator(220)],
        verbose_name='Пульс',
    )
    note = models.TextField(blank=True, verbose_name='Заметка')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-measured_at']
        verbose_name = 'Измерение'
        verbose_name_plural = 'Измерения'
        indexes = [models.Index(fields=['user', '-measured_at'])]

    def __str__(self):
        return f'{self.measured_at:%d.%m.%Y %H:%M} — {self.systolic}/{self.diastolic}'

    @property
    def is_hypertensive(self) -> bool:
        return self.systolic > 140 or self.diastolic > 90

    @property
    def is_pulse_abnormal(self) -> bool:
        return self.pulse > 100 or self.pulse < 50

    @property
    def status(self) -> str:
        if self.is_hypertensive:
            return 'danger'
        if self.is_pulse_abnormal:
            return 'warning'
        return 'normal'