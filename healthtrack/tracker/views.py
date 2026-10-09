import csv
from datetime import datetime

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from .forms import MeasurementForm, RegisterForm
from .models import Measurement


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'tracker/register.html', {'form': form})


@login_required
def dashboard(request):
    qs = Measurement.objects.filter(user=request.user)

    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if date_from:
        try:
            qs = qs.filter(measured_at__date__gte=datetime.strptime(date_from, '%Y-%m-%d'))
        except ValueError:
            pass
    if date_to:
        try:
            qs = qs.filter(measured_at__date__lte=datetime.strptime(date_to, '%Y-%m-%d'))
        except ValueError:
            pass

    chart_qs = list(qs.order_by('measured_at')[:100])
    chart_data = {
        'labels': [m.measured_at.strftime('%d.%m %H:%M') for m in chart_qs],
        'systolic': [m.systolic for m in chart_qs],
        'diastolic': [m.diastolic for m in chart_qs],
        'pulse': [m.pulse for m in chart_qs],
    }

    context = {
        'measurements': qs[:200],
        'chart_data': chart_data,
        'date_from': date_from or '',
        'date_to': date_to or '',
        'danger_count': qs.filter(Q(systolic__gt=140) | Q(diastolic__gt=90)).count(),
    }
    return render(request, 'tracker/dashboard.html', context)


@login_required
def measurement_add(request):
    if request.method == 'POST':
        form = MeasurementForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            if obj.is_hypertensive:
                messages.warning(request, '⚠ Внимание! Давление выше нормы (140/90).')
            else:
                messages.success(request, 'Измерение сохранено.')
            return redirect('dashboard')
    else:
        form = MeasurementForm(initial={'measured_at': timezone.now()})
    return render(request, 'tracker/measurement_form.html', {'form': form})


@login_required
def measurement_delete(request, pk):
    Measurement.objects.filter(pk=pk, user=request.user).delete()
    messages.info(request, 'Измерение удалено.')
    return redirect('dashboard')


@login_required
def export_csv(request):
    qs = Measurement.objects.filter(user=request.user).order_by('-measured_at')
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="measurements.csv"'
    response.write('\ufeff')
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Дата', 'Верхнее', 'Нижнее', 'Пульс', 'Заметка', 'Статус'])
    for m in qs:
        writer.writerow([
            m.measured_at.strftime('%d.%m.%Y %H:%M'),
            m.systolic, m.diastolic, m.pulse,
            m.note, 'Высокое' if m.is_hypertensive else 'Норма',
        ])
    return response