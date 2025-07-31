from .models import User, SleepRecord, ExerciseRecord, DietRecord, FoodCalorieReference
from rest_framework import serializers
from .utils import verify_user_password
from datetime import datetime, date

class LoginSerializer(serializers.Serializer):
    userName = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )
    
    def validate(self, data):
        username = data.get('userName')
        password = data.get('password')
        
        try:
            user = User.objects.get(userName=username)
        except User.DoesNotExist:
            raise serializers.ValidationError("用户名或密码错误")
            
        if not verify_user_password(user, password):
            raise serializers.ValidationError("用户名或密码错误")
            
        # 返回用户对象
        data['user'] = user
        return data


class SleepRecordSerializer(serializers.ModelSerializer):
    sleep_quality_score = serializers.SerializerMethodField(read_only=True)
    sleep_duration_hours = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = SleepRecord
        fields = [
            'id', 'sleep_date', 'bedtime', 'wake_time', 
            'sleep_duration', 'sleep_duration_hours', 'sleep_quality_score',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['sleep_duration', 'created_at', 'updated_at']
    
    def get_sleep_quality_score(self, obj):
        return obj.get_sleep_quality_score()
    
    def get_sleep_duration_hours(self, obj):
        if obj.sleep_duration:
            return round(obj.sleep_duration / 60, 1)
        return 0
    
    def validate_sleep_date(self, value):
        """验证睡眠日期不能是未来日期"""
        if value > date.today():
            raise serializers.ValidationError("睡眠日期不能是未来日期")
        return value
    
    def validate(self, data):
        """验证睡眠时长合理性"""
        bedtime = data.get('bedtime')
        wake_time = data.get('wake_time')
        sleep_date = data.get('sleep_date')
        
        if bedtime and wake_time and sleep_date:
            # 临时计算睡眠时长进行验证
            temp_record = SleepRecord(
                sleep_date=sleep_date,
                bedtime=bedtime,
                wake_time=wake_time
            )
            duration_minutes = temp_record._calculate_sleep_duration()
            duration_hours = duration_minutes / 60
            
            # 检查睡眠时长合理性（4-12小时）
            if duration_hours < 4 or duration_hours > 12:
                raise serializers.ValidationError(
                    f"睡眠时长不合理：{duration_hours:.1f}小时。建议范围：4-12小时"
                )
        
        return data


class WeeklySleepStatsSerializer(serializers.Serializer):
    """一周睡眠统计数据序列化器"""
    records = SleepRecordSerializer(many=True, read_only=True)
    average_sleep_duration = serializers.FloatField(read_only=True)
    average_sleep_hours = serializers.FloatField(read_only=True)
    average_quality_score = serializers.FloatField(read_only=True)
    total_records = serializers.IntegerField(read_only=True)
    sleep_regularity = serializers.CharField(read_only=True)
    recommendations = serializers.ListField(read_only=True)


class ExerciseRecordSerializer(serializers.ModelSerializer):
    exercise_type_display = serializers.SerializerMethodField(read_only=True)
    exercise_intensity = serializers.SerializerMethodField(read_only=True)
    duration_hours = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = ExerciseRecord
        fields = [
            'id', 'exercise_date', 'exercise_type', 'exercise_type_display',
            'duration_minutes', 'duration_hours', 'calories_burned', 
            'exercise_intensity', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_exercise_type_display(self, obj):
        return obj.get_exercise_type_display()
    
    def get_exercise_intensity(self, obj):
        return obj.get_exercise_intensity()
    
    def get_duration_hours(self, obj):
        return round(obj.duration_minutes / 60, 1)
    
    def validate_exercise_date(self, value):
        """验证运动日期不能是未来日期"""
        if value > date.today():
            raise serializers.ValidationError("运动日期不能是未来日期")
        return value
    
    def validate_duration_minutes(self, value):
        """验证运动时长合理性"""
        if value < 5:
            raise serializers.ValidationError("运动时长不能少于5分钟")
        if value > 480:  # 8小时
            raise serializers.ValidationError("运动时长不能超过8小时")
        return value
    
    def validate_calories_burned(self, value):
        """验证卡路里消耗合理性"""
        if value is not None and value <= 0:
            raise serializers.ValidationError("卡路里消耗必须为正数")
        return value


class WeeklyExerciseStatsSerializer(serializers.Serializer):
    """一周运动统计数据序列化器"""
    records = ExerciseRecordSerializer(many=True, read_only=True)
    total_duration_minutes = serializers.IntegerField(read_only=True)
    total_duration_hours = serializers.FloatField(read_only=True)
    total_calories_burned = serializers.IntegerField(read_only=True)
    average_daily_duration = serializers.FloatField(read_only=True)
    average_daily_calories = serializers.FloatField(read_only=True)
    most_frequent_exercise = serializers.CharField(read_only=True)
    exercise_frequency = serializers.IntegerField(read_only=True)
    fitness_score = serializers.IntegerField(read_only=True)
    recommendations = serializers.ListField(read_only=True)


class FoodCalorieReferenceSerializer(serializers.ModelSerializer):
    """食物卡路里参考序列化器"""
    food_category_display = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = FoodCalorieReference
        fields = [
            'id', 'food_name', 'calories_per_100g', 'food_category', 
            'food_category_display', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_food_category_display(self, obj):
        return obj.get_food_category_display()


class DietRecordSerializer(serializers.ModelSerializer):
    """饮食记录序列化器"""
    meal_type_display = serializers.SerializerMethodField(read_only=True)
    meal_type_order = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = DietRecord
        fields = [
            'id', 'diet_date', 'meal_type', 'meal_type_display', 'meal_type_order',
            'food_name', 'portion_size', 'calories_per_100g', 'total_calories',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['total_calories', 'created_at', 'updated_at']
    
    def get_meal_type_display(self, obj):
        return obj.get_meal_type_display()
    
    def get_meal_type_order(self, obj):
        return obj.get_meal_type_display_order()
    
    def validate_diet_date(self, value):
        """验证饮食日期不能是未来日期"""
        if value > date.today():
            raise serializers.ValidationError("饮食日期不能是未来日期")
        return value
    
    def validate_food_name(self, value):
        """验证食物名称"""
        if len(value.strip()) == 0:
            raise serializers.ValidationError("食物名称不能为空")
        if len(value) > 50:
            raise serializers.ValidationError("食物名称不能超过50个字符")
        return value.strip()
    
    def validate_portion_size(self, value):
        """验证食物分量合理性"""
        if value < 1:
            raise serializers.ValidationError("食物分量不能少于1克")
        if value > 2000:
            raise serializers.ValidationError("食物分量不能超过2000克")
        return value
    
    def validate_calories_per_100g(self, value):
        """验证卡路里值合理性"""
        if value <= 0:
            raise serializers.ValidationError("每100g卡路里必须为正数")
        if value > 900:  # 最高热量食物约900kcal/100g
            raise serializers.ValidationError("每100g卡路里值过高，请检查数据")
        return value


class WeeklyDietStatsSerializer(serializers.Serializer):
    """一周饮食统计数据序列化器"""
    records = DietRecordSerializer(many=True, read_only=True)
    total_calories = serializers.IntegerField(read_only=True)
    average_daily_calories = serializers.FloatField(read_only=True)
    meal_distribution = serializers.DictField(read_only=True)  # 各餐次卡路里分布
    food_variety_score = serializers.IntegerField(read_only=True)  # 食物多样性评分
    nutrition_balance_score = serializers.IntegerField(read_only=True)  # 营养均衡评分
    daily_calories_target = serializers.IntegerField(read_only=True, default=2000)  # 每日推荐摄入量
    target_achievement_rate = serializers.FloatField(read_only=True)  # 目标达成率
    recommendations = serializers.ListField(read_only=True)