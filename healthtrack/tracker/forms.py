from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Measurement


class MeasurementForm(forms.ModelForm):
    class Meta:
        model = Measurement
        fields = ['measured_at', 'systolic', 'diastolic', 'pulse', 'note']
        widgets = {
            'measured_at': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M',
            ),
            'systolic': forms.NumberInput(attrs={'class': 'form-control'}),
            'diastolic': forms.NumberInput(attrs={'class': 'form-control'}),
            'pulse': forms.NumberInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['measured_at'].input_formats = ['%Y-%m-%dT%H:%M']

    def clean(self):
        cleaned = super().clean()
        s, d = cleaned.get('systolic'), cleaned.get('diastolic')
        if s and d and s <= d:
            raise forms.ValidationError('Верхнее давление должно быть больше нижнего.')
        return cleaned


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.update({'class': 'form-control'})