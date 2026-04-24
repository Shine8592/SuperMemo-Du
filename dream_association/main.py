#!/usr/bin/env python3
"""
梦境联想模式主程序
整合梦境分析、关联发现和洞察生成
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dream_association.analyzer import DreamAnalyzer
from dream_association.correlator import DreamCorrelator
from dream_association.generator import InsightGenerator


def main():
    """主程序"""
    print("\n" + "="*70)
    print("🌙 梦境联想模式 v1.0")
    print("="*70)
    
    # 初始化组件
    analyzer = DreamAnalyzer()
    correlator = DreamCorrelator(similarity_threshold=0.4)
    generator = InsightGenerator()
    
    # 获取梦境数据
    dream_file = os.path.join(os.path.dirname(__file__), '..', '..', 
                             'memory', 'daily', '2026-04-23.md')
    
    dreams = []
    
    # 从文件中读取梦境（如果存在）
    if os.path.exists(dream_file):
        with open(dream_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # 提取梦境内容
            if '梦境' in content or '梦' in content:
                dreams.append({
                    "content": content[:500],  # 限制长度
                    "date": "2026-04-23"
                })
    
    # 如果没有文件中的梦境，使用示例数据
    if not dreams:
        dreams = [
            {
                "content": "梦见自己在天空中自由飞翔，感觉非常开心和兴奋，没有任何束缚。",
                "date": "2026-04-21"
            },
            {
                "content": "梦见自己像鸟儿一样在天空中翱翔，感觉无比自由和快乐。",
                "date": "2026-04-23"
            },
            {
                "content": "梦见在考试中什么都不会，监考老师很严厉，我很紧张，很害怕。",
                "date": "2026-04-22"
            },
            {
                "content": "梦见和家人团聚，大家都很开心，吃了一顿丰盛的晚餐。",
                "date": "2026-04-20"
            }
        ]
    
    # 分析所有梦境
    print(f"\n📊 正在分析 {len(dreams)} 个梦境...")
    analyses = []
    
    for dream in dreams:
        result = analyzer.analyze(dream["content"], dream["date"])
        analyses.append(result)
        
        print(f"\n🌙 梦境 #{len(analyses)} ({dream['date']})")
        print(f"   内容: {dream['content'][:50]}...")
        print(f"   主题: {[t['theme'] for t in result['analysis']['themes'][:3]]}")
        print(f"   情感: {list(result['analysis']['emotions'].keys())}")
    
    # 发现关联
    print("\n" + "="*70)
    print("🔗 梦境关联发现")
    print("="*70)
    
    correlations = correlator.find_correlations(analyses)
    
    if correlations:
        for i, corr in enumerate(correlations[:5], 1):  # 显示前5个关联
            print(f"\n{i}. 🔗 {corr['dream1_id'][:8]} ↔ {corr['dream2_id'][:8]}")
            print(f"   相似度: {corr['overall_similarity']}")
            print(f"   类型: {corr['correlation_type']}")
            print(f"   共享主题: {corr['shared_themes']}")
            print(f"   解释: {corr['interpretation']}")
    else:
        print("\n未发现明显的梦境关联")
    
    # 识别模式
    print("\n" + "="*70)
    print("📊 模式识别")
    print("="*70)
    
    patterns = correlator.identify_patterns(analyses)
    
    if patterns:
        for i, pattern in enumerate(patterns[:5], 1):  # 显示前5个模式
            print(f"\n{i}. 🏷️  {pattern['type'].upper()}: {pattern['pattern']}")
            print(f"   频率: {pattern.get('frequency', 'N/A')}")
            print(f"   重要性: {pattern['importance']}")
            print(f"   解释: {pattern['interpretation']}")
    else:
        print("\n未发现明显的模式")
    
    # 检测周期
    print("\n" + "="*70)
    print("🔄 周期检测")
    print("="*70)
    
    cycles = correlator.detect_cycles(analyses)
    
    if cycles:
        for i, cycle in enumerate(cycles, 1):
            print(f"\n{i}. 🔄 {cycle['type']}")
            print(f"   模式: {cycle['pattern']}")
            print(f"   周期: {cycle['period']}")
            print(f"   重要性: {cycle['importance']}")
    else:
        print("\n未检测到明显的周期性模式")
    
    # 构建梦境图
    print("\n" + "="*70)
    print("🌐 梦境关联图")
    print("="*70)
    
    graph = correlator.build_dream_graph(analyses, correlations)
    
    print(f"\n节点数: {graph['metadata']['total_dreams']}")
    print(f"边数: {graph['metadata']['total_correlations']}")
    print(f"密度: {graph['metadata']['density']:.3f}")
    
    print("\n主要节点:")
    for node in graph['nodes'][:5]:
        print(f"  • {node['label'][:30]}... ({node['date']})")
    
    # 生成洞察
    print("\n" + "="*70)
    print("💡 梦境洞察")
    print("="*70)
    
    # 为最重要的梦境生成洞察
    main_dream = analyses[0]
    insights_result = generator.generate_insights(
        main_dream,
        user_context={
            "current_focus": "personal_growth",
            "recent_events": "seeking_new_challenges"
        },
        correlations=correlations,
        patterns=patterns
    )
    
    print(f"\n梦境: {main_dream['content'][:80]}...")
    print(f"洞察重要性: {insights_result['importance']}")
    
    print(f"\n💭 主要洞察:")
    for i, insight in enumerate(insights_result["insights"][:3], 1):
        print(f"\n{i}. {insight['insight']}")
        print(f"   类型: {insight['type']} | 重要性: {insight['importance']}")
    
    print(f"\n🎯 建议行动:")
    for i, suggestion in enumerate(insights_result["suggestions"][:3], 1):
        print(f"{i}. {suggestion['suggestion']}")
    
    print(f"\n🤔 反思:")
    for i, prompt in enumerate(insights_result["reflection_prompts"][:2], 1):
        print(f"{i}. {prompt}")
    
    # 保存结果
    print("\n" + "="*70)
    print("💾 保存结果")
    print("="*70)
    
    results_dir = os.path.join(os.path.dirname(__file__), '..', '..',
                              'memory', 'dream_association_results')
    os.makedirs(results_dir, exist_ok=True)
    
    # 保存详细分析
    detailed_results = {
        "analyses": analyses,
        "correlations": correlations,
        "patterns": patterns,
        "cycles": cycles,
        "graph": graph,
        "insights": insights_result,
        "generated_at": datetime.now().isoformat()
    }
    
    results_file = os.path.join(results_dir, 
                               f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(detailed_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存到: {results_file}")
    
    print("\n" + "="*70)
    print("✅ 梦境联想分析完成!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
