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