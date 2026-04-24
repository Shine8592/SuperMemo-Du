#!/usr/bin/env python3
"""
梦境联想控制器
整合分析、关联发现和洞察生成功能
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import List, Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dream_association.analyzer import DreamAnalyzer
from dream_association.correlator import DreamCorrelator
from dream_association.generator import InsightGenerator


class DreamAssociationController:
    """梦境联想控制器"""
    
    def __init__(self):
        self.analyzer = DreamAnalyzer()
        self.correlator = DreamCorrelator()
        self.generator = InsightGenerator()
        self.dream_database = []
    
    def analyze_dream(self, dream_text: str, dream_date: str = None) -> Dict[str, Any]:
        """分析单个梦境"""
        result = self.analyzer.analyze(dream_text, dream_date)
        self.dream_database.append(result)
        return result
    
    def analyze_multiple_dreams(self, dreams: List[Dict]) -> List[Dict]:
        """分析多个梦境"""
        results = []
        for dream_info in dreams:
            text = dream_info.get("text", "")
            date = dream_info.get("date")
            result = self.analyzer.analyze(text, date)
            results.append(result)
        
        self.dream_database.extend(results)
        return results
    
    def find_associations(self) -> Dict[str, Any]:
        """发现梦境之间的关联"""
        if len(self.dream_database) < 2:
            return {
                "status": "error",
                "message": "需要至少2个梦境来分析关联",
                "correlations": [],
                "patterns": [],
                "cycles": []
            }
        
        return self.correlator.find_correlations(self.dream_database)
    
    def generate_insights(self, dream_id: str = None) -> Dict[str, Any]:
        """生成梦境洞察"""
        if not self.dream_database:
            return {
                "status": "error",
                "message": "没有梦境数据可分析"
            }
        
        # 如果指定了dream_id，只分析该梦境
        if dream_id:
            target_dream = None
            for dream in self.dream_database:
                if dream.get("dream_id") == dream_id:
                    target_dream = dream
                    break
            
            if not target_dream:
                return {
                    "status": "error",
                    "message": f"找不到梦境 {dream_id}"
                }
            
            dreams_to_analyze = [target_dream]
        else:
            # 分析所有梦境
            dreams_to_analyze = self.dream_database
        
        # 查找关联
        correlations = self.find_associations()
        
        # 为每个目标梦境生成洞察
        insights_results = []
        for dream in dreams_to_analyze:
            insights = self.generator.generate_insights(
                dream, correlations, {}
            )
            insights_results.append(insights)
        
        return {
            "status": "success",
            "dreams_analyzed": len(dreams_to_analyze),
            "correlations": correlations,
            "insights": insights_results,
            "generated_at": datetime.now().isoformat()
        }
    
    def generate_full_report(self, dream_id: str = None) -> Dict[str, Any]:
        """生成完整的梦境分析报告"""
        insights_result = self.generate_insights(dream_id)
        
        if insights_result.get("status") == "error":
            return insights_result
        
        # 构建完整报告
        report = {
            "report_type": "dream_association_full_report",
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_dreams_in_database": len(self.dream_database),
                "dreams_analyzed": insights_result["dreams_analyzed"],
                "total_correlations": len(insights_result["correlations"].get("correlations", [])),
                "total_patterns": len(insights_result["correlations"].get("patterns", [])),
                "total_cycles": len(insights_result["correlations"].get("cycles", [])),
                "total_insights": sum(
                    len(r.get("insights", [])) 
                    for r in insights_result.get("insights", [])
                )
            },
            "dreams": insights_result.get("insights", []),
            "associations": insights_result.get("correlations", {}),
            "key_findings": self._extract_key_findings(insights_result),
            "recommendations": self._generate_recommendations(insights_result)
        }
        
        return report
    
    def _extract_key_findings(self, insights_result: Dict) -> List[str]:
        """提取关键发现"""
        findings = []
        
        # 从关联摘要中提取
        summary = insights_result.get("correlations", {}).get("summary", {})
        if summary.get("key_insights"):
            findings.extend(summary["key_insights"])
        
        # 从洞察中提取重要洞察
        for dream_insights in insights_result.get("insights", []):
            for insight in dream_insights.get("insights", []):
                if insight.get("importance", 0) > 0.7:
                    findings.append(insight.get("insight", ""))
        
        return findings[:5]  # 返回前5个关键发现
    
    def _generate_recommendations(self, insights_result: Dict) -> List[str]:
        """生成整体建议"""
        recommendations = []
        
        # 收集所有建议
        all_suggestions = []
        for dream_insights in insights_result.get("insights", []):
            all_suggestions.extend(dream_insights.get("suggestions", []))
        
        # 去重并选择最重要的
        unique_suggestions = list(set(all_suggestions))
        recommendations.extend(unique_suggestions[:5])
        
        return recommendations
    
    def save_report(self, report: Dict, filename: str = None) -> str:
        """保存报告到文件"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"dream_report_{timestamp}.json"
        
        filepath = os.path.join(
            os.path.dirname(__file__), "..", "reports", filename
        )
        
        # 确保目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def load_dreams_from_files(self, dream_dir: str = None) -> List[Dict]:
        """从文件加载梦境日志"""
        if not dream_dir:
            dream_dir = os.path.join(
                os.path.dirname(__file__), "..", "..", "dreaming", "rem"
            )
        
        loaded_dreams = []
        
        if not os.path.exists(dream_dir):
            print(f"梦境目录不存在: {dream_dir}")
            return loaded_dreams
        
        # 读取目录中的所有.md文件
        for filename in os.listdir(dream_dir):
            if filename.endswith(".md"):
                filepath = os.path.join(dream_dir, filename)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 从文件名中提取日期
                date_str = filename.replace(".md", "")
                
                dream_info = {
                    "text": content,
                    "date": date_str
                }
                
                loaded_dreams.append(dream_info)
        
        return loaded_dreams


def main():
    """命令行接口"""
    parser = argparse.ArgumentParser(
        description="梦境联想系统 - 分析和发现梦境模式"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 分析单个梦境
    analyze_parser = subparsers.add_parser(
        "analyze", help="分析单个梦境"
    )
    analyze_parser.add_argument(
        "text", help="梦境内容"
    )
    analyze_parser.add_argument(
        "--date", help="梦境日期 (YYYY-MM-DD)", default=None
    )
    
    # 批量分析
    batch_parser = subparsers.add_parser(
        "batch", help="批量分析梦境"
    )
    batch_parser.add_argument(
        "--file", help="包含梦境的JSON文件", default=None
    )
    batch_parser.add_argument(
        "--dir", help="梦境日志目录", default=None
    )
    
    # 发现关联
    assoc_parser = subparsers.add_parser(
        "associate", help="发现梦境关联"
    )
    
    # 生成洞察
    insight_parser = subparsers.add_parser(
        "insight", help="生成梦境洞察"
    )
    insight_parser.add_argument(
        "--dream-id", help="特定梦境ID", default=None
    )
    
    # 生成完整报告
    report_parser = subparsers.add_parser(
        "report", help="生成完整报告"
    )
    report_parser.add_argument(
        "--dream-id", help="特定梦境ID", default=None
    )
    report_parser.add_argument(
        "--save", help="保存报告到文件", action="store_true"
    )
    
    # 加载文件
    load_parser = subparsers.add_parser(
        "load", help="从文件加载梦境"
    )
    load_parser.add_argument(
        "--dir", help="梦境日志目录", default=None
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    controller = DreamAssociationController()
    
    try:
        if args.command == "analyze":
            # 分析单个梦境
            result = controller.analyze_dream(args.text, args.date)
            print(f"\n✅ 梦境分析完成: {result['dream_id']}")
            print(f"📅 日期: {result['dream_date']}")
            print(f"📝 摘要: {result['summary']}")
            print(f"\n🎨 主题:")
            for theme in result["analysis"]["themes"]:
                print(f"  • {theme['theme']} (强度: {theme['strength']})")
            print(f"\n😊 情感:")
            for emotion, strength in result["analysis"]["emotions"].items():
                print(f"  • {emotion}: {strength}")
            print(f"\n🏷️  关键词: {', '.join(result['analysis']['keywords'])}")
        
        elif args.command == "batch":
            # 批量分析
            dreams = []
            
            if args.file:
                with open(args.file, 'r', encoding='utf-8') as f:
                    dreams = json.load(f)
            elif args.dir:
                loaded = controller.load_dreams_from_files(args.dir)
                dreams = [{"text": d, "date": date} for d, date in loaded]
            else:
                # 使用默认目录
                loaded = controller.load_dreams_from_files()
                dreams = [{"text": d, "date": date} for d, date in loaded]
            
            if not dreams:
                print("❌ 没有找到梦境数据")
                return
            
            results = controller.analyze_multiple_dreams(dreams)
            print(f"\n✅ 批量分析完成: {len(results)} 个梦境")
            for result in results:
                print(f"  • {result['dream_id']}: {result['summary']}")
        
        elif args.command == "associate":
            # 发现关联
            if not controller.dream_database:
                # 加载默认数据
                loaded = controller.load_dreams_from_files()
                controller.analyze_multiple_dreams(
                    [{"text": d, "date": date} for d, date in loaded]
                )
            
            result = controller.find_associations()
            print(f"\n🔗 关联分析结果")
            print(f"📊 总梦境数: {result['total_dreams']}")
            print(f"🔗 关联数: {result['summary']['total_correlations']}")
            print(f"📈 模式数: {result['summary']['patterns_found']}")
            print(f"🌀 周期数: {result['summary']['cycles_detected']}")
            
            if result["correlations"]:
                print(f"\n主要关联:")
                for i, corr in enumerate(result["correlations"][:5], 1):
                    print(f"\n  {i}. [{corr['type']}] 相似度: {corr.get('similarity_score', corr.get('emotion_similarity', 0))}")
                    print(f"     {corr['dream1']['date']} <-> {corr['dream2']['date']}")
            
            if result["summary"]["key_insights"]:
                print(f"\n💡 关键洞察:")
                for i, insight in enumerate(result["summary"]["key_insights"], 1):
                    print(f"  {i}. {insight}")
        
        elif args.command == "insight":
            # 生成洞察
            if not controller.dream_database:
                loaded = controller.load_dreams_from_files()
                controller.analyze_multiple_dreams(
                    [{"text": d, "date": date} for d, date in loaded]
                )
            
            result = controller.generate_insights(args.dream_id)
            
            if result.get("status") == "error":
                print(f"❌ {result['message']}")
                return
            
            print(f"\n💡 梦境洞察")
            print(f"📊 分析了 {result['dreams_analyzed']} 个梦境")
            
            for dream_insights in result["insights"]:
                print(f"\n🎯 梦境: {dream_insights['dream_id']}")
                print(f"{'='*60}")
                
                for insight in dream_insights["insights"]:
                    print(f"\n📌 [{insight['type']}] 重要性: {insight['importance']}")
                    print(f"   {insight['insight']}")
                
                if dream_insights["suggestions"]:
                    print(f"\n🎯 建议:")
                    for suggestion in dream_insights["suggestions"][:3]:
                        print(f"   • {suggestion}")
                
                if dream_insights["reflection_prompts"]:
                    print(f"\n🤔 思考问题:")
                    for prompt in dream_insights["reflection_prompts"][:2]:
                        print(f"   • {prompt}")
        
        elif args.command == "report":
            # 生成完整报告
            result = controller.generate_full_report(args.dream_id)
            
            if result.get("status") == "error":
                print(f"❌ {result['message']}")
                return
            
            print(f"\n📄 梦境分析完整报告")
            print(f"{'='*70}")
            print(f"生成时间: {result['generated_at']}")
            print(f"\n📊 摘要:")
            summary = result["summary"]
            print(f"  • 梦境总数: {summary['total_dreams_in_database']}")
            print(f"  • 分析梦境: {summary['dreams_analyzed']}")
            print(f"  • 关联发现: {summary['total_correlations']}")
            print(f"  • 模式识别: {summary['total_patterns']}")
            print(f"  • 周期检测: {summary['total_cycles']}")
            print(f"  • 洞察生成: {summary['total_insights']}")
            
            if result["key_findings"]:
                print(f"\n🌟 关键发现:")
                for i, finding in enumerate(result["key_findings"], 1):
                    print(f"  {i}. {finding}")
            
            if result["recommendations"]:
                print(f"\n🎯 建议:")
                for i, recommendation in enumerate(result["recommendations"], 1):
                    print(f"  {i}. {recommendation}")
            
            if args.save:
                filepath = controller.save_report(result)
                print(f"\n💾 报告已保存: {filepath}")
        
        elif args.command == "load":
            # 加载文件
            loaded = controller.load_dreams_from_files(args.dir)
            print(f"\n📂 已加载 {len(loaded)} 个梦境日志")
            for date, content in loaded:
                print(f"  • {date}: {content[:50]}...")
            
            # 自动分析
            if loaded:
                print(f"\n🔍 开始自动分析...")
                controller.analyze_multiple_dreams(
                    [{"text": d, "date": date} for d, date in loaded]
                )
                print(f"✅ 分析完成!")
    
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
