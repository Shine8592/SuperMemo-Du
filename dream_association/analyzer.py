#!/usr/bin/env python3
"""
梦境分析器 - 深度分析梦境内容
提取主题、情感、关键词和语义嵌入
"""

import re
import json
from typing import List, Dict, Any
from datetime import datetime
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dual_memory_engine import MemoryCoordinator


class DreamAnalyzer:
    """梦境内容深度分析器"""
    
    def __init__(self):
        # 主题关键词库
        self.theme_keywords = {
            "自由": ["飞翔", "天空", "自由", "无拘无束", "翱翔", "漂浮", "解脱"],
            "恐惧": ["害怕", "恐惧", "恐怖", "噩梦", "追赶", "坠落", "被困"],
            "成功": ["胜利", "成功", "攀登", "高峰", "成就", "完成", "获奖"],
            "爱情": ["爱", "喜欢", "拥抱", "亲吻", "恋人", "浪漫", "甜蜜"],
            "家庭": ["家人", "父母", "家", "童年", "亲人", "团聚", "温暖"],
            "工作": ["工作", "考试", "面试", "任务", "压力", "责任", "挑战"],
            "旅行": ["旅行", "迷路", "探索", "发现", "冒险", "远行", "旅游"],
            "健康": ["生病", "受伤", "医院", "医生", "治疗", "康复", "健康"],
            "财富": ["金钱", "财富", "礼物", "彩票", "发财", "贫穷", "花费"],
            "死亡": ["死亡", "逝去", "葬礼", "告别", "结束", "永别", "灵魂"]
        }
        
        # 情感关键词库
        self.emotion_keywords = {
            "joy": ["开心", "快乐", "高兴", "愉快", "兴奋", "幸福", "喜悦", "满足", "微笑"],
            "sadness": ["悲伤", "难过", "伤心", "痛苦", "哭泣", "失落", "沮丧", "失望"],
            "anger": ["生气", "愤怒", "恼火", "暴躁", "不满", "抱怨", "怨恨", "气愤"],
            "fear": ["害怕", "恐惧", "紧张", "担忧", "焦虑", "惊慌", "恐慌", "不安"],
            "surprise": ["惊讶", "惊奇", "意外", "震惊", "不可思议", "没想到"],
            "peace": ["平静", "安宁", "放松", "舒适", "祥和", "宁静", "安详", "和谐"],
            "excitement": ["兴奋", "激动", "振奋", "期待", "渴望", "热情", "热血"]
        }
        
        # 停止词
        self.stop_words = {"的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", 
                          "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会",
                          "着", "没有", "看", "好", "自己", "这", "那", "他", "她", "它",
                          "们", "什么", "怎么", "为什么", "哪里", "谁", "哪个", "这样", "那么"}
    
    def analyze(self, dream_text: str, dream_date: str = None) -> Dict[str, Any]:
        """
        深度分析梦境内容
        
        Args:
            dream_text: 梦境内容文本
            dream_date: 梦境日期 (YYYY-MM-DD格式)
        
        Returns:
            梦境分析结果字典
        """
        if not dream_date:
            dream_date = datetime.now().strftime("%Y-%m-%d")
        
        # 清理文本
        clean_text = self._clean_text(dream_text)
        
        # 提取各种信息
        themes = self.extract_themes(clean_text)
        emotions = self.analyze_emotions(clean_text)
        keywords = self.extract_keywords(clean_text)
        entities = self.extract_entities(clean_text)
        summary = self.generate_summary(dream_text)
        
        # 生成语义嵌入 (使用现有系统)
        embedding = self._generate_embedding(clean_text)
        
        analysis_result = {
            "dream_id": f"dream_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "dream_date": dream_date,
            "content": dream_text,
            "summary": summary,
            "analysis": {
                "themes": themes,
                "emotions": emotions,
                "keywords": keywords,
                "entities": entities,
                "embedding": embedding
            },
            "created_at": datetime.now().isoformat()
        }
        
        return analysis_result
    
    def _clean_text(self, text: str) -> str:
        """清理和预处理文本"""
        # 移除特殊字符，保留基本标点
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s\u3000-\u303f\uff00-\uffef。！？，、；：]', '', text)
        # 去除多余空格
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def extract_themes(self, text: str) -> List[Dict[str, Any]]:
        """提取梦境主题"""
        themes = []
        text_lower = text.lower()
        
        for theme, keywords in self.theme_keywords.items():
            match_count = 0
            matched_keywords = []
            
            for keyword in keywords:
                if keyword in text:
                    match_count += 1
                    matched_keywords.append(keyword)
            
            if match_count > 0:
                # 计算主题强度 (0-1)
                strength = min(match_count / len(keywords), 1.0)
                # 考虑关键词密度
                density = match_count / max(len(text), 1) * 100
                
                themes.append({
                    "theme": theme,
                    "strength": round(min(strength + density / 100, 1.0), 3),
                    "matched_keywords": matched_keywords,
                    "match_count": match_count
                })
        
        # 按强度排序
        themes.sort(key=lambda x: x["strength"], reverse=True)
        return themes[:5]  # 返回前5个主题
    
    def analyze_emotions(self, text: str) -> Dict[str, float]:
        """分析梦境情感"""
        emotions = {}
        text_lower = text.lower()
        
        for emotion, keywords in self.emotion_keywords.items():
            match_count = 0
            for keyword in keywords:
                if keyword in text:
                    match_count += 1
            
            if match_count > 0:
                # 计算情感强度
                strength = min(match_count / len(keywords), 1.0)
                emotions[emotion] = round(strength, 3)
        
        # 如果没有检测到明显情感，返回中性
        if not emotions:
            emotions["neutral"] = 0.5
        
        return emotions
    
    def extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 使用简单的词频统计
        import collections
        
        # 分词 (简化版，实际应使用专业分词工具)
        words = []
        for char in text:
            if '\u4e00' <= char <= '\u9fff':  # 中文字符
                words.append(char)
        
        # 统计词频
        word_freq = collections.Counter(words)
        
        # 移除停止词
        for stop_word in self.stop_words:
            word_freq.pop(stop_word, None)
        
        # 返回频率最高的关键词
        keywords = [word for word, freq in word_freq.most_common(10)]
        
        return keywords
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """提取实体信息"""
        entities = {
            "people": [],
            "places": [],
            "objects": [],
            "actions": []
        }
        
        # 简单的实体识别规则
        person_indicators = ["我", "你", "他", "她", "我们", "你们", "他们"]
        place_indicators = ["家", "学校", "公司", "医院", "公园", "山", "海", "城市"]
        object_indicators = ["房子", "车", "书", "手机", "电脑", "衣服", "食物", "水"]
        action_indicators = ["走", "跑", "跳", "飞", "吃", "喝", "看", "听", "说", "做"]
        
        for indicator in person_indicators:
            if indicator in text:
                entities["people"].append(indicator)
        
        for indicator in place_indicators:
            if indicator in text:
                entities["places"].append(indicator)
        
        for indicator in object_indicators:
            if indicator in text:
                entities["objects"].append(indicator)
        
        for indicator in action_indicators:
            if indicator in text:
                entities["actions"].append(indicator)
        
        # 去重
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        return entities
    
    def generate_summary(self, text: str, max_length: int = 100) -> str:
        """生成梦境摘要"""
        if len(text) <= max_length:
            return text
        
        # 简单截断，保留完整句子
        summary = text[:max_length]
        last_period = summary.rfind('。')
        if last_period > 0:
            summary = summary[:last_period + 1]
        
        return summary + '...'
    
    def _generate_embedding(self, text: str) -> List[float]:
        """生成文本的语义嵌入向量"""
        # 这里应该使用sentence-transformers模型
        # 由于环境限制，我们使用一个简化的hash-based方法作为占位
        # 实际使用时应该替换为真实的嵌入模型
        
        import hashlib
        import numpy as np
        
        # 生成确定性的向量 (仅用于演示)
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()
        
        # 创建384维向量 (与现有系统匹配)
        vector = []
        for i in range(384):
            # 使用hash值生成伪随机但确定性的数值
            val = int(hash_hex[i % len(hash_hex)], 16) / 15.0 - 0.5
            vector.append(round(val, 4))
        
        return vector


def main():
    """测试梦境分析器"""
    analyzer = DreamAnalyzer()
    
    # 测试用例
    test_dreams = [
        "梦见自己在天空中自由飞翔，感觉非常开心和兴奋，没有任何束缚。",
        "梦见自己在考试，但什么都不会，很紧张，醒来后一身冷汗。",
        "梦见和家人团聚，大家都很开心，吃了一顿丰盛的晚餐。",
        "梦见攀登一座高山，虽然很累但最终到达了山顶，感觉很有成就感。"
    ]
    
    for i, dream in enumerate(test_dreams, 1):
        print(f"\n{'='*70}")
        print(f"🌙 梦境分析 #{i}")
        print(f"{'='*70}")
        print(f"内容: {dream}")
        
        result = analyzer.analyze(dream)
        
        print(f"\n📊 主题:")
        for theme in result["analysis"]["themes"]:
            print(f"  • {theme['theme']} (强度: {theme['strength']})")
        
        print(f"\n😊 情感:")
        for emotion, strength in result["analysis"]["emotions"].items():
            print(f"  • {emotion}: {strength}")
        
        print(f"\n🏷️  关键词: {', '.join(result['analysis']['keywords'])}")
        print(f"📝 摘要: {result['summary']}")


if __name__ == "__main__":
    main()
