from typing import Any
from django.db import models
from django.forms.models import BaseModelForm
from django.shortcuts import render,redirect
from django.http import HttpRequest, HttpResponse
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from . models import Task
from django.urls import reverse_lazy

# Create your views here.


class CustomLoginView(LoginView):
    template_name = 'login.html'

    def get_success_url(self):
        return reverse_lazy('tasks')


class RegisterPage(FormView):
    template_name = 'register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')


    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            redirect('tasks')
        return super().get(request, *args, **kwargs)


class TaskList(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'task_list.html'
    context_object_name = 'tasks'

    # use to pass context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = Task.objects.filter(user=self.request.user)
        context['count'] = context['tasks'].filter(complete=False).count()
        
        
        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['tasks'] = Task.objects.filter(title__icontains=search_input).filter(user=self.request.user)
        
        context['search_input'] = search_input
        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'task_detail.html'
    context_object_name = 'details'


class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    template_name = 'task_form.html'
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    template_name = 'task_form.html'
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')


class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'task_confirm_delete.html'
    context_object_name = 'tasks'
    success_url = reverse_lazy('tasks')

    # def get_queryset(self):
    #     owner = self.request.user
    #     return self.model.objects.filter(user=owner)
