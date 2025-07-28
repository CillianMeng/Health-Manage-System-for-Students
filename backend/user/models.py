from django.db import models
from datetime import datetime, timedelta

# Create your models here.
class User(models.Model):
    userName = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=64)

    def __str__(self):
        return self.userName

class SleepRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sleep_records')
    date = models.DateField(help_text="睡眠记录的日期")
    sleep_time = models.TimeField(help_text="入睡时间")
    wake_time = models.TimeField(help_text="起床时间")
    sleep_duration = models.DurationField(null=True, blank=True, help_text="睡眠时长（自动计算）")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'date')  # 每个用户每天只能有一条记录
        ordering = ['-date']

    def save(self, *args, **kwargs):
        # 自动计算睡眠时长
        if self.sleep_time and self.wake_time:
            # 创建datetime对象来计算时间差
            sleep_datetime = datetime.combine(self.date, self.sleep_time)
            wake_datetime = datetime.combine(self.date, self.wake_time)
            
            # 如果起床时间早于入睡时间，说明是第二天起床
            if self.wake_time < self.sleep_time:
                wake_datetime += timedelta(days=1)
            
            self.sleep_duration = wake_datetime - sleep_datetime
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.userName} - {self.date}"

    @property
    def sleep_duration_hours(self):
        """返回睡眠时长（小时）"""
        if self.sleep_duration:
            return round(self.sleep_duration.total_seconds() / 3600, 2)
        return None

class ExerciseRecord(models.Model):
    EXERCISE_TYPES = [
        ('running', '跑步'),
        ('walking', '步行'),
        ('cycling', '骑行'),
        ('swimming', '游泳'),
        ('basketball', '篮球'),
        ('football', '足球'),
        ('tennis', '网球'),
        ('badminton', '羽毛球'),
        ('yoga', '瑜伽'),
        ('fitness', '健身'),
        ('dancing', '舞蹈'),
        ('climbing', '爬山'),
        ('other', '其他'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercise_records')
    date = models.DateField(help_text="运动记录的日期")
    exercise_type = models.CharField(max_length=20, choices=EXERCISE_TYPES, help_text="运动类型")
    duration_minutes = models.PositiveIntegerField(help_text="运动时长（分钟）")
    calories_burned = models.PositiveIntegerField(help_text="消耗的卡路里数")
    notes = models.TextField(blank=True, help_text="备注信息")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.user.userName} - {self.get_exercise_type_display()} - {self.date}"

    @property
    def duration_hours(self):
        """返回运动时长（小时）"""
        return round(self.duration_minutes / 60, 2)

    def get_intensity_level(self):
        """根据运动时长和卡路里消耗判断运动强度"""
        calories_per_minute = self.calories_burned / self.duration_minutes if self.duration_minutes > 0 else 0
        
        if calories_per_minute >= 10:
            return "高强度"
        elif calories_per_minute >= 6:
            return "中强度"
        elif calories_per_minute >= 3:
            return "低强度"
        else:
            return "轻微活动"

class FoodItem(models.Model):
    """食物数据库模型"""
    FOOD_CATEGORIES = [
        ('grains', '谷物类'),
        ('vegetables', '蔬菜类'),
        ('fruits', '水果类'),
        ('meat', '肉类'),
        ('seafood', '海鲜类'),
        ('dairy', '乳制品'),
        ('nuts', '坚果类'),
        ('beverages', '饮品类'),
        ('snacks', '零食类'),
        ('cooking_oil', '调料油脂'),
        ('other', '其他'),
    ]
    
    name = models.CharField(max_length=100, help_text="食物名称")
    category = models.CharField(max_length=20, choices=FOOD_CATEGORIES, help_text="食物分类")
    calories_per_100g = models.PositiveIntegerField(help_text="每100克的卡路里")
    protein_per_100g = models.FloatField(default=0, help_text="每100克蛋白质含量(g)")
    fat_per_100g = models.FloatField(default=0, help_text="每100克脂肪含量(g)")
    carbs_per_100g = models.FloatField(default=0, help_text="每100克碳水化合物含量(g)")
    common_serving_size = models.CharField(max_length=50, default="100g", help_text="常见分量描述")
    common_serving_calories = models.PositiveIntegerField(help_text="常见分量的卡路里")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

class DietRecord(models.Model):
    """饮食记录模型"""
    MEAL_CHOICES = [
        ('breakfast', '早餐'),
        ('lunch', '午餐'),
        ('dinner', '晚餐'),
        ('snack', '加餐/零食'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='diet_records')
    date = models.DateField(help_text="饮食记录的日期")
    meal_type = models.CharField(max_length=20, choices=MEAL_CHOICES, help_text="餐次类型")
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE, null=True, blank=True, help_text="选择的食物")
    food_name = models.CharField(max_length=100, help_text="食物名称（手动输入或从数据库选择）")
    serving_size = models.CharField(max_length=50, help_text="分量描述，如：1碗、100g、1个等")
    serving_weight_grams = models.PositiveIntegerField(help_text="分量重量（克）")
    calories = models.PositiveIntegerField(help_text="估算的卡路里数")
    notes = models.TextField(blank=True, help_text="备注信息")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'meal_type', '-created_at']

    def __str__(self):
        return f"{self.user.userName} - {self.get_meal_type_display()} - {self.food_name} - {self.date}"

    def save(self, *args, **kwargs):
        # 如果选择了食物数据库中的食物，自动计算卡路里
        if self.food_item and self.serving_weight_grams:
            calculated_calories = round((self.food_item.calories_per_100g * self.serving_weight_grams) / 100)
            if not self.calories or self.calories == 0:
                self.calories = calculated_calories
            # 如果没有手动输入食物名称，使用数据库中的名称
            if not self.food_name:
                self.food_name = self.food_item.name
        
        super().save(*args, **kwargs)

    @property
    def calories_per_100g(self):
        """计算每100克的卡路里（用于对比）"""
        if self.serving_weight_grams > 0:
            return round((self.calories * 100) / self.serving_weight_grams)
        return 0