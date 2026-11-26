
import re
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Employee
from decimal import Decimal


@login_required
def employee_list(request):
    search = request.GET.get('search')
    department = request.GET.get('department')

    employees = Employee.objects.all()

    if search:
        employees = employees.filter(name__icontains=search)

    if department:
        employees = employees.filter(department=department)

    total_employees = Employee.objects.count()

    departments = Employee.objects.values_list(
        'department', flat=True
    ).distinct()

    return render(request, 'employees/employee_list.html', {
        'employees': employees,
        'total_employees': total_employees,
        'departments': departments
    })


@login_required
def add_employee(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        if not re.fullmatch(r'[0-9]{10}', phone or ''):
            messages.error(
                request,
                'Phone number must contain exactly 10 digits.'
            )
            return redirect('add_employee')

        department = request.POST.get('department')
        salary = request.POST.get('salary')
        joining_date = request.POST.get('joining_date')

        Employee.objects.create(
            name=name,
            email=email,
            phone=phone,
            department=department,
            salary=salary,
            joining_date=joining_date
        )

        messages.success(request, 'Employee Added Successfully!')
        return redirect('employee_list')

    return render(request, 'employees/add_employee.html')

@login_required
def delete_employee(request, id):
    if request.method == 'POST':
        employee = Employee.objects.get(id=id)
        employee.delete()
        messages.success(request, 'Employee Deleted Successfully!')

    return redirect('employee_list')


@login_required
def edit_employee(request, id):
    employee = Employee.objects.get(id=id)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        department = request.POST.get('department')
        salary = request.POST.get('salary')
        joining_date = request.POST.get('joining_date')

        if not re.fullmatch(r'[0-9]{10}', phone or ''):
            messages.error(request, 'Phone number must contain exactly 10 digits.')
            return redirect('edit_employee', id=id)

        # Check whether any details have changed
        changed = (
            employee.name != name or
            employee.email != email or
            employee.phone != phone or
            employee.department != department or
            employee.salary != Decimal(salary) or
            employee.joining_date.isoformat() != joining_date
        )

        if not changed:
            return redirect('employee_list')

        employee.name = name
        employee.email = email
        employee.phone = phone
        employee.department = department
        employee.salary = salary
        employee.joining_date = joining_date

        employee.save()

        messages.success(request, 'Employee Updated Successfully!')

        return redirect('employee_list')

    return render(request, 'employees/edit_employee.html', {
        'employee': employee
    })


@login_required
def dashboard(request):
    total_employees = Employee.objects.count()

    return render(request, 'employees/dashboard.html', {
        'total_employees': total_employees
    })
