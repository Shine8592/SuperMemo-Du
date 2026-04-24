#!/usr/bin/env python3
"""
梦境关联发现器
发现梦境之间的概念、情感和时间关联
"""

import os
import sys
import json
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import itertools

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class DreamCorrelator:
    """梦境关联发现器"""
    
    def __init__(self, similarity_threshold: float = 0.7):
        self.similarity_threshold = similarity_threshold
        self.max_time_gap_days = 30  # 最大时间间隔（天）
    
    def find_correlations(self, dream_analyses: List[Dict]) -> Dict[str, Any]:
        """
        发现梦境之间的各种关联
        
        Args:
            dream_analyses: 梦境分析结果列表
        
        Returns:
            包含各种关联的发现结果
        """
        # 按时间排序
        sorted_dreams = sorted(dream_analyses, key=lambda x: x.get('dream_date', ''))
        
        # 发现不同类型的关联
        semantic_corr = self._find_semantic_correlations(sorted_dreams)
        emotional_corr = self._find_emotional_correlations(sorted_dreams)
        temporal_corr = self._find_temporal_correlations(sorted_dreams)
        pattern_correlations = self._identify_patterns(sorted_dreams)
        cycles = self._detect_cycles(sorted_dreams)
        
        # 合并所有关联
        all_correlations = self._merge_correlations(
            semantic_corr, emotional_corr, temporal_corr
        )
        
        return {
            "total_dreams": len(sorted_dreams),
            "correlations": all_correlations,
            "patterns": pattern_correlations,
            "cycles": cycles,
            "summary": self._generate_correlation_summary(
                all_correlations, pattern_correlations, cycles
            ),
            "analyzed_at": datetime.now().isoformat()
        }
    
    def _find_semantic_correlations(self, dreams: List[Dict]) -> List[Dict]:
        """发现语义相似度关联"""
        correlations = []
        
        for i, dream1 in enumerate(dreams):
            for dream2 in dreams[i+1:]:
                # 计算时间间隔
                days_gap = self._calculate_days_gap(dream1, dream2)
                
                if days_gap > self.max_time_gap_days:
                    continue
                
                # 检查是否有主题重叠
                theme_sim = self._calculate_theme_similarity(dream1, dream2)
                
                if theme_sim >= self.similarity_threshold:
                    correlations.append({
                        "type": "semantic",
                        "dream1": {
                            "id": dream1.get("dream_id", "unknown"),
                            "date": dream1.get("dream_date", ""),
                            "summary": dream1.get("summary", "")[:50]
                        },
                        "dream2": {
                            "id": dream2.get("dream_id", "unknown"),
                            "date": dream2.get("dream_date", ""),
                            "summary": dream2.get("summary", "")[:50]
                        },
                        "similarity_score": round(theme_sim, 3),
                        "days_gap": days_gap,
                        "shared_themes": self._get_shared_themes(dream1, dream2),
                        "strength": self._classify_strength(theme_sim)
                    })
        
        # 按相似度排序
        correlations.sort(key=lambda x: x["similarity_score"], reverse=True)
        return correlations
    
    def _find_emotional_correlations(self, dreams: List[Dict]) -> List[Dict]:
        """发现情感相似性关联"""
        correlations = []
        
        for i, dream1 in enumerate(dreams):
            for dream2 in dreams[i+1:]:
                days_gap = self._calculate_days_gap(dream1, dream2)
                
                if days_gap > self.max_time_gap_days:
                    continue
                
                # 计算情感相似度
                emotion_sim = self._calculate_emotion_similarity(dream1, dream2)
                
                if emotion_sim >= 0.6:  # 情感相似度阈值较低
                    correlations.append({
                        "type": "emotional",
                        "dream1": {
                            "id": dream1.get("dream_id", "unknown"),
                            "date": dream1.get("dream_date", ""),
                        },
                        "dream2": {
                            "id": dream2.get("dream_id", "unknown"),
                            "date": dream2.get("dream_date", ""),
                        },
                        "emotion_similarity": round(emotion_sim, 3),
                        "days_gap": days_gap,
                        "shared_emotions": self._get_shared_emotions(dream1, dream2),
                        "dominant_emotion": self._get_dominant_emotion(dream1, dream2)
                    })
        
        correlations.sort(key=lambda x: x["emotion_similarity"], reverse=True)
        return correlations
    
    def _find_temporal_correlations(self, dreams: List[Dict]) -> List[Dict]:
        """发现时间序列关联"""
        correlations = []
        
        # 检查连续出现的主题
        for i in range(len(dreams) - 1):
            dream1 = dreams[i]
            dream2 = dreams[i + 1]
            
            days_gap = self._calculate_days_gap(dream1, dream2)
            
            if days_gap <= 7:  # 一周内的梦境
                # 检查是否有相关主题
                shared_themes = self._get_shared_themes(dream1, dream2)
                
                if shared_themes:
                    correlations.append({
                        "type": "temporal",
                        "dream1": {
                            "id": dream1.get("dream_id", "unknown"),
                            "date": dream1.get("dream_date", ""),
                        },
                        "dream2": {
                            "id": dream2.get("dream_id", "unknown"),
                            "date": dream2.get("dream_date", ""),
                        },
                        "days_gap": days_gap,
                        "shared_themes": shared_themes,
                        "pattern_type": "sequential"
                    })
        
        return correlations
    
    def _identify_patterns(self, dreams: List[Dict]) -> List[Dict]:
        """识别梦境模式"""
        patterns = []
        
        # 1. 识别重复主题模式
        theme_patterns = self._identify_theme_patterns(dreams)
        patterns.extend(theme_patterns)
        
        # 2. 识别情感模式
        emotion_patterns = self._identify_emotion_patterns(dreams)
        patterns.extend(emotion_patterns)
        
        # 3. 识别时间模式
        time_patterns = self._identify_time_patterns(dreams)
        patterns.extend(time_patterns)
        
        return patterns
    
    def _assess_pattern_significance(self, occurrence_count: int, total_dreams: int) -> str:
        """评估模式的重要性"""
        if total_dreams == 0:
            return "low"
        
        frequency = occurrence_count / total_dreams
        
        if frequency >= 0.5 or occurrence_count >= 3:
            return "high"
        elif frequency >= 0.3 or occurrence_count >= 2:
            return "moderate"
        else:
            return "low"
    
    def _identify_theme_patterns(self, dreams: List[Dict]) -> List[Dict]:
        """识别主题重复模式"""
        patterns = []
        
        # 统计每个主题出现的频率
        theme_frequency = defaultdict(list)
        
        for dream in dreams:
            themes = dream.get("analysis", {}).get("themes", [])
            for theme_info in themes:
                theme = theme_info.get("theme")
                if theme:
                    theme_frequency[theme].append({
                        "date": dream.get("dream_date", ""),
                        "strength": theme_info.get("strength", 0)
                    })
        
        # 找出出现多次的主题
        for theme, occurrences in theme_frequency.items():
            if len(occurrences) >= 2:
                patterns.append({
                    "pattern_type": "theme_repetition",
                    "theme": theme,
                    "occurrences": len(occurrences),
                    "dates": [occ["date"] for occ in occurrences],
                    "average_strength": round(
                        sum(occ["strength"] for occ in occurrences) / len(occurrences), 3
                    ),
                    "significance": self._assess_pattern_significance(len(occurrences), len(dreams))
                })
        
        patterns.sort(key=lambda x: x["occurrences"], reverse=True)
        return patterns

    
    def _identify_emotion_patterns(self, dreams: List[Dict]) -> List[Dict]:
        """识别情感模式"""
        patterns = []
        
        # 统计总体情感趋势
        emotion_totals = defaultdict(float)
        emotion_counts = defaultdict(int)
        
        for dream in dreams:
            emotions = dream.get("analysis", {}).get("emotions", {})
            for emotion, strength in emotions.items():
                if emotion != "neutral":
                    emotion_totals[emotion] += strength
                    emotion_counts[emotion] += 1
        
        # 计算平均情感强度
        for emotion in emotion_totals:
            avg_strength = emotion_totals[emotion] / emotion_counts[emotion]
            
            if avg_strength > 0.5:  # 显著的情感倾向
                patterns.append({
                    "pattern_type": "emotional_tendency",
                    "emotion": emotion,
                    "average_strength": round(avg_strength, 3),
                    "occurrence_count": emotion_counts[emotion],
                    "total_dreams": len(dreams),
                    "percentage": round(emotion_counts[emotion] / len(dreams) * 100, 1)
                })
        
        return patterns
    
    def _identify_time_patterns(self, dreams: List[Dict]) -> List[Dict]:
        """识别时间相关模式"""
        patterns = []
        
        if len(dreams) < 3:
            return patterns
        
        # 检查周期模式（简单实现）
        dream_dates = [datetime.strptime(d.get("dream_date", ""), "%Y-%m-%d") 
                      for d in dreams if d.get("dream_date")]
        
        if len(dream_dates) >= 2:
            # 计算平均间隔
            intervals = []
            for i in range(len(dream_dates) - 1):
                gap = (dream_dates[i + 1] - dream_dates[i]).days
                intervals.append(gap)
            
            if intervals:
                avg_interval = sum(intervals) / len(intervals)
                patterns.append({
                    "pattern_type": "temporal_frequency",
                    "average_days_between_dreams": round(avg_interval, 1),
                    "total_dream_period": (dream_dates[-1] - dream_dates[0]).days,
                    "dreams_per_week": round(len(dreams) / max(avg_interval / 7, 1), 2)
                })
        
        return patterns
    
    def _detect_cycles(self, dreams: List[Dict]) -> List[Dict]:
        """检测周期性模式"""
        cycles = []
        
        if len(dreams) < 4:
            return cycles
        
        # 简化的周期检测
        dream_dates = sorted([d for d in dreams if d.get("dream_date")], 
                           key=lambda x: x.get("dream_date", ""))
        
        if len(dream_dates) < 4:
            return cycles
        
        # 检查是否有规律的时间间隔
        dates = [datetime.strptime(d.get("dream_date", ""), "%Y-%m-%d") 
                for d in dream_dates]
        
        intervals = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
        
        # 检查间隔的一致性
        if len(intervals) >= 3:
            avg_interval = sum(intervals) / len(intervals)
            variance = sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)
            
            # 如果方差较小，可能存在周期
            if variance < 10 and avg_interval > 0:
                cycles.append({
                    "cycle_type": "potential_periodicity",
                    "average_interval_days": round(avg_interval, 1),
                    "variance": round(variance, 2),
                    "confidence": "moderate",
                    "description": f"梦境间隔约 {round(avg_interval)} 天，可能存在周期性模式"
                })
        
        return cycles
    
    def _calculate_days_gap(self, dream1: Dict, dream2: Dict) -> int:
        """计算两个梦境之间的天数间隔"""
        date1_str = dream1.get("dream_date", "")
        date2_str = dream2.get("dream_date", "")
        
        if not date1_str or not date2_str:
            return 999
        
        try:
            date1 = datetime.strptime(date1_str, "%Y-%m-%d")
            date2 = datetime.strptime(date2_str, "%Y-%m-%d")
            return abs((date2 - date1).days)
        except ValueError:
            return 999
    
    def _calculate_theme_similarity(self, dream1: Dict, dream2: Dict) -> float:
        """计算主题相似度"""
        themes1 = [t.get("theme") for t in dream1.get("analysis", {}).get("themes", [])]
        themes2 = [t.get("theme") for t in dream2.get("analysis", {}).get("themes", [])]
        
        if not themes1 or not themes2:
            return 0.0
        
        # Jaccard相似度
        set1, set2 = set(themes1), set(themes2)
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    def _calculate_emotion_similarity(self, dream1: Dict, dream2: Dict) -> float:
        """计算情感相似度"""
        emotions1 = dream1.get("analysis", {}).get("emotions", {})
        emotions2 = dream2.get("analysis", {}).get("emotions", {})
        
        # 移除neutral
        emotions1 = {k: v for k, v in emotions1.items() if k != "neutral"}
        emotions2 = {k: v for k, v in emotions2.items() if k != "neutral"}
        
        if not emotions1 or not emotions2:
            return 0.0
        
        # 计算余弦相似度
        all_emotions = set(emotions1.keys()) | set(emotions2.keys())
        
        dot_product = sum(emotions1.get(e, 0) * emotions2.get(e, 0) for e in all_emotions)
        mag1 = sum(v**2 for v in emotions1.values()) ** 0.5
        mag2 = sum(v**2 for v in emotions2.values()) ** 0.5
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)
    
    def _get_shared_themes(self, dream1: Dict, dream2: Dict) -> List[str]:
        """获取共享主题"""
        themes1 = [t.get("theme") for t in dream1.get("analysis", {}).get("themes", [])]
        themes2 = [t.get("theme") for t in dream2.get("analysis", {}).get("themes", [])]
        
        shared = set(themes1).intersection(set(themes2))
        return list(shared)
    
    def _get_shared_emotions(self, dream1: Dict, dream2: Dict) -> List[str]:
        """获取共享情感"""
        emotions1 = set(k for k, v in dream1.get("analysis", {}).get("emotions", {}).items() 
                        if v > 0.3 and k != "neutral")
        emotions2 = set(k for k, v in dream2.get("analysis", {}).get("emotions", {}).items() 
                        if v > 0.3 and k != "neutral")
        
        shared = emotions1.intersection(emotions2)
        return list(shared)
    
    def _get_dominant_emotion(self, dream1: Dict, dream2: Dict) -> str:
        """获取主导情感"""
        combined_emotions = defaultdict(float)
        
        for dream in [dream1, dream2]:
            emotions = dream.get("analysis", {}).get("emotions", {})
            for emotion, strength in emotions.items():
                if emotion != "neutral":
                    combined_emotions[emotion] += strength
        
        if combined_emotions:
            return max(combined_emotions.items(), key=lambda x: x[1])[0]
        
        return "neutral"
    
    def _classify_strength(self, similarity: float) -> str:
        """分类关联强度"""
        if similarity >= 0.8:
            return "strong"
        elif similarity >= 0.6:
            return "moderate"
        else:
            return "weak"
    
    def _merge_correlations(self, *correlation_lists) -> List[Dict]:
        """合并所有关联列表"""
        all_correlations = []
        for corr_list in correlation_lists:
            all_correlations.extend(corr_list)
        
        # 按类型和强度排序
        all_correlations.sort(key=lambda x: (
            x.get("type", ""),
            -x.get("similarity_score", x.get("emotion_similarity", 0))
        ))
        
        return all_correlations
    
    def _generate_correlation_summary(self, correlations: List[Dict], 
                                     patterns: List[Dict], 
                                     cycles: List[Dict]) -> Dict[str, Any]:
        """生成关联分析摘要"""
        summary = {
            "total_correlations": len(correlations),
            "correlations_by_type": defaultdict(int),
            "strong_correlations": 0,
            "patterns_found": len(patterns),
            "cycles_detected": len(cycles),
            "key_insights": []
        }
        
        # 统计关联类型
        for corr in correlations:
            corr_type = corr.get("type", "unknown")
            summary["correlations_by_type"][corr_type] += 1
            
            if corr.get("strength") == "strong":
                summary["strong_correlations"] += 1
        
        # 生成关键洞察
        if summary["strong_correlations"] >= 3:
            summary["key_insights"].append(
                "检测到多个强关联，表明存在明确的梦境主题模式。"
            )
        
        if patterns:
            theme_patterns = [p for p in patterns if p.get("pattern_type") == "theme_repetition"]
            if theme_patterns:
                main_theme = theme_patterns[0].get("theme", "")
                summary["key_insights"].append(
                    f"主题 '{main_theme}' 重复出现，可能是当前的重要关注点。"
                )
        
        if cycles:
            summary["key_insights"].append(
                "检测到潜在的周期性模式，建议持续观察以确认。"
            )
        
        # 转换defaultdict为普通dict
        summary["correlations_by_type"] = dict(summary["correlations_by_type"])
        
        return summary


def main():
    """测试关联发现器"""
    from analyzer import DreamAnalyzer
    
    correlator = DreamCorrelator()
    analyzer = DreamAnalyzer()
    
    # 测试用例
    test_dreams = [
        "梦见自己在天空中自由飞翔，感觉非常开心和兴奋，没有任何束缚。",
        "梦见自己在攀登一座高山，虽然很累但最终到达了山顶，很有成就感。",
        "梦见在广阔的原野上奔跑，感觉自由自在，心情愉悦。",
        "梦见考试失败，很紧张，醒来后一身冷汗，很害怕。",
    ]
    
    # 分析梦境
    print("🔍 分析梦境...")
    analyses = []
    for i, dream in enumerate(test_dreams):
        date = f"2026-04-{20 + i}"
        result = analyzer.analyze(dream, date)
        analyses.append(result)
        print(f"  • 梦境 {i+1}: {result['summary']}")
    
    # 发现关联
    print("\n🔗 发现关联...")
    correlations = correlator.find_correlations(analyses)
    
    # 显示结果
    print(f"\n📊 分析摘要:")
    print(f"  总梦境数: {correlations['total_dreams']}")
    print(f"  关联数: {correlations['summary']['total_correlations']}")
    print(f"  模式数: {correlations['summary']['patterns_found']}")
    print(f"  周期数: {correlations['summary']['cycles_detected']}")
    
    if correlations['correlations']:
        print(f"\n🔗 主要关联:")
        for i, corr in enumerate(correlations['correlations'][:3], 1):
            print(f"\n  {i}. [{corr['type']}] 相似度: {corr.get('similarity_score', corr.get('emotion_similarity', 0))}")
            print(f"     梦境1: {corr['dream1']['date']}")
            print(f"     梦境2: {corr['dream2']['date']}")
    
    if correlations['patterns']:
        print(f"\n📈 发现模式:")
        for i, pattern in enumerate(correlations['patterns'][:3], 1):
            if pattern['pattern_type'] == 'theme_repetition':
                print(f"\n  {i}. 🔁 主题重复: '{pattern['theme']}'")
                print(f"     出现次数: {pattern['occurrences']}")
                print(f"     重要性: {pattern['significance']}")
    
    if correlations['summary']['key_insights']:
        print(f"\n💡 关键洞察:")
        for i, insight in enumerate(correlations['summary']['key_insights'], 1):
            print(f"  {i}. {insight}")


if __name__ == "__main__":
    main()
