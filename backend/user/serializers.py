from .models import User, SleepRecord, ExerciseRecord, DietRecord, FoodCalorieReference, HealthReport, GoalProgress, HealthGoal
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


class HealthReportSerializer(serializers.ModelSerializer):
    """健康报告序列化器"""
    health_grade_display = serializers.SerializerMethodField(read_only=True)
    health_trend_display = serializers.SerializerMethodField(read_only=True)
    period = serializers.SerializerMethodField(read_only=True)
    grade = serializers.SerializerMethodField(read_only=True)
    scores = serializers.SerializerMethodField(read_only=True)
    key_insights = serializers.SerializerMethodField(read_only=True)
    recommendations = serializers.SerializerMethodField(read_only=True)
    data_summary = serializers.SerializerMethodField(read_only=True)
    detailed_analysis = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = HealthReport
        fields = [
            'id', 'report_date', 'period_start', 'period_end', 'period',
            'overall_score', 'sleep_score', 'exercise_score', 'diet_score',
            'scores', 'health_grade', 'health_grade_display', 'grade',
            'health_trend', 'health_trend_display',
            'key_insights', 'recommendations', 'data_summary', 'detailed_analysis',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_health_grade_display(self, obj):
        return obj.get_health_grade_display()
    
    def get_health_trend_display(self, obj):
        return obj.get_health_trend_display()
    
    def get_period(self, obj):
        return obj.get_period_display()
    
    def get_grade(self, obj):
        # 返回英文的等级简写
        grade_map = {
            'excellent': 'Excellent',
            'good': 'Good',
            'fair': 'Fair',
            'needs_improvement': 'Needs Improvement',
            'poor': 'Poor'
        }
        return grade_map.get(obj.health_grade, 'Unknown')
    
    def get_scores(self, obj):
        """返回各维度评分字典"""
        return {
            'sleep': obj.sleep_score,
            'exercise': obj.exercise_score,
            'diet': obj.diet_score
        }
    
    def get_key_insights(self, obj):
        """返回关键洞察列表"""
        return obj.get_key_insights_list()
    
    def get_recommendations(self, obj):
        """返回健康建议列表"""
        return obj.get_recommendations_list()
    
    def get_data_summary(self, obj):
        """返回数据摘要"""
        return obj.get_data_summary_dict()
    
    def get_detailed_analysis(self, obj):
        """返回详细分析"""
        return obj.get_detailed_analysis_dict()


class HealthReportListSerializer(serializers.ModelSerializer):
    """健康报告列表序列化器（简化版）"""
    period = serializers.SerializerMethodField(read_only=True)
    grade = serializers.SerializerMethodField(read_only=True)
    health_grade_display = serializers.SerializerMethodField(read_only=True)
    health_trend_display = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = HealthReport
        fields = [
            'id', 'report_date', 'period', 'overall_score', 
            'health_grade', 'health_grade_display', 'grade',
            'health_trend', 'health_trend_display', 'created_at'
        ]
    
    def get_period(self, obj):
        return obj.get_period_display()
    
    def get_grade(self, obj):
        grade_map = {
            'excellent': 'Excellent',
            'good': 'Good',
            'fair': 'Fair',
            'needs_improvement': 'Needs Improvement',
            'poor': 'Poor'
        }
        return grade_map.get(obj.health_grade, 'Unknown')
    
    def get_health_grade_display(self, obj):
        return obj.get_health_grade_display()
    
    def get_health_trend_display(self, obj):
        return obj.get_health_trend_display()


class HealthReportGenerateSerializer(serializers.Serializer):
    """生成健康报告的请求序列化器"""
    period_days = serializers.IntegerField(default=7, min_value=1, max_value=30)
    
    def validate_period_days(self, value):
        """验证统计周期"""
        if value < 1:
            raise serializers.ValidationError("统计周期不能少于1天")
        if value > 30:
            raise serializers.ValidationError("统计周期不能超过30天")
        return value


class HealthReportStatisticsSerializer(serializers.Serializer):
    """健康报告统计序列化器"""
    total_reports = serializers.IntegerField(read_only=True)
    average_overall_score = serializers.FloatField(read_only=True)
    best_score = serializers.IntegerField(read_only=True)
    worst_score = serializers.IntegerField(read_only=True)
    improvement_trend = serializers.CharField(read_only=True)
    score_history = serializers.ListField(read_only=True)
    category_averages = serializers.DictField(read_only=True)


class GoalProgressSerializer(serializers.ModelSerializer):
    """目标进度记录序列化器"""
    
    class Meta:
        model = GoalProgress
        fields = ['id', 'date', 'value', 'notes', 'created_at']
        read_only_fields = ['created_at']


class HealthGoalSerializer(serializers.ModelSerializer):
    """健康目标序列化器"""
    progress_percentage = serializers.ReadOnlyField()
    progress_color = serializers.SerializerMethodField(read_only=True)
    status_color = serializers.SerializerMethodField(read_only=True)
    achievement_level = serializers.SerializerMethodField(read_only=True)
    days_remaining = serializers.SerializerMethodField(read_only=True)
    is_overdue = serializers.SerializerMethodField(read_only=True)
    recent_progress = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = HealthGoal
        fields = [
            'id', 'goal_type', 'title', 'description',
            'target_value', 'current_value', 'unit',
            'frequency', 'start_date', 'end_date',
            'status', 'progress_percentage', 'progress_color',
            'status_color', 'achievement_level', 'days_remaining',
            'is_overdue', 'reminder_enabled', 'reminder_time',
            'recent_progress', 'created_at', 'updated_at'
        ]
        read_only_fields = ['progress_percentage', 'created_at', 'updated_at']
    
    def get_progress_color(self, obj):
        return obj.get_progress_color()
    
    def get_status_color(self, obj):
        return obj.get_status_display_color()
    
    def get_achievement_level(self, obj):
        return obj.get_achievement_level()
    
    def get_days_remaining(self, obj):
        return obj.days_remaining()
    
    def get_is_overdue(self, obj):
        return obj.is_overdue()
    
    def get_recent_progress(self, obj):
        """获取最近7天的进度记录"""
        from datetime import date, timedelta
        end_date = date.today()
        start_date = end_date - timedelta(days=6)
        
        progress_records = obj.progress_records.filter(
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        return GoalProgressSerializer(progress_records, many=True).data


class HealthGoalCreateSerializer(serializers.ModelSerializer):
    """创建健康目标序列化器"""
    
    class Meta:
        model = HealthGoal
        fields = [
            'goal_type', 'title', 'description',
            'target_value', 'unit', 'frequency',
            'start_date', 'end_date',
            'reminder_enabled', 'reminder_time'
        ]
    
    def validate_end_date(self, value):
        """验证结束日期"""
        start_date = self.initial_data.get('start_date')
        if start_date and value <= datetime.strptime(start_date, '%Y-%m-%d').date():
            raise serializers.ValidationError("结束日期必须晚于开始日期")
        return value
    
    def validate_target_value(self, value):
        """验证目标数值"""
        if value <= 0:
            raise serializers.ValidationError("目标数值必须大于0")
        return value


class HealthGoalStatsSerializer(serializers.Serializer):
    """健康目标统计序列化器"""
    total_goals = serializers.IntegerField(read_only=True)
    active_goals = serializers.IntegerField(read_only=True)
    completed_goals = serializers.IntegerField(read_only=True)
    completion_rate = serializers.FloatField(read_only=True)
    average_progress = serializers.FloatField(read_only=True)
    goals_by_type = serializers.DictField(read_only=True)
    recent_achievements = serializers.ListField(read_only=True)