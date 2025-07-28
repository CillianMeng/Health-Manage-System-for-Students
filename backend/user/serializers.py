from .models import User, SleepRecord, ExerciseRecord, FoodItem, DietRecord
from rest_framework import serializers
from .utils import verify_user_password

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
    sleep_duration_hours = serializers.ReadOnlyField()
    user_name = serializers.CharField(source='user.userName', read_only=True)
    
    class Meta:
        model = SleepRecord
        fields = ['id', 'user', 'user_name', 'date', 'sleep_time', 'wake_time', 
                 'sleep_duration', 'sleep_duration_hours', 'created_at', 'updated_at']
        read_only_fields = ['sleep_duration', 'created_at', 'updated_at']

    def validate(self, data):
        # 检查日期不能是未来
        from datetime import date
        if data.get('date') and data['date'] > date.today():
            raise serializers.ValidationError("不能记录未来的睡眠数据")
        
        return data

class SleepRecordCreateSerializer(serializers.ModelSerializer):
    """创建睡眠记录的序列化器（不需要传user_id，从session获取）"""
    
    class Meta:
        model = SleepRecord
        fields = ['date', 'sleep_time', 'wake_time']

    def validate(self, data):
        from datetime import date
        if data.get('date') and data['date'] > date.today():
            raise serializers.ValidationError("不能记录未来的睡眠数据")
        
        return data

class ExerciseRecordSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.userName', read_only=True)
    exercise_type_display = serializers.CharField(source='get_exercise_type_display', read_only=True)
    duration_hours = serializers.ReadOnlyField()
    intensity_level = serializers.CharField(source='get_intensity_level', read_only=True)
    
    class Meta:
        model = ExerciseRecord
        fields = ['id', 'user', 'user_name', 'date', 'exercise_type', 'exercise_type_display',
                 'duration_minutes', 'duration_hours', 'calories_burned', 'intensity_level',
                 'notes', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        # 检查日期不能是未来
        from datetime import date
        if data.get('date') and data['date'] > date.today():
            raise serializers.ValidationError("不能记录未来的运动数据")
        
        # 检查运动时长合理性
        if data.get('duration_minutes') and data['duration_minutes'] > 600:  # 10小时
            raise serializers.ValidationError("单次运动时长不能超过10小时")
        
        # 检查卡路里消耗合理性
        if data.get('calories_burned') and data['calories_burned'] > 3000:
            raise serializers.ValidationError("单次运动消耗卡路里不能超过3000")
        
        return data

class ExerciseRecordCreateSerializer(serializers.ModelSerializer):
    """创建运动记录的序列化器（不需要传user_id，从session获取）"""
    
    class Meta:
        model = ExerciseRecord
        fields = ['date', 'exercise_type', 'duration_minutes', 'calories_burned', 'notes']

    def validate(self, data):
        from datetime import date
        if data.get('date') and data['date'] > date.today():
            raise serializers.ValidationError("不能记录未来的运动数据")
        
        if data.get('duration_minutes') and data['duration_minutes'] > 600:
            raise serializers.ValidationError("单次运动时长不能超过10小时")
        
        if data.get('calories_burned') and data['calories_burned'] > 3000:
            raise serializers.ValidationError("单次运动消耗卡路里不能超过3000")
        
        return data

class FoodItemSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = FoodItem
        fields = ['id', 'name', 'category', 'category_display', 'calories_per_100g', 
                 'protein_per_100g', 'fat_per_100g', 'carbs_per_100g',
                 'common_serving_size', 'common_serving_calories']

class DietRecordSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.userName', read_only=True)
    meal_type_display = serializers.CharField(source='get_meal_type_display', read_only=True)
    food_item_name = serializers.CharField(source='food_item.name', read_only=True)
    food_item_category = serializers.CharField(source='food_item.get_category_display', read_only=True)
    calories_per_100g = serializers.ReadOnlyField()
    
    class Meta:
        model = DietRecord
        fields = ['id', 'user', 'user_name', 'date', 'meal_type', 'meal_type_display',
                 'food_item', 'food_item_name', 'food_item_category', 'food_name', 
                 'serving_size', 'serving_weight_grams', 'calories', 'calories_per_100g',
                 'notes', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        # 检查日期不能是未来
        from datetime import date
        if data.get('date') and data['date'] > date.today():
            raise serializers.ValidationError("不能记录未来的饮食数据")
        
        # 检查分量重量合理性
        if data.get('serving_weight_grams') and data['serving_weight_grams'] > 2000:  # 2kg
            raise serializers.ValidationError("单次饮食分量不能超过2000克")
        
        # 检查卡路里合理性
        if data.get('calories') and data['calories'] > 5000:
            raise serializers.ValidationError("单次饮食卡路里不能超过5000")
        
        # 如果选择了食物数据库中的食物，验证food_name是否与数据库一致
        if data.get('food_item') and data.get('food_name'):
            if data['food_name'] != data['food_item'].name:
                # 允许用户修改食物名称，但给出提示
                pass
        
        return data

class DietRecordCreateSerializer(serializers.ModelSerializer):
    """创建饮食记录的序列化器（不需要传user_id，从session获取）"""
    
    class Meta:
        model = DietRecord
        fields = ['date', 'meal_type', 'food_item', 'food_name', 'serving_size', 
                 'serving_weight_grams', 'calories', 'notes']

    def validate(self, data):
        from datetime import date
        if data.get('date') and data['date'] > date.today():
            raise serializers.ValidationError("不能记录未来的饮食数据")
        
        if data.get('serving_weight_grams') and data['serving_weight_grams'] > 2000:
            raise serializers.ValidationError("单次饮食分量不能超过2000克")
        
        if data.get('calories') and data['calories'] > 5000:
            raise serializers.ValidationError("单次饮食卡路里不能超过5000")
        
        # 确保至少有食物名称或食物项目之一
        if not data.get('food_name') and not data.get('food_item'):
            raise serializers.ValidationError("必须提供食物名称或选择食物数据库中的食物")
        
        return data