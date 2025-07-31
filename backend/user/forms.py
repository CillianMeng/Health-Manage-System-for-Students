"""
后台管理系统表单
"""
from django import forms
from django.contrib.auth.hashers import make_password
from .models import User, SleepRecord, ExerciseRecord
from .utils import set_user_password


class AdminUserForm(forms.ModelForm):
    """管理员用户表单"""
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入密码'}),
        required=False,  # 编辑时不强制要求
        label='密码'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请再次输入密码'}),
        required=False,  # 编辑时不强制要求
        label='确认密码'
    )
    
    class Meta:
        model = User
        fields = ['userName']
        widgets = {
            'userName': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '请输入用户名'
            }),
        }
        labels = {
            'userName': '用户名',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 如果是新建用户，密码字段为必填
        if not self.instance.pk:
            self.fields['password1'].required = True
            self.fields['password2'].required = True
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        # 如果填写了密码，需要验证两次输入是否一致
        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError('两次输入的密码不一致')
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password1')
        
        # 只有当输入了新密码时才更新密码
        if password:
            set_user_password(user, password)
        
        if commit:
            user.save()
        return user


class AdminSleepRecordForm(forms.ModelForm):
    """管理员睡眠记录表单"""
    
    class Meta:
        model = SleepRecord
        fields = ['user', 'sleep_date', 'bedtime', 'wake_time']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'sleep_date': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date',
                'placeholder': '选择睡眠日期'
            }),
            'bedtime': forms.TimeInput(attrs={
                'class': 'form-control', 
                'type': 'time',
                'placeholder': '选择入睡时间'
            }),
            'wake_time': forms.TimeInput(attrs={
                'class': 'form-control', 
                'type': 'time',
                'placeholder': '选择起床时间'
            }),
        }
        labels = {
            'user': '用户',
            'sleep_date': '睡眠日期',
            'bedtime': '入睡时间',
            'wake_time': '起床时间',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        sleep_date = cleaned_data.get('sleep_date')
        
        # 检查是否已存在相同用户和日期的记录
        if user and sleep_date:
            existing = SleepRecord.objects.filter(
                user=user, 
                sleep_date=sleep_date
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing.exists():
                raise forms.ValidationError('该用户在此日期已有睡眠记录')
        
        return cleaned_data


class AdminExerciseRecordForm(forms.ModelForm):
    """管理员运动记录表单"""
    
    class Meta:
        model = ExerciseRecord
        fields = ['user', 'exercise_date', 'exercise_type', 'duration_minutes', 'calories_burned', 'notes']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'exercise_date': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date',
                'placeholder': '选择运动日期'
            }),
            'exercise_type': forms.Select(attrs={'class': 'form-control'}),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': '请输入运动时长（分钟）',
                'min': 1,
                'max': 480
            }),
            'calories_burned': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': '卡路里消耗（可选，留空自动计算）',
                'min': 1
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': '备注信息（可选）'
            }),
        }
        labels = {
            'user': '用户',
            'exercise_date': '运动日期',
            'exercise_type': '运动类型',
            'duration_minutes': '运动时长（分钟）',
            'calories_burned': '消耗卡路里',
            'notes': '备注',
        }
    
    def clean_duration_minutes(self):
        duration = self.cleaned_data.get('duration_minutes')
        if duration and (duration < 5 or duration > 480):
            raise forms.ValidationError('运动时长应在5-480分钟之间')
        return duration
    
    def clean_calories_burned(self):
        calories = self.cleaned_data.get('calories_burned')
        if calories is not None and calories <= 0:
            raise forms.ValidationError('卡路里消耗必须为正数')
        return calories
