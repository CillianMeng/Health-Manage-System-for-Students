"""
后台管理系统表单
"""
from django import forms
from django.contrib.auth.hashers import make_password
from .models import User, SleepRecord, ExerciseRecord, DietRecord, FoodCalorieReference
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


class AdminDietRecordForm(forms.ModelForm):
    """管理员饮食记录表单"""
    
    class Meta:
        model = DietRecord
        fields = ['user', 'diet_date', 'meal_type', 'food_name', 'portion_size', 'calories_per_100g', 'notes']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'diet_date': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date',
                'placeholder': '选择饮食日期'
            }),
            'meal_type': forms.Select(attrs={'class': 'form-control'}),
            'food_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '请输入食物名称',
                'list': 'food-suggestions'
            }),
            'portion_size': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': '请输入食物分量（克/毫升）',
                'min': 1,
                'max': 2000
            }),
            'calories_per_100g': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': '每100g/ml卡路里',
                'min': 1,
                'max': 900
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': '备注信息（可选）'
            }),
        }
        labels = {
            'user': '用户',
            'diet_date': '饮食日期',
            'meal_type': '餐次',
            'food_name': '食物名称',
            'portion_size': '食物分量（克/毫升）',
            'calories_per_100g': '每100g/ml卡路里',
            'notes': '备注',
        }
    
    def clean_food_name(self):
        food_name = self.cleaned_data.get('food_name')
        if food_name:
            food_name = food_name.strip()
            if len(food_name) == 0:
                raise forms.ValidationError('食物名称不能为空')
            if len(food_name) > 50:
                raise forms.ValidationError('食物名称不能超过50个字符')
        return food_name
    
    def clean_portion_size(self):
        portion = self.cleaned_data.get('portion_size')
        if portion and (portion < 1 or portion > 2000):
            raise forms.ValidationError('食物分量应在1-2000克/毫升之间')
        return portion
    
    def clean_calories_per_100g(self):
        calories = self.cleaned_data.get('calories_per_100g')
        if calories and (calories <= 0 or calories > 900):
            raise forms.ValidationError('每100g卡路里应在1-900之间')
        return calories


class AdminFoodCalorieReferenceForm(forms.ModelForm):
    """管理员食物卡路里参考表单"""
    
    class Meta:
        model = FoodCalorieReference
        fields = ['food_name', 'calories_per_100g', 'food_category', 'description']
        widgets = {
            'food_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '请输入食物名称'
            }),
            'calories_per_100g': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': '每100g/ml卡路里含量',
                'min': 0,
                'max': 900
            }),
            'food_category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': '食物描述（可选）'
            }),
        }
        labels = {
            'food_name': '食物名称',
            'calories_per_100g': '每100g/ml卡路里',
            'food_category': '食物分类',
            'description': '描述',
        }
    
    def clean_food_name(self):
        food_name = self.cleaned_data.get('food_name')
        if food_name:
            food_name = food_name.strip()
            if len(food_name) == 0:
                raise forms.ValidationError('食物名称不能为空')
            if len(food_name) > 50:
                raise forms.ValidationError('食物名称不能超过50个字符')
            
            # 检查名称唯一性
            existing = FoodCalorieReference.objects.filter(
                food_name=food_name
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing.exists():
                raise forms.ValidationError('该食物名称已存在')
        
        return food_name
    
    def clean_calories_per_100g(self):
        calories = self.cleaned_data.get('calories_per_100g')
        if calories is not None and (calories < 0 or calories > 900):
            raise forms.ValidationError('每100g卡路里应在0-900之间')
        return calories
