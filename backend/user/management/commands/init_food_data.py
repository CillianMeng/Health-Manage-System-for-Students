from django.core.management.base import BaseCommand
from user.models import FoodCalorieReference


class Command(BaseCommand):
    help = '初始化食物卡路里参考数据'

    def handle(self, *args, **options):
        # 定义常见食物数据
        food_data = [
            # 主食类
            {'food_name': '米饭', 'calories_per_100g': 116, 'food_category': 'staple', 'description': '煮熟的白米饭'},
            {'food_name': '面条', 'calories_per_100g': 109, 'food_category': 'staple', 'description': '煮熟的面条'},
            {'food_name': '面包', 'calories_per_100g': 265, 'food_category': 'staple', 'description': '白面包'},
            {'food_name': '馒头', 'calories_per_100g': 221, 'food_category': 'staple', 'description': '普通馒头'},
            {'food_name': '包子', 'calories_per_100g': 120, 'food_category': 'staple', 'description': '肉包子'},
            {'food_name': '饺子', 'calories_per_100g': 240, 'food_category': 'staple', 'description': '猪肉饺子'},
            {'food_name': '意大利面', 'calories_per_100g': 131, 'food_category': 'staple', 'description': '煮熟的意大利面'},
            
            # 蔬菜类
            {'food_name': '白菜', 'calories_per_100g': 17, 'food_category': 'vegetable', 'description': '新鲜白菜'},
            {'food_name': '西红柿', 'calories_per_100g': 19, 'food_category': 'vegetable', 'description': '新鲜西红柿'},
            {'food_name': '黄瓜', 'calories_per_100g': 15, 'food_category': 'vegetable', 'description': '新鲜黄瓜'},
            {'food_name': '胡萝卜', 'calories_per_100g': 41, 'food_category': 'vegetable', 'description': '新鲜胡萝卜'},
            {'food_name': '土豆', 'calories_per_100g': 76, 'food_category': 'vegetable', 'description': '生土豆'},
            {'food_name': '西兰花', 'calories_per_100g': 34, 'food_category': 'vegetable', 'description': '新鲜西兰花'},
            {'food_name': '菠菜', 'calories_per_100g': 23, 'food_category': 'vegetable', 'description': '新鲜菠菜'},
            {'food_name': '芹菜', 'calories_per_100g': 16, 'food_category': 'vegetable', 'description': '新鲜芹菜'},
            
            # 水果类
            {'food_name': '苹果', 'calories_per_100g': 54, 'food_category': 'fruit', 'description': '新鲜苹果'},
            {'food_name': '香蕉', 'calories_per_100g': 89, 'food_category': 'fruit', 'description': '新鲜香蕉'},
            {'food_name': '橙子', 'calories_per_100g': 47, 'food_category': 'fruit', 'description': '新鲜橙子'},
            {'food_name': '葡萄', 'calories_per_100g': 69, 'food_category': 'fruit', 'description': '新鲜葡萄'},
            {'food_name': '西瓜', 'calories_per_100g': 26, 'food_category': 'fruit', 'description': '新鲜西瓜'},
            {'food_name': '草莓', 'calories_per_100g': 32, 'food_category': 'fruit', 'description': '新鲜草莓'},
            {'food_name': '桃子', 'calories_per_100g': 39, 'food_category': 'fruit', 'description': '新鲜桃子'},
            {'food_name': '梨', 'calories_per_100g': 57, 'food_category': 'fruit', 'description': '新鲜梨'},
            
            # 肉类
            {'food_name': '猪肉', 'calories_per_100g': 143, 'food_category': 'meat', 'description': '瘦猪肉'},
            {'food_name': '牛肉', 'calories_per_100g': 125, 'food_category': 'meat', 'description': '瘦牛肉'},
            {'food_name': '鸡肉', 'calories_per_100g': 167, 'food_category': 'meat', 'description': '去皮鸡胸肉'},
            {'food_name': '鱼肉', 'calories_per_100g': 104, 'food_category': 'meat', 'description': '淡水鱼肉'},
            {'food_name': '鸡蛋', 'calories_per_100g': 144, 'food_category': 'meat', 'description': '鸡蛋'},
            {'food_name': '虾', 'calories_per_100g': 87, 'food_category': 'meat', 'description': '新鲜虾肉'},
            {'food_name': '羊肉', 'calories_per_100g': 118, 'food_category': 'meat', 'description': '瘦羊肉'},
            
            # 乳制品
            {'food_name': '牛奶', 'calories_per_100g': 54, 'food_category': 'dairy', 'description': '全脂牛奶'},
            {'food_name': '酸奶', 'calories_per_100g': 72, 'food_category': 'dairy', 'description': '普通酸奶'},
            {'food_name': '奶酪', 'calories_per_100g': 328, 'food_category': 'dairy', 'description': '硬质奶酪'},
            {'food_name': '酸奶（低脂）', 'calories_per_100g': 43, 'food_category': 'dairy', 'description': '低脂酸奶'},
            {'food_name': '牛奶（脱脂）', 'calories_per_100g': 34, 'food_category': 'dairy', 'description': '脱脂牛奶'},
            
            # 饮料类
            {'food_name': '可乐', 'calories_per_100g': 43, 'food_category': 'beverage', 'description': '碳酸饮料'},
            {'food_name': '果汁', 'calories_per_100g': 45, 'food_category': 'beverage', 'description': '混合果汁'},
            {'food_name': '啤酒', 'calories_per_100g': 32, 'food_category': 'beverage', 'description': '普通啤酒'},
            {'food_name': '白开水', 'calories_per_100g': 0, 'food_category': 'beverage', 'description': '纯净水'},
            {'food_name': '绿茶', 'calories_per_100g': 1, 'food_category': 'beverage', 'description': '无糖绿茶'},
            {'food_name': '咖啡', 'calories_per_100g': 2, 'food_category': 'beverage', 'description': '黑咖啡'},
            
            # 零食类
            {'food_name': '薯片', 'calories_per_100g': 536, 'food_category': 'snack', 'description': '油炸薯片'},
            {'food_name': '巧克力', 'calories_per_100g': 546, 'food_category': 'snack', 'description': '牛奶巧克力'},
            {'food_name': '饼干', 'calories_per_100g': 502, 'food_category': 'snack', 'description': '普通饼干'},
            {'food_name': '坚果', 'calories_per_100g': 607, 'food_category': 'snack', 'description': '混合坚果'},
            {'food_name': '爆米花', 'calories_per_100g': 382, 'food_category': 'snack', 'description': '爆米花'},
        ]

        # 清除现有数据（可选）
        # FoodCalorieReference.objects.all().delete()

        # 添加食物数据
        created_count = 0
        updated_count = 0

        for food_info in food_data:
            food, created = FoodCalorieReference.objects.get_or_create(
                food_name=food_info['food_name'],
                defaults={
                    'calories_per_100g': food_info['calories_per_100g'],
                    'food_category': food_info['food_category'],
                    'description': food_info.get('description', ''),
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'创建食物: {food.food_name}')
                )
            else:
                # 更新现有记录
                food.calories_per_100g = food_info['calories_per_100g']
                food.food_category = food_info['food_category']
                food.description = food_info.get('description', '')
                food.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'更新食物: {food.food_name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'食物数据初始化完成！创建 {created_count} 条新记录，更新 {updated_count} 条记录。'
            )
        )
