from django.db import models
from datetime import datetime, time, timedelta

# Create your models here.
class User(models.Model):
    userName = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=64)
    
    def __str__(self):
        return self.userName


class SleepRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sleep_records')
    sleep_date = models.DateField(help_text="睡眠日期（以入睡日期为准）")
    bedtime = models.TimeField(help_text="入睡时间")
    wake_time = models.TimeField(help_text="起床时间")
    sleep_duration = models.IntegerField(help_text="睡眠时长（分钟）", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'sleep_date']
        ordering = ['-sleep_date']
    
    def save(self, *args, **kwargs):
        """保存时自动计算睡眠时长"""
        if self.bedtime and self.wake_time:
            self.sleep_duration = self._calculate_sleep_duration()
        super().save(*args, **kwargs)
    
    def _calculate_sleep_duration(self):
        """计算睡眠时长（支持跨日）"""
        # 创建datetime对象进行计算
        bedtime_dt = datetime.combine(self.sleep_date, self.bedtime)
        
        # 如果起床时间早于入睡时间，说明跨日了
        if self.wake_time < self.bedtime:
            # 起床时间在第二天
            wake_date = self.sleep_date + timedelta(days=1)
        else:
            # 同一天
            wake_date = self.sleep_date
            
        wake_time_dt = datetime.combine(wake_date, self.wake_time)
        
        # 计算时长差（分钟）
        duration = wake_time_dt - bedtime_dt
        return int(duration.total_seconds() / 60)
    
    def get_sleep_quality_score(self):
        """根据睡眠时长计算睡眠质量评分"""
        if not self.sleep_duration:
            return 0
            
        duration_hours = self.sleep_duration / 60
        
        # 基于推荐睡眠时长（7-9小时）的评分
        if 7 <= duration_hours <= 9:
            return 100
        elif 6 <= duration_hours < 7 or 9 < duration_hours <= 10:
            return 80
        elif 5 <= duration_hours < 6 or 10 < duration_hours <= 11:
            return 60
        elif 4 <= duration_hours < 5 or 11 < duration_hours <= 12:
            return 40
        else:
            return 20
    
    def __str__(self):
        return f"{self.user.userName} - {self.sleep_date} ({self.sleep_duration}min)"


class ExerciseRecord(models.Model):
    EXERCISE_TYPES = [
        ('running', '跑步'),
        ('swimming', '游泳'),
        ('basketball', '篮球'),
        ('football', '足球'),
        ('tennis', '网球'),
        ('badminton', '羽毛球'),
        ('gym', '健身房'),
        ('yoga', '瑜伽'),
        ('cycling', '骑行'),
        ('other', '其他'),
    ]
    
    # MET值对应表（代谢当量）
    MET_VALUES = {
        'running': 8.0,
        'swimming': 7.0,
        'basketball': 6.5,
        'football': 7.0,
        'tennis': 7.0,
        'badminton': 5.5,
        'gym': 6.0,
        'yoga': 3.0,
        'cycling': 6.0,
        'other': 5.0,
    }
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercise_records')
    exercise_date = models.DateField(help_text="运动日期")
    exercise_type = models.CharField(max_length=20, choices=EXERCISE_TYPES, help_text="运动类型")
    duration_minutes = models.PositiveIntegerField(help_text="运动时长（分钟）")
    calories_burned = models.PositiveIntegerField(help_text="消耗卡路里", blank=True, null=True)
    notes = models.TextField(blank=True, help_text="备注信息")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-exercise_date', '-created_at']
    
    def save(self, *args, **kwargs):
        """保存时自动计算卡路里消耗（如果没有手动输入）"""
        if not self.calories_burned and self.duration_minutes:
            self.calories_burned = self._calculate_calories()
        super().save(*args, **kwargs)
    
    def _calculate_calories(self, weight_kg=65):
        """
        根据MET值计算卡路里消耗
        公式：卡路里 = MET × 体重(kg) × 时间(小时)
        默认体重65kg
        """
        met_value = self.MET_VALUES.get(self.exercise_type, 5.0)
        duration_hours = self.duration_minutes / 60
        calories = met_value * weight_kg * duration_hours
        return int(calories)
    
    def get_exercise_intensity(self):
        """根据MET值返回运动强度"""
        met_value = self.MET_VALUES.get(self.exercise_type, 5.0)
        if met_value < 3:
            return "低强度"
        elif met_value < 6:
            return "中等强度"
        else:
            return "高强度"
    
    def __str__(self):
        return f"{self.user.userName} - {self.exercise_date} - {self.get_exercise_type_display()} ({self.duration_minutes}min)"


class FoodCalorieReference(models.Model):
    """食物卡路里参考表"""
    FOOD_CATEGORIES = [
        ('staple', '主食'),
        ('vegetable', '蔬菜'),
        ('fruit', '水果'),
        ('meat', '肉类'),
        ('dairy', '乳制品'),
        ('beverage', '饮料'),
        ('snack', '零食'),
        ('other', '其他'),
    ]
    
    food_name = models.CharField(max_length=50, unique=True, help_text="食物名称")
    calories_per_100g = models.PositiveIntegerField(help_text="每100g/ml的卡路里含量")
    food_category = models.CharField(max_length=20, choices=FOOD_CATEGORIES, help_text="食物分类")
    description = models.TextField(blank=True, help_text="食物描述")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['food_category', 'food_name']
        verbose_name = "食物卡路里参考"
        verbose_name_plural = "食物卡路里参考"
    
    def __str__(self):
        return f"{self.food_name} ({self.calories_per_100g}kcal/100g)"


class DietRecord(models.Model):
    """饮食记录模型"""
    MEAL_TYPES = [
        ('breakfast', '早餐'),
        ('lunch', '午餐'),
        ('dinner', '晚餐'),
        ('snack', '加餐'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='diet_records')
    diet_date = models.DateField(help_text="饮食日期")
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES, help_text="餐次类型")
    food_name = models.CharField(max_length=50, help_text="食物名称")
    portion_size = models.PositiveIntegerField(help_text="食物分量（克或毫升）")
    calories_per_100g = models.PositiveIntegerField(help_text="每100g/ml卡路里")
    total_calories = models.PositiveIntegerField(help_text="总卡路里", blank=True, null=True)
    notes = models.TextField(blank=True, help_text="备注信息")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-diet_date', 'meal_type', '-created_at']
        verbose_name = "饮食记录"
        verbose_name_plural = "饮食记录"
    
    def save(self, *args, **kwargs):
        """保存时自动计算总卡路里"""
        if self.portion_size and self.calories_per_100g:
            self.total_calories = self._calculate_total_calories()
        super().save(*args, **kwargs)
    
    def _calculate_total_calories(self):
        """计算总卡路里：分量 × 每100g卡路里 / 100"""
        return int(self.portion_size * self.calories_per_100g / 100)
    
    def get_meal_type_display_order(self):
        """返回餐次的显示顺序"""
        meal_order = {
            'breakfast': 1,
            'lunch': 2,
            'dinner': 3,
            'snack': 4,
        }
        return meal_order.get(self.meal_type, 5)
    
    def __str__(self):
        return f"{self.user.userName} - {self.diet_date} - {self.get_meal_type_display()} - {self.food_name} ({self.total_calories}kcal)"