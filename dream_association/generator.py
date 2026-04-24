#!/usr/bin/env python3
"""
梦境洞察生成器
基于梦境分析结果生成创意洞察和个人成长建议
"""

import os
import sys
import json
import random
from typing import List, Dict, Any
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class InsightGenerator:
    """梦境洞察生成器"""
    
    def __init__(self):
        # 洞察模板库
        self.insight_templates = self._load_insight_templates()
        self.suggestion_templates = self._load_suggestion_templates()
        self.reflection_prompts = self._load_reflection_prompts()
    
    def _load_insight_templates(self) -> Dict[str, List[str]]:
        """加载洞察模板"""
        return {
            "freedom": [
                "你的梦境显示对自由的强烈渴望，这可能与当前感受到的某些限制有关。",
                "飞翔的梦境往往象征着超越和解脱，反映了你希望突破现状的愿望。",
                "自由主题的频繁出现，暗示你正在寻求更多自主权和选择空间。"
            ],
            "fear": [
                "恐惧型梦境往往是潜意识的警示，提醒你关注内心的担忧和焦虑。",
                "噩梦虽然让人不安，但它们也是心灵处理和释放压力的方式。",
                "面对恐惧的梦境，可能是在邀请你正视并克服生活中的挑战。"
            ],
            "success": [
                "成功主题的梦境反映了你的自信心和成就动机，很积极！",
                "攀登和胜利的梦境显示你具备克服困难的能力和决心。",
                "这些梦境可能是潜意识对即将成功的预示和鼓励。"
            ],
            "family": [
                "家庭主题的梦境通常与情感需求和安全感相关。",
                "对家人的思念或家庭场景的梦境，反映了你对归属感的重视。",
                "家庭相关的梦境可能是在提醒你需要关注亲情关系。"
            ],
            "work": [
                "工作相关的梦境显示你对职业发展的关注和投入。",
                "考试和任务的梦境可能反映了你在现实中的压力和期待。",
                "这些梦境是在提醒你平衡工作与生活，避免过度紧张。"
            ],
            "health": [
                "健康主题的梦境是身体和心灵的自我关怀信号，值得关注。",
                "生病和治疗的梦境可能是在提醒你需要关注身心健康。",
                "这些梦境显示你的身体智慧在与你沟通。"
            ],
            "general": [
                "梦境是潜意识的语言，通过象征和隐喻与你交流。",
                "每个梦境都是独特的，重要的是找到对你个人有意义的内涵。",
                "梦境可以提供新的视角，帮助你理解自己和生活的不同层面。"
            ]
        }
    
    def _load_suggestion_templates(self) -> Dict[str, List[str]]:
        """加载建议模板"""
        return {
            "reflection": [
                "花时间思考梦境中的主题与你当前生活的关联",
                "记录梦境出现时的情境和感受，寻找模式",
                "尝试理解梦境可能在提醒你关注什么"
            ],
            "action": [
                "尝试一个小的改变，打破日常模式",
                "与信任的人分享你的梦境和感受",
                "给自己一些空间和时间来处理这些情感",
                "通过艺术、写作或运动表达梦境中的情感"
            ],
            "awareness": [
                "在接下来的一周，特别留意相关的情境和感受",
                "注意是否有现实事件触发了类似的梦境主题",
                "观察自己对这些梦境主题的反应和态度"
            ]
        }
    
    def _load_reflection_prompts(self) -> List[str]:
        """加载反思提示"""
        return [
            "这个梦境主题在什么情况下出现最频繁？",
            "它与你当前的生活状态有何关联？",
            "如果这个梦境是信息，它想告诉你什么？",
            "你可以如何将这些洞察应用到日常生活中？",
            "这个梦境反映了你的哪些深层需求或渴望？",
            "它与你最近经历的事件有什么联系？",
            "它揭示了你性格的哪些方面？",
            "你可以从这个梦境中学到什么关于自己的新认识？"
        ]
    
    def generate_insights(self, dream_analysis: Dict, 
                         correlations: Dict = None,
                         user_context: Dict = None) -> Dict[str, Any]:
        """
        生成全面的梦境洞察
        
        Args:
            dream_analysis: 单个或组合的梦境分析结果
            correlations: 关联发现结果（可选）
            user_context: 用户上下文信息（可选）
        
        Returns:
            包含洞察、建议和反思提示的字典
        """
        insights = []
        suggestions = []
        
        # 1. 基于主题生成洞察
        theme_insights = self._generate_theme_insights(dream_analysis)
        insights.extend(theme_insights)
        
        # 2. 基于情感生成洞察
        emotion_insights = self._generate_emotion_insights(dream_analysis)
        insights.extend(emotion_insights)
        
        # 3. 基于关联生成洞察
        if correlations:
            correlation_insights = self._generate_correlation_insights(
                correlations, dream_analysis
            )
            insights.extend(correlation_insights)
        
        # 4. 基于模式生成洞察
        if correlations and correlations.get('patterns'):
            pattern_insights = self._generate_pattern_insights(
                correlations['patterns'], dream_analysis
            )
            insights.extend(pattern_insights)
        
        # 5. 生成一般建议
        general_suggestions = self._generate_general_suggestions(dream_analysis)
        suggestions.extend(general_suggestions)
        
        # 6. 基于洞察生成具体建议
        insight_based_suggestions = self._generate_insight_based_suggestions(insights)
        suggestions.extend(insight_based_suggestions)
        
        # 7. 选择合适的反思提示
        prompts = self._select_reflection_prompts(insights, dream_analysis)
        
        return {
            "dream_id": dream_analysis.get("dream_id", "unknown"),
            "generated_at": datetime.now().isoformat(),
            "insights": self._format_insights(insights),
            "suggestions": suggestions,
            "reflection_prompts": prompts,
            "confidence_level": self._calculate_confidence(insights),
            "summary": self._generate_summary(insights, suggestions)
        }
    
    def _generate_theme_insights(self, dream_analysis: Dict) -> List[Dict]:
        """基于主题生成洞察"""
        insights = []
        themes = dream_analysis.get("analysis", {}).get("themes", [])
        
        for theme_info in themes[:3]:  # 只考虑前3个最强主题
            theme = theme_info.get("theme")
            strength = theme_info.get("strength", 0)
            
            if strength > 0.3:  # 只考虑显著的主题
                # 获取适合的洞察模板
                template = self._get_theme_insight(theme, strength)
                if template:
                    insights.append({
                        "type": "theme",
                        "theme": theme,
                        "strength": strength,
                        "insight": template,
                        "importance": strength
                    })
        
        return insights
    
    def _generate_emotion_insights(self, dream_analysis: Dict) -> List[Dict]:
        """基于情感生成洞察"""
        insights = []
        emotions = dream_analysis.get("analysis", {}).get("emotions", {})
        
        # 移除neutral
        emotions = {k: v for k, v in emotions.items() if k != "neutral"}
        
        if emotions:
            # 找出主导情感
            dominant_emotion = max(emotions.items(), key=lambda x: x[1])
            emotion_name, emotion_strength = dominant_emotion
            
            if emotion_strength > 0.4:
                insight = self._get_emotion_insight(emotion_name, emotion_strength)
                insights.append({
                    "type": "emotion",
                    "emotion": emotion_name,
                    "strength": emotion_strength,
                    "insight": insight,
                    "importance": emotion_strength
                })
            
            # 如果有多个显著情感，生成综合洞察
            significant_emotions = [(e, s) for e, s in emotions.items() if s > 0.3]
            if len(significant_emotions) >= 2:
                combined_insight = self._generate_combined_emotion_insight(
                    significant_emotions
                )
                insights.append({
                    "type": "emotional_complexity",
                    "emotions": [e for e, s in significant_emotions],
                    "insight": combined_insight,
                    "importance": 0.7
                })
        
        return insights
    
    def _generate_correlation_insights(self, correlations: Dict, 
                                      dream_analysis: Dict) -> List[Dict]:
        """基于关联生成洞察"""
        insights = []
        
        strong_correlations = [
            c for c in correlations.get("correlations", [])
            if c.get("strength") == "strong" or c.get("similarity_score", 0) >= 0.75
        ]
        
        if strong_correlations:
            if len(strong_correlations) >= 2:
                insights.append({
                    "type": "pattern_recognition",
                    "insight": (
                        "检测到多个强关联，表明存在明确的" 
                        "梦境主题模式。这可能反映了你在现实生活中"
                        "持续关注或处理的重要议题。"
                    ),
                    "importance": 0.8
                })
            else:
                insights.append({
                    "type": "significant_connection",
                    "insight": (
                        "发现重要的梦境关联，这可能表明不同" 
                        "梦境体验之间存在深层的心理联系。"
                    ),
                    "importance": 0.6
                })
        
        return insights
    
    def _generate_pattern_insights(self, patterns: List[Dict], 
                                  dream_analysis: Dict) -> List[Dict]:
        """基于模式生成洞察"""
        insights = []
        
        theme_patterns = [
            p for p in patterns 
            if p.get("pattern_type") == "theme_repetition" and p.get("occurrences", 0) >= 2
        ]
        
        for pattern in theme_patterns:
            theme = pattern.get("theme", "")
            occurrences = pattern.get("occurrences", 0)
            
            if occurrences >= 3:
                insights.append({
                    "type": "recurring_theme",
                    "theme": theme,
                    "insight": (
                        f"主题 '{theme}' 在你的梦境中重复出现了 {occurrences} 次，"
                        "这强烈表明这是你潜意识中非常重要的议题，"
                        "值得深入探索和关注。"
                    ),
                    "importance": 0.9
                })
            elif occurrences == 2:
                insights.append({
                    "type": "emerging_pattern",
                    "theme": theme,
                    "insight": (
                        f"主题 '{theme}' 出现了 {occurrences} 次，"
                        "虽然数量不多，但可能预示着这个议题"
                        "正在进入你的关注中心。"
                    ),
                    "importance": 0.6
                })
        
        emotion_patterns = [
            p for p in patterns if p.get("pattern_type") == "emotional_tendency"
        ]
        
        for pattern in emotion_patterns:
            emotion = pattern.get("emotion", "")
            strength = pattern.get("average_strength", 0)
            percentage = pattern.get("percentage", 0)
            
            if strength > 0.6 and percentage > 50:
                insights.append({
                    "type": "emotional_tendency",
                    "emotion": emotion,
                    "insight": (
                        f"你的梦境中'{emotion}'情感的频繁出现"
                        f"({percentage:.0f}%)显示出明显的情感倾向，"
                        "这可能反映了你当前的心理状态和情感需求。"
                    ),
                    "importance": 0.7
                })
        
        return insights
    
    def _generate_general_suggestions(self, dream_analysis: Dict) -> List[str]:
        """生成一般性建议"""
        suggestions = []
        
        themes = dream_analysis.get("analysis", {}).get("themes", [])
        emotions = dream_analysis.get("analysis", {}).get("emotions", {})
        
        # 添加反思类建议
        suggestions.append(random.choice(self.suggestion_templates["reflection"]))
        
        # 如果有强烈情感，添加情感管理建议
        significant_emotions = [(e, s) for e, s in emotions.items() if s > 0.5 and e != "neutral"]
        if significant_emotions:
            suggestions.append("留意这些梦境情感在日常生活中的体现")
            suggestions.append("考虑通过合适的方式表达和处理这些情感")
        
        # 添加行动类建议
        suggestions.append(random.choice(self.suggestion_templates["action"]))
        
        return list(set(suggestions))  # 去重
    
    def _generate_insight_based_suggestions(self, insights: List[Dict]) -> List[str]:
        """基于洞察生成个性化建议"""
        suggestions = []
        
        for insight in insights:
            insight_type = insight.get("type", "")
            
            if insight_type == "theme":
                theme = insight.get("theme", "")
                strength = insight.get("strength", 0)
                
                if strength > 0.5:
                    suggestions.append(
                        f"深入探索'{theme}'主题对你生活的意义和影响"
                    )
            
            elif insight_type == "emotion":
                emotion = insight.get("emotion", "")
                suggestions.append(
                    f"探索'{emotion}'情感背后的深层需求和动机"
                )
        
        return suggestions
    
    def _select_reflection_prompts(self, insights: List[Dict], 
                                   dream_analysis: Dict) -> List[str]:
        """选择合适的反思提示"""
        prompts = []
        
        # 确保至少有3个提示
        selected_prompts = random.sample(
            self.reflection_prompts, 
            min(3, len(self.reflection_prompts))
        )
        prompts.extend(selected_prompts)
        
        # 基于洞察添加具体提示
        for insight in insights[:2]:  # 基于前2个最重要的洞察
            if insight.get("type") == "theme":
                theme = insight.get("theme", "")
                prompts.append(
                    f"这个'{theme}'主题对你来说有什么特殊意义？"
                )
        
        return prompts[:4]  # 返回前4个提示
    
    def _get_theme_insight(self, theme: str, strength: float) -> str:
        """获取主题洞察"""
        if theme in self.insight_templates:
            templates = self.insight_templates[theme]
        else:
            templates = self.insight_templates["general"]
        
        # 根据强度选择不同的模板
        if strength > 0.7:
            return templates[0] if len(templates) > 0 else ""
        elif strength > 0.5:
            return templates[1] if len(templates) > 1 else templates[0]
        else:
            return templates[2] if len(templates) > 2 else templates[0]
    
    def _get_emotion_insight(self, emotion: str, strength: float) -> str:
        """获取情感洞察"""
        emotion_map = {
            "joy": "喜悦的情感反映了你内心积极的能量和满足感。",
            "sadness": "悲伤的情感是心灵自我疗愈过程的一部分，值得温柔对待。",
            "anger": "愤怒往往提示我们需要关注某些边界或公正问题。",
            "fear": "恐惧是保护机制，提醒我们关注潜在的风险或不确定性。",
            "surprise": "惊讶的情感表明生活中出现了意料之外的变化或可能性。",
            "peace": "平静的情感显示你内心有良好的平衡和和谐状态。",
            "excitement": "兴奋的情感预示着新的可能性和积极的改变即将到来。"
        }
        
        return emotion_map.get(emotion, 
            f"{emotion}情感的强烈出现值得你关注和理解。")
    
    def _generate_combined_emotion_insight(self, emotions: List[tuple]) -> str:
        """生成复合情感洞察"""
        emotion_names = [e for e, s in emotions]
        emotion_str = "、".join(emotion_names)
        return (
            f"你的梦境显示出复杂的情感模式: {emotion_str}。"
            "这种情感的交织表明你的内心正在经历一个复杂的心理过程，"
            "建议通过适当的方式理解和管理这些情感。"
        )
    
    def _format_insights(self, insights: List[Dict]) -> List[Dict]:
        """格式化洞察，按重要性排序"""
        return sorted(insights, key=lambda x: x.get("importance", 0), reverse=True)
    
    def _calculate_confidence(self, insights: List[Dict]) -> str:
        """计算洞察的置信度"""
        if not insights:
            return "low"
        
        avg_importance = sum(i.get("importance", 0) for i in insights) / len(insights)
        
        if avg_importance > 0.7:
            return "high"
        elif avg_importance > 0.4:
            return "medium"
        else:
            return "low"
    
    def _generate_summary(self, insights: List[Dict], suggestions: List[str]) -> str:
        """生成摘要"""
        if not insights:
            return "基于当前梦境分析，我们建议您持续关注梦境内容，记录更多的梦境细节。"
        
        main_insight = insights[0]
        return main_insight.get("insight", "")


def main():
    """测试洞察生成器"""
    from analyzer import DreamAnalyzer
    from correlator import DreamCorrelator
    
    generator = InsightGenerator()
    analyzer = DreamAnalyzer()
    correlator = DreamCorrelator()
    
    # 测试用例
    test_dreams = [
        "梦见自己在天空中自由飞翔，感觉非常开心和兴奋，没有任何束缚。",
        "梦见在广阔的原野上奔跑，感觉自由自在，心情愉悦。",
        "梦见攀登一座高山，虽然很累但最终到达了山顶，很有成就感。",
    ]
    
    # 分析梦境
    print("🔍 分析梦境...")
    analyses = []
    for i, dream in enumerate(test_dreams):
        result = analyzer.analyze(dream, f"2026-04-{20+i}")
        analyses.append(result)
        print(f"  • 梦境 {i+1}: {result['summary']}")
    
    # 发现关联
    print("\n🔗 发现关联...")
    correlations = correlator.find_correlations(analyses)
    
    # 生成洞察
    print("\n💡 生成洞察...")
    insights_result = generator.generate_insights(analyses[0], correlations)
    
    print(f"\n📄 梦境: {insights_result['dream_id']}")
    print(f"📊 置信度: {insights_result['confidence_level']}")
    
    print(f"\n💡 洞察:")
    for insight in insights_result["insights"]:
        print(f"\n📌 [{insight['type']}] 重要性: {insight['importance']}")
        print(f"   {insight['insight']}")
    
    if insights_result["suggestions"]:
        print(f"\n🎯 建议:")
        for suggestion in insights_result["suggestions"][:3]:
            print(f"   • {suggestion}")
    
    if insights_result["reflection_prompts"]:
        print(f"\n🤔 思考问题:")
        for prompt in insights_result["reflection_prompts"][:2]:
            print(f"   • {prompt}")


if __name__ == "__main__":
    main()
