"""
健康数据分析器
用于生成健康报告和计算各种健康指标
"""
from datetime import datetime, date, timedelta
from collections import defaultdict, Counter
import statistics
from .models import User, SleepRecord, ExerciseRecord, DietRecord, HealthReport


class HealthAnalyzer:
    """健康数据分析器"""
    
    def __init__(self, user, period_days=7):
        self.user = user
        self.period_days = period_days
        self.end_date = date.today()
        self.start_date = self.end_date - timedelta(days=period_days - 1)
        
        # 获取周期内的数据
        self.sleep_records = self._get_sleep_records()
        self.exercise_records = self._get_exercise_records()
        self.diet_records = self._get_diet_records()
    
    def _get_sleep_records(self):
        """获取睡眠记录"""
        return SleepRecord.objects.filter(
            user=self.user,
            sleep_date__gte=self.start_date,
            sleep_date__lte=self.end_date
        ).order_by('sleep_date')
    
    def _get_exercise_records(self):
        """获取运动记录"""
        return ExerciseRecord.objects.filter(
            user=self.user,
            exercise_date__gte=self.start_date,
            exercise_date__lte=self.end_date
        ).order_by('exercise_date')
    
    def _get_diet_records(self):
        """获取饮食记录"""
        return DietRecord.objects.filter(
            user=self.user,
            diet_date__gte=self.start_date,
            diet_date__lte=self.end_date
        ).order_by('diet_date', 'meal_type')
    
    def calculate_sleep_score(self):
        """计算睡眠健康评分"""
        if not self.sleep_records:
            return 0
        
        # 睡眠时长评分（40%）
        duration_score = self._calculate_sleep_duration_score()
        
        # 睡眠规律评分（35%）
        regularity_score = self._calculate_sleep_regularity_score()
        
        # 睡眠质量评分（25%）
        quality_score = self._calculate_sleep_quality_score()
        
        # 加权计算总评分
        total_score = (
            duration_score * 0.4 +
            regularity_score * 0.35 +
            quality_score * 0.25
        )
        
        return min(100, max(0, int(total_score)))
    
    def _calculate_sleep_duration_score(self):
        """计算睡眠时长评分"""
        durations = [record.sleep_duration / 60 for record in self.sleep_records if record.sleep_duration]
        if not durations:
            return 0
        
        avg_duration = statistics.mean(durations)
        
        # 理想睡眠时长：7-9小时
        if 7 <= avg_duration <= 9:
            return 100
        else:
            # 距离理想时长越远分数越低
            deviation = min(abs(avg_duration - 7), abs(avg_duration - 9))
            return max(0, 100 - deviation * 10)
    
    def _calculate_sleep_regularity_score(self):
        """计算睡眠规律评分"""
        if len(self.sleep_records) < 3:
            return 60  # 数据不足时给基础分
        
        # 入睡时间方差
        bedtimes = [self._time_to_minutes(record.bedtime) for record in self.sleep_records]
        wake_times = [self._time_to_minutes(record.wake_time) for record in self.sleep_records]
        
        # 计算方差（分钟）
        bedtime_variance = statistics.variance(bedtimes) if len(bedtimes) > 1 else 0
        waketime_variance = statistics.variance(wake_times) if len(wake_times) > 1 else 0
        
        # 方差越小（越规律）分数越高
        bedtime_score = max(60, 100 - bedtime_variance / 60)
        waketime_score = max(60, 100 - waketime_variance / 60)
        
        return (bedtime_score + waketime_score) / 2
    
    def _calculate_sleep_quality_score(self):
        """计算睡眠质量评分"""
        if not self.sleep_records:
            return 0
        
        # 理想睡眠时长的天数比例
        ideal_days = sum(
            1 for record in self.sleep_records
            if record.sleep_duration and 7 * 60 <= record.sleep_duration <= 9 * 60
        )
        
        ideal_ratio = ideal_days / len(self.sleep_records)
        base_score = ideal_ratio * 100
        
        # 连续性奖励：连续记录给额外分数
        continuity_bonus = min(10, len(self.sleep_records) * 2)
        
        return min(100, base_score + continuity_bonus)
    
    def calculate_exercise_score(self):
        """计算运动健康评分"""
        if not self.exercise_records:
            return 0
        
        # 运动频率评分（35%）
        frequency_score = self._calculate_exercise_frequency_score()
        
        # 运动强度评分（40%）
        intensity_score = self._calculate_exercise_intensity_score()
        
        # 运动多样性评分（25%）
        variety_score = self._calculate_exercise_variety_score()
        
        # 加权计算总评分
        total_score = (
            frequency_score * 0.35 +
            intensity_score * 0.40 +
            variety_score * 0.25
        )
        
        return min(100, max(0, int(total_score)))
    
    def _calculate_exercise_frequency_score(self):
        """计算运动频率评分"""
        # 统计运动天数
        exercise_days = len(set(record.exercise_date for record in self.exercise_records))
        
        # 理想频率：每周4-6次（按7天周期计算）
        ideal_frequency = min(6, (self.period_days / 7) * 5)  # 每周5次为理想
        
        frequency_ratio = exercise_days / ideal_frequency
        
        if frequency_ratio >= 1:
            return 100
        else:
            return frequency_ratio * 100
    
    def _calculate_exercise_intensity_score(self):
        """计算运动强度评分"""
        total_calories = sum(record.calories_burned or 0 for record in self.exercise_records)
        
        # 目标：每周消耗1500-2500卡路里（按周期调整）
        weekly_target = 2000 * (self.period_days / 7)
        
        if weekly_target * 0.75 <= total_calories <= weekly_target * 1.25:
            return 100
        else:
            deviation = abs(total_calories - weekly_target)
            return max(0, 100 - deviation / 20)
    
    def _calculate_exercise_variety_score(self):
        """计算运动多样性评分"""
        exercise_types = set(record.exercise_type for record in self.exercise_records)
        variety_count = len(exercise_types)
        
        # 最多5种运动类型可获得满分
        return min(100, variety_count * 20)
    
    def calculate_diet_score(self):
        """计算饮食健康评分"""
        if not self.diet_records:
            return 0
        
        # 卡路里控制评分（45%）
        calorie_score = self._calculate_diet_calorie_score()
        
        # 营养均衡评分（35%）
        balance_score = self._calculate_diet_balance_score()
        
        # 饮食规律评分（20%）
        regularity_score = self._calculate_diet_regularity_score()
        
        # 加权计算总评分
        total_score = (
            calorie_score * 0.45 +
            balance_score * 0.35 +
            regularity_score * 0.20
        )
        
        return min(100, max(0, int(total_score)))
    
    def _calculate_diet_calorie_score(self):
        """计算卡路里控制评分"""
        # 按日期分组计算每日总卡路里
        daily_calories = defaultdict(int)
        for record in self.diet_records:
            daily_calories[record.diet_date] += record.total_calories or 0
        
        if not daily_calories:
            return 0
        
        avg_daily_calories = statistics.mean(daily_calories.values())
        
        # 理想摄入：1800-2200卡路里/天
        if 1800 <= avg_daily_calories <= 2200:
            return 100
        else:
            deviation = min(abs(avg_daily_calories - 1800), abs(avg_daily_calories - 2200))
            return max(0, 100 - deviation / 20)
    
    def _calculate_diet_balance_score(self):
        """计算营养均衡评分"""
        # 食物种类多样性
        food_variety = len(set(record.food_name for record in self.diet_records))
        variety_score = min(100, food_variety * 5)  # 每种食物5分，最多100分
        
        # 餐次分配合理性
        meal_distribution = self._get_meal_distribution()
        distribution_score = self._evaluate_meal_distribution(meal_distribution)
        
        return (variety_score + distribution_score) / 2
    
    def _calculate_diet_regularity_score(self):
        """计算饮食规律评分"""
        # 每日记录完整性
        record_days = len(set(record.diet_date for record in self.diet_records))
        completeness_score = (record_days / self.period_days) * 100
        
        # 用餐时间规律性（简化评估）
        meal_types = [record.meal_type for record in self.diet_records]
        meal_balance = len(set(meal_types)) / 4 * 100  # 4种餐次类型
        
        return (completeness_score + meal_balance) / 2
    
    def calculate_overall_score(self):
        """计算综合健康评分"""
        sleep_score = self.calculate_sleep_score()
        exercise_score = self.calculate_exercise_score()
        diet_score = self.calculate_diet_score()
        
        # 权重分配：睡眠35%，运动35%，饮食30%
        overall = (
            sleep_score * 0.35 +
            exercise_score * 0.35 +
            diet_score * 0.30
        )
        
        return int(overall)
    
    def generate_key_insights(self):
        """生成关键洞察"""
        insights = []
        
        # 睡眠洞察
        if self.sleep_records:
            avg_sleep = statistics.mean([r.sleep_duration / 60 for r in self.sleep_records if r.sleep_duration])
            if avg_sleep >= 8:
                insights.append("睡眠质量良好，平均睡眠时长达标")
            elif avg_sleep < 7:
                insights.append("睡眠不足，建议增加睡眠时间")
            
            # 睡眠规律性
            if len(self.sleep_records) >= 5:
                insights.append("睡眠记录较为完整，有助于建立规律作息")
        
        # 运动洞察
        if self.exercise_records:
            exercise_days = len(set(r.exercise_date for r in self.exercise_records))
            if exercise_days >= 4:
                insights.append("运动频率达到理想标准")
            elif exercise_days >= 2:
                insights.append("运动频率良好，建议继续保持")
            else:
                insights.append("运动频率偏低，建议增加运动次数")
        
        # 饮食洞察
        if self.diet_records:
            food_variety = len(set(r.food_name for r in self.diet_records))
            if food_variety >= 15:
                insights.append("饮食种类丰富，营养较为均衡")
            elif food_variety < 8:
                insights.append("饮食种类较单一，建议增加食物多样性")
        
        return insights[:5]  # 返回最多5条洞察
    
    def generate_recommendations(self):
        """生成健康建议"""
        recommendations = []
        
        sleep_score = self.calculate_sleep_score()
        exercise_score = self.calculate_exercise_score()
        diet_score = self.calculate_diet_score()
        
        # 睡眠建议
        if sleep_score < 70:
            recommendations.append({
                "category": "sleep",
                "priority": "high",
                "title": "改善睡眠质量",
                "description": "建议建立规律的作息时间，确保每晚7-9小时的充足睡眠"
            })
        elif sleep_score < 85:
            recommendations.append({
                "category": "sleep",
                "priority": "medium",
                "title": "优化睡眠习惯",
                "description": "睡眠质量良好，建议睡前1小时避免使用电子设备"
            })
        
        # 运动建议
        if exercise_score < 70:
            recommendations.append({
                "category": "exercise",
                "priority": "high",
                "title": "增加运动频率",
                "description": "建议每周进行4-5次有氧运动，每次30-45分钟"
            })
        elif exercise_score < 85:
            recommendations.append({
                "category": "exercise",
                "priority": "medium",
                "title": "丰富运动类型",
                "description": "在现有运动基础上，增加力量训练和柔韧性练习"
            })
        
        # 饮食建议
        if diet_score < 70:
            recommendations.append({
                "category": "diet",
                "priority": "high",
                "title": "改善饮食结构",
                "description": "建议增加蔬菜水果摄入，控制高热量食物，保持营养均衡"
            })
        elif diet_score < 85:
            recommendations.append({
                "category": "diet",
                "priority": "medium",
                "title": "优化用餐规律",
                "description": "建议固定三餐时间，合理控制各餐次的卡路里分配"
            })
        
        return recommendations[:6]  # 返回最多6条建议
    
    def generate_data_summary(self):
        """生成数据摘要"""
        # 睡眠数据摘要
        sleep_days = len(self.sleep_records)
        avg_sleep_hours = 0
        if self.sleep_records:
            avg_sleep_hours = statistics.mean([
                r.sleep_duration / 60 for r in self.sleep_records if r.sleep_duration
            ])
        
        # 运动数据摘要
        exercise_days = len(set(r.exercise_date for r in self.exercise_records))
        total_calories_burned = sum(r.calories_burned or 0 for r in self.exercise_records)
        
        # 饮食数据摘要
        diet_days = len(set(r.diet_date for r in self.diet_records))
        daily_calories = defaultdict(int)
        for record in self.diet_records:
            daily_calories[record.diet_date] += record.total_calories or 0
        
        avg_calories_intake = statistics.mean(daily_calories.values()) if daily_calories else 0
        
        return {
            "sleep_days": sleep_days,
            "exercise_days": exercise_days,
            "diet_days": diet_days,
            "avg_sleep_hours": round(avg_sleep_hours, 1),
            "total_calories_burned": total_calories_burned,
            "avg_calories_intake": int(avg_calories_intake)
        }
    
    def generate_detailed_analysis(self):
        """生成详细分析"""
        analysis = {}
        
        # 睡眠详细分析
        if self.sleep_records:
            sleep_durations = [r.sleep_duration / 60 for r in self.sleep_records if r.sleep_duration]
            analysis["sleep_analysis"] = {
                "avg_sleep_duration": round(statistics.mean(sleep_durations), 1),
                "sleep_regularity_score": int(self._calculate_sleep_regularity_score()),
                "best_sleep_day": str(max(self.sleep_records, key=lambda r: r.sleep_duration or 0).sleep_date),
                "worst_sleep_day": str(min(self.sleep_records, key=lambda r: r.sleep_duration or 999).sleep_date)
            }
        
        # 运动详细分析
        if self.exercise_records:
            total_time = sum(r.duration_minutes for r in self.exercise_records)
            exercise_types = [r.exercise_type for r in self.exercise_records]
            most_common_exercise = Counter(exercise_types).most_common(1)[0][0] if exercise_types else None
            
            analysis["exercise_analysis"] = {
                "total_exercise_time": total_time,
                "avg_calories_burned": int(statistics.mean([r.calories_burned or 0 for r in self.exercise_records])),
                "exercise_frequency": len(set(r.exercise_date for r in self.exercise_records)),
                "dominant_exercise_type": most_common_exercise
            }
        
        # 饮食详细分析
        if self.diet_records:
            daily_calories = defaultdict(int)
            meal_calories = defaultdict(int)
            
            for record in self.diet_records:
                daily_calories[record.diet_date] += record.total_calories or 0
                meal_calories[record.meal_type] += record.total_calories or 0
            
            total_calories = sum(meal_calories.values())
            calorie_distribution = {}
            if total_calories > 0:
                calorie_distribution = {
                    meal: int((calories / total_calories) * 100)
                    for meal, calories in meal_calories.items()
                }
            
            analysis["diet_analysis"] = {
                "avg_daily_calories": int(statistics.mean(daily_calories.values())) if daily_calories else 0,
                "meal_balance_score": int(self._calculate_diet_balance_score()),
                "most_frequent_meal": max(meal_calories.items(), key=lambda x: x[1])[0] if meal_calories else None,
                "calorie_distribution": calorie_distribution
            }
        
        return analysis
    
    def determine_health_trend(self):
        """确定健康趋势（相比上一周期）"""
        # 获取上一周期的报告
        previous_end = self.start_date - timedelta(days=1)
        previous_start = previous_end - timedelta(days=self.period_days - 1)
        
        try:
            previous_report = HealthReport.objects.filter(
                user=self.user,
                period_start=previous_start,
                period_end=previous_end
            ).first()
            
            if previous_report:
                current_score = self.calculate_overall_score()
                previous_score = previous_report.overall_score
                
                if current_score > previous_score + 5:
                    return 'improving'
                elif current_score < previous_score - 5:
                    return 'declining'
                else:
                    return 'stable'
        except:
            pass
        
        # 没有历史数据时，基于当前评分判断
        current_score = self.calculate_overall_score()
        if current_score >= 85:
            return 'stable'  # 高分时认为稳定
        elif current_score >= 70:
            return 'improving'  # 中等分数认为在改善
        else:
            return 'declining'  # 低分认为需要改善
    
    # 辅助方法
    def _time_to_minutes(self, time_obj):
        """将时间对象转换为从午夜开始的分钟数"""
        return time_obj.hour * 60 + time_obj.minute
    
    def _get_meal_distribution(self):
        """获取餐次分布"""
        meal_calories = defaultdict(int)
        for record in self.diet_records:
            meal_calories[record.meal_type] += record.total_calories or 0
        return dict(meal_calories)
    
    def _evaluate_meal_distribution(self, meal_distribution):
        """评估餐次分配合理性"""
        if not meal_distribution:
            return 0
        
        total_calories = sum(meal_distribution.values())
        if total_calories == 0:
            return 0
        
        # 理想分配：早餐25%、午餐40%、晚餐30%、加餐5%
        ideal_distribution = {
            'breakfast': 0.25,
            'lunch': 0.40,
            'dinner': 0.30,
            'snack': 0.05
        }
        
        score = 100
        for meal_type, ideal_ratio in ideal_distribution.items():
            actual_ratio = meal_distribution.get(meal_type, 0) / total_calories
            deviation = abs(actual_ratio - ideal_ratio)
            score -= deviation * 100  # 偏差越大扣分越多
        
        return max(0, score)

    def generate_comprehensive_report(self, user, period_type='weekly'):
        """生成综合健康报告"""
        try:
            # 计算各项评分
            sleep_score = self.calculate_sleep_score()
            exercise_score = self.calculate_exercise_score()
            diet_score = self.calculate_diet_score()
            overall_score = self.calculate_overall_score()
            
            # 计算健康等级
            if overall_score >= 90:
                health_grade = 'A'
            elif overall_score >= 80:
                health_grade = 'B'
            elif overall_score >= 70:
                health_grade = 'C'
            elif overall_score >= 60:
                health_grade = 'D'
            else:
                health_grade = 'F'
            
            # 生成洞察和建议
            insights = self.generate_key_insights()
            recommendations = self.generate_recommendations()
            data_summary = self.generate_data_summary()
            
            # 构建报告数据
            report_data = {
                'period_start': self.start_date,
                'period_end': self.end_date,
                'overall_score': round(overall_score, 1),
                'health_grade': health_grade,
                'scores': {
                    'sleep': round(sleep_score, 1),
                    'exercise': round(exercise_score, 1),
                    'diet': round(diet_score, 1)
                },
                'trends': {
                    'sleep_trend': 'stable',  # 可以根据历史数据计算趋势
                    'exercise_trend': 'stable',
                    'diet_trend': 'stable'
                },
                'insights': insights,
                'recommendations': recommendations,
                'data_summary': data_summary
            }
            
            return report_data
            
        except Exception as e:
            print(f"生成健康报告时出错: {str(e)}")
            return None
