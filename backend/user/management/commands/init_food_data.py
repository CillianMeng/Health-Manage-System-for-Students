from django.core.management.base import BaseCommand
from user.models import FoodItem

class Command(BaseCommand):
    help = '初始化食物数据库，添加常见中式食物及其卡路里信息'

    def handle(self, *args, **options):
        # 清空现有数据（可选）
        if self.confirm_action("是否清空现有食物数据？"):
            FoodItem.objects.all().delete()
            self.stdout.write(self.style.WARNING('已清空现有食物数据'))

        # 食物数据 - 基于中国食物成分表和常见食物
        foods_data = [
            # 谷物类
            {'name': '白米饭', 'category': 'grains', 'calories_per_100g': 116, 'protein_per_100g': 2.6, 'fat_per_100g': 0.3, 'carbs_per_100g': 25.9, 'common_serving_size': '1碗(150g)', 'common_serving_calories': 174},
            {'name': '糙米饭', 'category': 'grains', 'calories_per_100g': 112, 'protein_per_100g': 2.5, 'fat_per_100g': 0.9, 'carbs_per_100g': 22.9, 'common_serving_size': '1碗(150g)', 'common_serving_calories': 168},
            {'name': '白面条', 'category': 'grains', 'calories_per_100g': 138, 'protein_per_100g': 4.5, 'fat_per_100g': 0.5, 'carbs_per_100g': 28.0, 'common_serving_size': '1碗(200g)', 'common_serving_calories': 276},
            {'name': '全麦面条', 'category': 'grains', 'calories_per_100g': 124, 'protein_per_100g': 5.0, 'fat_per_100g': 0.9, 'carbs_per_100g': 25.0, 'common_serving_size': '1碗(200g)', 'common_serving_calories': 248},
            {'name': '小馒头', 'category': 'grains', 'calories_per_100g': 221, 'protein_per_100g': 7.0, 'fat_per_100g': 1.1, 'carbs_per_100g': 47.0, 'common_serving_size': '1个(50g)', 'common_serving_calories': 111},
            {'name': '白面包', 'category': 'grains', 'calories_per_100g': 266, 'protein_per_100g': 8.5, 'fat_per_100g': 3.1, 'carbs_per_100g': 51.0, 'common_serving_size': '1片(25g)', 'common_serving_calories': 67},
            {'name': '燕麦片', 'category': 'grains', 'calories_per_100g': 367, 'protein_per_100g': 15.0, 'fat_per_100g': 6.2, 'carbs_per_100g': 61.0, 'common_serving_size': '1碗冲泡(30g)', 'common_serving_calories': 110},
            {'name': '小米粥', 'category': 'grains', 'calories_per_100g': 46, 'protein_per_100g': 1.5, 'fat_per_100g': 0.1, 'carbs_per_100g': 9.0, 'common_serving_size': '1碗(200g)', 'common_serving_calories': 92},

            # 蔬菜类
            {'name': '白菜', 'category': 'vegetables', 'calories_per_100g': 21, 'protein_per_100g': 1.5, 'fat_per_100g': 0.1, 'carbs_per_100g': 4.0, 'common_serving_size': '1盘(150g)', 'common_serving_calories': 32},
            {'name': '菠菜', 'category': 'vegetables', 'calories_per_100g': 28, 'protein_per_100g': 2.6, 'fat_per_100g': 0.3, 'carbs_per_100g': 4.5, 'common_serving_size': '1盘(100g)', 'common_serving_calories': 28},
            {'name': '西红柿', 'category': 'vegetables', 'calories_per_100g': 19, 'protein_per_100g': 0.9, 'fat_per_100g': 0.2, 'carbs_per_100g': 4.0, 'common_serving_size': '1个中等(150g)', 'common_serving_calories': 29},
            {'name': '黄瓜', 'category': 'vegetables', 'calories_per_100g': 15, 'protein_per_100g': 0.8, 'fat_per_100g': 0.1, 'carbs_per_100g': 2.9, 'common_serving_size': '1根(200g)', 'common_serving_calories': 30},
            {'name': '胡萝卜', 'category': 'vegetables', 'calories_per_100g': 39, 'protein_per_100g': 1.0, 'fat_per_100g': 0.2, 'carbs_per_100g': 8.8, 'common_serving_size': '1根中等(100g)', 'common_serving_calories': 39},
            {'name': '土豆', 'category': 'vegetables', 'calories_per_100g': 81, 'protein_per_100g': 2.0, 'fat_per_100g': 0.1, 'carbs_per_100g': 18.4, 'common_serving_size': '1个中等(150g)', 'common_serving_calories': 122},
            {'name': '西兰花', 'category': 'vegetables', 'calories_per_100g': 33, 'protein_per_100g': 4.1, 'fat_per_100g': 0.6, 'carbs_per_100g': 4.3, 'common_serving_size': '1盘(150g)', 'common_serving_calories': 50},
            {'name': '韭菜', 'category': 'vegetables', 'calories_per_100g': 26, 'protein_per_100g': 2.4, 'fat_per_100g': 0.4, 'carbs_per_100g': 4.6, 'common_serving_size': '1盘(100g)', 'common_serving_calories': 26},

            # 水果类
            {'name': '苹果', 'category': 'fruits', 'calories_per_100g': 54, 'protein_per_100g': 0.2, 'fat_per_100g': 0.2, 'carbs_per_100g': 13.5, 'common_serving_size': '1个中等(150g)', 'common_serving_calories': 81},
            {'name': '香蕉', 'category': 'fruits', 'calories_per_100g': 93, 'protein_per_100g': 1.4, 'fat_per_100g': 0.2, 'carbs_per_100g': 22.0, 'common_serving_size': '1根(100g)', 'common_serving_calories': 93},
            {'name': '橙子', 'category': 'fruits', 'calories_per_100g': 48, 'protein_per_100g': 0.8, 'fat_per_100g': 0.2, 'carbs_per_100g': 11.7, 'common_serving_size': '1个(150g)', 'common_serving_calories': 72},
            {'name': '葡萄', 'category': 'fruits', 'calories_per_100g': 65, 'protein_per_100g': 0.6, 'fat_per_100g': 0.4, 'carbs_per_100g': 16.7, 'common_serving_size': '一串小(100g)', 'common_serving_calories': 65},
            {'name': '草莓', 'category': 'fruits', 'calories_per_100g': 30, 'protein_per_100g': 1.0, 'fat_per_100g': 0.2, 'carbs_per_100g': 7.0, 'common_serving_size': '10颗(100g)', 'common_serving_calories': 30},
            {'name': '西瓜', 'category': 'fruits', 'calories_per_100g': 25, 'protein_per_100g': 0.6, 'fat_per_100g': 0.1, 'carbs_per_100g': 6.2, 'common_serving_size': '1块(200g)', 'common_serving_calories': 50},

            # 肉类
            {'name': '鸡胸肉', 'category': 'meat', 'calories_per_100g': 133, 'protein_per_100g': 19.4, 'fat_per_100g': 5.0, 'carbs_per_100g': 2.5, 'common_serving_size': '1块(100g)', 'common_serving_calories': 133},
            {'name': '猪瘦肉', 'category': 'meat', 'calories_per_100g': 155, 'protein_per_100g': 20.3, 'fat_per_100g': 7.9, 'carbs_per_100g': 1.2, 'common_serving_size': '100g', 'common_serving_calories': 155},
            {'name': '牛瘦肉', 'category': 'meat', 'calories_per_100g': 125, 'protein_per_100g': 20.2, 'fat_per_100g': 4.2, 'carbs_per_100g': 2.0, 'common_serving_size': '100g', 'common_serving_calories': 125},
            {'name': '羊肉', 'category': 'meat', 'calories_per_100g': 118, 'protein_per_100g': 19.0, 'fat_per_100g': 4.5, 'carbs_per_100g': 0.7, 'common_serving_size': '100g', 'common_serving_calories': 118},
            {'name': '鸡蛋', 'category': 'meat', 'calories_per_100g': 139, 'protein_per_100g': 13.3, 'fat_per_100g': 8.8, 'carbs_per_100g': 2.8, 'common_serving_size': '1个(50g)', 'common_serving_calories': 70},

            # 海鲜类
            {'name': '草鱼', 'category': 'seafood', 'calories_per_100g': 124, 'protein_per_100g': 18.1, 'fat_per_100g': 5.2, 'carbs_per_100g': 0.0, 'common_serving_size': '100g', 'common_serving_calories': 124},
            {'name': '带鱼', 'category': 'seafood', 'calories_per_100g': 127, 'protein_per_100g': 17.7, 'fat_per_100g': 5.6, 'carbs_per_100g': 0.0, 'common_serving_size': '100g', 'common_serving_calories': 127},
            {'name': '虾', 'category': 'seafood', 'calories_per_100g': 87, 'protein_per_100g': 18.6, 'fat_per_100g': 1.2, 'carbs_per_100g': 0.8, 'common_serving_size': '10只(80g)', 'common_serving_calories': 70},

            # 乳制品
            {'name': '牛奶', 'category': 'dairy', 'calories_per_100g': 66, 'protein_per_100g': 3.2, 'fat_per_100g': 3.8, 'carbs_per_100g': 4.7, 'common_serving_size': '1杯(250ml)', 'common_serving_calories': 165},
            {'name': '酸奶', 'category': 'dairy', 'calories_per_100g': 72, 'protein_per_100g': 2.9, 'fat_per_100g': 2.7, 'carbs_per_100g': 9.3, 'common_serving_size': '1杯(150g)', 'common_serving_calories': 108},
            {'name': '奶酪', 'category': 'dairy', 'calories_per_100g': 328, 'protein_per_100g': 25.0, 'fat_per_100g': 23.0, 'carbs_per_100g': 3.5, 'common_serving_size': '1片(20g)', 'common_serving_calories': 66},

            # 坚果类
            {'name': '花生', 'category': 'nuts', 'calories_per_100g': 563, 'protein_per_100g': 21.7, 'fat_per_100g': 48.0, 'carbs_per_100g': 23.8, 'common_serving_size': '一把(30g)', 'common_serving_calories': 169},
            {'name': '核桃', 'category': 'nuts', 'calories_per_100g': 627, 'protein_per_100g': 15.4, 'fat_per_100g': 58.8, 'carbs_per_100g': 19.1, 'common_serving_size': '5个(30g)', 'common_serving_calories': 188},
            {'name': '杏仁', 'category': 'nuts', 'calories_per_100g': 578, 'protein_per_100g': 22.0, 'fat_per_100g': 51.4, 'carbs_per_100g': 19.5, 'common_serving_size': '一把(28g)', 'common_serving_calories': 162},

            # 饮品类
            {'name': '绿茶', 'category': 'beverages', 'calories_per_100g': 0, 'protein_per_100g': 0.0, 'fat_per_100g': 0.0, 'carbs_per_100g': 0.0, 'common_serving_size': '1杯(250ml)', 'common_serving_calories': 0},
            {'name': '咖啡(黑)', 'category': 'beverages', 'calories_per_100g': 1, 'protein_per_100g': 0.1, 'fat_per_100g': 0.0, 'carbs_per_100g': 0.0, 'common_serving_size': '1杯(250ml)', 'common_serving_calories': 3},
            {'name': '可乐', 'category': 'beverages', 'calories_per_100g': 43, 'protein_per_100g': 0.0, 'fat_per_100g': 0.0, 'carbs_per_100g': 10.6, 'common_serving_size': '1罐(330ml)', 'common_serving_calories': 142},
            {'name': '橙汁', 'category': 'beverages', 'calories_per_100g': 45, 'protein_per_100g': 0.5, 'fat_per_100g': 0.1, 'carbs_per_100g': 11.0, 'common_serving_size': '1杯(250ml)', 'common_serving_calories': 113},
            {'name': '豆浆', 'category': 'beverages', 'calories_per_100g': 16, 'protein_per_100g': 1.8, 'fat_per_100g': 0.7, 'carbs_per_100g': 1.1, 'common_serving_size': '1杯(250ml)', 'common_serving_calories': 40},

            # 零食类
            {'name': '薯片', 'category': 'snacks', 'calories_per_100g': 547, 'protein_per_100g': 6.0, 'fat_per_100g': 37.0, 'carbs_per_100g': 50.0, 'common_serving_size': '1小包(28g)', 'common_serving_calories': 153},
            {'name': '巧克力', 'category': 'snacks', 'calories_per_100g': 531, 'protein_per_100g': 4.9, 'fat_per_100g': 31.0, 'carbs_per_100g': 63.0, 'common_serving_size': '1块(20g)', 'common_serving_calories': 106},
            {'name': '饼干', 'category': 'snacks', 'calories_per_100g': 433, 'protein_per_100g': 7.0, 'fat_per_100g': 14.0, 'carbs_per_100g': 71.0, 'common_serving_size': '3片(30g)', 'common_serving_calories': 130},

            # 调料油脂
            {'name': '食用油', 'category': 'cooking_oil', 'calories_per_100g': 899, 'protein_per_100g': 0.0, 'fat_per_100g': 99.9, 'carbs_per_100g': 0.0, 'common_serving_size': '1勺(10ml)', 'common_serving_calories': 90},
            {'name': '蜂蜜', 'category': 'cooking_oil', 'calories_per_100g': 321, 'protein_per_100g': 0.4, 'fat_per_100g': 0.0, 'carbs_per_100g': 80.9, 'common_serving_size': '1勺(20g)', 'common_serving_calories': 64},
            {'name': '白糖', 'category': 'cooking_oil', 'calories_per_100g': 400, 'protein_per_100g': 0.0, 'fat_per_100g': 0.0, 'carbs_per_100g': 99.9, 'common_serving_size': '1勺(10g)', 'common_serving_calories': 40},
        ]

        # 批量创建食物数据
        created_count = 0
        for food_data in foods_data:
            food_item, created = FoodItem.objects.get_or_create(
                name=food_data['name'],
                defaults=food_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'已添加: {food_item.name}')
            else:
                self.stdout.write(f'已存在: {food_item.name}')

        self.stdout.write(
            self.style.SUCCESS(f'食物数据库初始化完成！共添加 {created_count} 种新食物，数据库中现有 {FoodItem.objects.count()} 种食物。')
        )

    def confirm_action(self, message):
        """确认操作"""
        confirm = input(f"{message} [y/N]: ")
        return confirm.lower() in ['y', 'yes']
