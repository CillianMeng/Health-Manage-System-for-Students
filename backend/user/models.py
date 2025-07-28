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