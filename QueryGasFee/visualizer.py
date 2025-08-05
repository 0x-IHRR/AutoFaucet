#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据可视化模块
提供gas费用数据的图表展示功能
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 设置样式
sns.set_style("whitegrid")
plt.style.use('seaborn-v0_8')

class GasFeeVisualizer:
    """Gas费用数据可视化器"""
    
    def __init__(self, stats_data: Dict = None, stats_file: str = None):
        """初始化可视化器
        
        Args:
            stats_data: 统计数据字典
            stats_file: 统计数据文件路径
        """
        if stats_data:
            self.stats = stats_data
        elif stats_file:
            self.stats = self.load_stats_file(stats_file)
        else:
            raise ValueError("必须提供stats_data或stats_file")
        
        self.output_dir = Path("charts")
        self.output_dir.mkdir(exist_ok=True)
    
    def load_stats_file(self, file_path: str) -> Dict:
        """加载统计数据文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def create_daily_gas_chart(self, save_html: bool = True, save_png: bool = True) -> go.Figure:
        """创建每日gas费用趋势图"""
        if 'by_date' not in self.stats:
            print("❌ 缺少按日期统计数据")
            return None
        
        # 准备数据
        dates = []
        daily_fees_eth = []
        daily_fees_usd = []
        transaction_counts = []
        avg_gas_prices = []
        
        for date, data in sorted(self.stats['by_date'].items()):
            dates.append(date)
            daily_fees_eth.append(data['total_gas_fee_eth'])
            daily_fees_usd.append(data.get('total_gas_fee_usd', 0))
            transaction_counts.append(data['transaction_count'])
            avg_gas_prices.append(data['avg_gas_price_gwei'])
        
        # 创建子图
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('每日Gas费用 (ETH)', '每日Gas费用 (USD)', '每日交易数量', '平均Gas价格 (Gwei)'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # 添加图表
        fig.add_trace(
            go.Scatter(x=dates, y=daily_fees_eth, mode='lines+markers', name='ETH费用',
                      line=dict(color='#1f77b4', width=2), marker=dict(size=6)),
            row=1, col=1
        )
        
        if any(daily_fees_usd):
            fig.add_trace(
                go.Scatter(x=dates, y=daily_fees_usd, mode='lines+markers', name='USD费用',
                          line=dict(color='#ff7f0e', width=2), marker=dict(size=6)),
                row=1, col=2
            )
        
        fig.add_trace(
            go.Bar(x=dates, y=transaction_counts, name='交易数量',
                   marker=dict(color='#2ca02c', opacity=0.7)),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=dates, y=avg_gas_prices, mode='lines+markers', name='平均Gas价格',
                      line=dict(color='#d62728', width=2), marker=dict(size=6)),
            row=2, col=2
        )
        
        # 更新布局
        fig.update_layout(
            title=dict(
                text='📊 Gas费用每日趋势分析',
                x=0.5,
                font=dict(size=20)
            ),
            height=800,
            showlegend=False,
            template='plotly_white'
        )
        
        # 更新坐标轴
        fig.update_xaxes(title_text="日期", row=2, col=1)
        fig.update_xaxes(title_text="日期", row=2, col=2)
        fig.update_yaxes(title_text="ETH", row=1, col=1)
        fig.update_yaxes(title_text="USD", row=1, col=2)
        fig.update_yaxes(title_text="交易数量", row=2, col=1)
        fig.update_yaxes(title_text="Gwei", row=2, col=2)
        
        # 保存文件
        if save_html:
            html_path = self.output_dir / "daily_gas_trends.html"
            fig.write_html(str(html_path))
            print(f"📊 每日趋势图已保存: {html_path}")
        
        if save_png:
            png_path = self.output_dir / "daily_gas_trends.png"
            fig.write_image(str(png_path), width=1200, height=800)
            print(f"📊 每日趋势图已保存: {png_path}")
        
        return fig
    
    def create_chain_comparison_chart(self, save_html: bool = True, save_png: bool = True) -> go.Figure:
        """创建链对比图"""
        if 'by_chain' not in self.stats:
            print("❌ 缺少按链统计数据")
            return None
        
        # 准备数据
        chains = list(self.stats['by_chain'].keys())
        transaction_counts = [self.stats['by_chain'][chain]['transaction_count'] for chain in chains]
        total_fees_eth = [self.stats['by_chain'][chain]['total_gas_fee_eth'] for chain in chains]
        avg_fees_eth = [self.stats['by_chain'][chain]['avg_gas_fee_eth'] for chain in chains]
        avg_gas_prices = [self.stats['by_chain'][chain]['avg_gas_price_gwei'] for chain in chains]
        
        # 创建子图
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('各链交易数量', '各链总Gas费用 (ETH)', '各链平均Gas费用 (ETH)', '各链平均Gas价格 (Gwei)'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # 颜色配置
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        
        # 添加图表
        fig.add_trace(
            go.Bar(x=chains, y=transaction_counts, name='交易数量',
                   marker=dict(color=colors[:len(chains)])),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(x=chains, y=total_fees_eth, name='总费用',
                   marker=dict(color=colors[:len(chains)])),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Bar(x=chains, y=avg_fees_eth, name='平均费用',
                   marker=dict(color=colors[:len(chains)])),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Bar(x=chains, y=avg_gas_prices, name='平均Gas价格',
                   marker=dict(color=colors[:len(chains)])),
            row=2, col=2
        )
        
        # 更新布局
        fig.update_layout(
            title=dict(
                text='🔗 各链Gas费用对比分析',
                x=0.5,
                font=dict(size=20)
            ),
            height=800,
            showlegend=False,
            template='plotly_white'
        )
        
        # 更新坐标轴
        fig.update_yaxes(title_text="交易数量", row=1, col=1)
        fig.update_yaxes(title_text="ETH", row=1, col=2)
        fig.update_yaxes(title_text="ETH", row=2, col=1)
        fig.update_yaxes(title_text="Gwei", row=2, col=2)
        
        # 保存文件
        if save_html:
            html_path = self.output_dir / "chain_comparison.html"
            fig.write_html(str(html_path))
            print(f"📊 链对比图已保存: {html_path}")
        
        if save_png:
            png_path = self.output_dir / "chain_comparison.png"
            fig.write_image(str(png_path), width=1200, height=800)
            print(f"📊 链对比图已保存: {png_path}")
        
        return fig
    
    def create_transaction_type_chart(self, save_html: bool = True, save_png: bool = True) -> go.Figure:
        """创建交易类型分布图"""
        if 'by_transaction_type' not in self.stats:
            print("❌ 缺少按交易类型统计数据")
            return None
        
        # 准备数据
        tx_types = list(self.stats['by_transaction_type'].keys())
        counts = [self.stats['by_transaction_type'][tx_type]['transaction_count'] for tx_type in tx_types]
        fees = [self.stats['by_transaction_type'][tx_type]['total_gas_fee_eth'] for tx_type in tx_types]
        
        # 创建子图
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('交易类型数量分布', '交易类型费用分布'),
            specs=[[{"type": "pie"}, {"type": "pie"}]]
        )
        
        # 添加饼图
        fig.add_trace(
            go.Pie(labels=tx_types, values=counts, name="交易数量",
                   textinfo='label+percent', textposition='auto'),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Pie(labels=tx_types, values=fees, name="Gas费用",
                   textinfo='label+percent', textposition='auto'),
            row=1, col=2
        )
        
        # 更新布局
        fig.update_layout(
            title=dict(
                text='📝 交易类型分布分析',
                x=0.5,
                font=dict(size=20)
            ),
            height=500,
            template='plotly_white'
        )
        
        # 保存文件
        if save_html:
            html_path = self.output_dir / "transaction_types.html"
            fig.write_html(str(html_path))
            print(f"📊 交易类型图已保存: {html_path}")
        
        if save_png:
            png_path = self.output_dir / "transaction_types.png"
            fig.write_image(str(png_path), width=1200, height=500)
            print(f"📊 交易类型图已保存: {png_path}")
        
        return fig
    
    def create_gas_price_distribution(self, save_html: bool = True, save_png: bool = True) -> go.Figure:
        """创建Gas价格分布图"""
        if 'gas_price_analysis' not in self.stats:
            print("❌ 缺少Gas价格分析数据")
            return None
        
        gas_analysis = self.stats['gas_price_analysis']
        
        # 创建Gas价格统计图
        fig = go.Figure()
        
        # 添加柱状图显示统计信息
        categories = ['最低价格', '平均价格', '中位数价格', '最高价格']
        values = [
            gas_analysis['min_gwei'],
            gas_analysis['avg_gwei'],
            gas_analysis['median_gwei'],
            gas_analysis['max_gwei']
        ]
        
        colors = ['#2ca02c', '#1f77b4', '#ff7f0e', '#d62728']
        
        fig.add_trace(
            go.Bar(
                x=categories,
                y=values,
                marker=dict(color=colors),
                text=[f'{v:.2f} Gwei' for v in values],
                textposition='auto'
            )
        )
        
        # 更新布局
        fig.update_layout(
            title=dict(
                text='⛽ Gas价格分布分析',
                x=0.5,
                font=dict(size=20)
            ),
            xaxis_title="统计类型",
            yaxis_title="Gas价格 (Gwei)",
            height=500,
            template='plotly_white'
        )
        
        # 保存文件
        if save_html:
            html_path = self.output_dir / "gas_price_distribution.html"
            fig.write_html(str(html_path))
            print(f"📊 Gas价格分布图已保存: {html_path}")
        
        if save_png:
            png_path = self.output_dir / "gas_price_distribution.png"
            fig.write_image(str(png_path), width=1000, height=500)
            print(f"📊 Gas价格分布图已保存: {png_path}")
        
        return fig
    
    def create_address_comparison(self, save_html: bool = True, save_png: bool = True) -> go.Figure:
        """创建地址对比图"""
        if 'by_address' not in self.stats:
            print("❌ 缺少按地址统计数据")
            return None
        
        # 准备数据
        addresses = list(self.stats['by_address'].keys())
        # 简化地址显示
        short_addresses = [f"{addr[:6]}...{addr[-4:]}" for addr in addresses]
        
        transaction_counts = [self.stats['by_address'][addr]['transaction_count'] for addr in addresses]
        total_fees = [self.stats['by_address'][addr]['total_gas_fee_eth'] for addr in addresses]
        avg_fees = [self.stats['by_address'][addr]['avg_gas_fee_eth'] for addr in addresses]
        
        # 创建子图
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=('各地址交易数量', '各地址总Gas费用 (ETH)', '各地址平均Gas费用 (ETH)'),
            specs=[[{"type": "bar"}, {"type": "bar"}, {"type": "bar"}]]
        )
        
        # 颜色配置
        colors = px.colors.qualitative.Set3[:len(addresses)]
        
        # 添加图表
        fig.add_trace(
            go.Bar(x=short_addresses, y=transaction_counts, name='交易数量',
                   marker=dict(color=colors)),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(x=short_addresses, y=total_fees, name='总费用',
                   marker=dict(color=colors)),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Bar(x=short_addresses, y=avg_fees, name='平均费用',
                   marker=dict(color=colors)),
            row=1, col=3
        )
        
        # 更新布局
        fig.update_layout(
            title=dict(
                text='👤 各地址Gas费用对比',
                x=0.5,
                font=dict(size=20)
            ),
            height=600,
            showlegend=False,
            template='plotly_white'
        )
        
        # 更新坐标轴
        fig.update_yaxes(title_text="交易数量", row=1, col=1)
        fig.update_yaxes(title_text="ETH", row=1, col=2)
        fig.update_yaxes(title_text="ETH", row=1, col=3)
        
        # 保存文件
        if save_html:
            html_path = self.output_dir / "address_comparison.html"
            fig.write_html(str(html_path))
            print(f"📊 地址对比图已保存: {html_path}")
        
        if save_png:
            png_path = self.output_dir / "address_comparison.png"
            fig.write_image(str(png_path), width=1400, height=600)
            print(f"📊 地址对比图已保存: {png_path}")
        
        return fig
    
    def create_comprehensive_dashboard(self, save_html: bool = True) -> go.Figure:
        """创建综合仪表板"""
        print("\n📊 正在生成综合仪表板...")
        
        # 创建所有图表
        daily_fig = self.create_daily_gas_chart(save_html=False, save_png=False)
        chain_fig = self.create_chain_comparison_chart(save_html=False, save_png=False)
        tx_type_fig = self.create_transaction_type_chart(save_html=False, save_png=False)
        gas_price_fig = self.create_gas_price_distribution(save_html=False, save_png=False)
        
        if self.stats.get('by_address') and len(self.stats['by_address']) > 1:
            address_fig = self.create_address_comparison(save_html=False, save_png=False)
        else:
            address_fig = None
        
        # 创建HTML仪表板
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Gas Fee 分析仪表板</title>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .summary {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            color: #666;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔥 Gas Fee 分析仪表板</h1>
        <p>Web3钱包链上gas费用统计分析报告</p>
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="summary">
        <h2>📊 总体统计摘要</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{self.stats['summary']['total_transactions']:,}</div>
                <div class="stat-label">总交易数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{self.stats['summary']['total_gas_fee_eth']:.4f}</div>
                <div class="stat-label">总Gas费用 (ETH)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{self.stats['summary']['avg_gas_fee_eth']:.6f}</div>
                <div class="stat-label">平均Gas费用 (ETH)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{self.stats['gas_price_analysis']['avg_gwei']:.2f}</div>
                <div class="stat-label">平均Gas价格 (Gwei)</div>
            </div>
        </div>
    </div>
"""
        
        # 添加图表
        charts = [
            (daily_fig, "每日Gas费用趋势"),
            (chain_fig, "各链对比分析"),
            (tx_type_fig, "交易类型分布"),
            (gas_price_fig, "Gas价格分析")
        ]
        
        if address_fig:
            charts.append((address_fig, "地址对比分析"))
        
        for fig, title in charts:
            if fig:
                chart_html = fig.to_html(include_plotlyjs='inline', div_id=f"chart_{title}")
                # 提取图表部分
                chart_div = chart_html.split('<div>')[1].split('</div>')[0]
                html_content += f"""
    <div class="chart-container">
        <h3>{title}</h3>
        <div>{chart_div}</div>
    </div>
"""
        
        html_content += """
</body>
</html>
"""
        
        # 保存仪表板
        if save_html:
            dashboard_path = self.output_dir / "gas_fee_dashboard.html"
            with open(dashboard_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"📊 综合仪表板已保存: {dashboard_path}")
        
        return None
    
    def generate_all_charts(self):
        """生成所有图表"""
        print("\n📊 开始生成所有可视化图表...")
        print(f"📁 图表保存目录: {self.output_dir.absolute()}")
        
        # 创建各种图表
        self.create_daily_gas_chart()
        self.create_chain_comparison_chart()
        self.create_transaction_type_chart()
        self.create_gas_price_distribution()
        
        if self.stats.get('by_address') and len(self.stats['by_address']) > 1:
            self.create_address_comparison()
        
        # 创建综合仪表板
        self.create_comprehensive_dashboard()
        
        print("\n✅ 所有图表生成完成!")
        print(f"📂 请查看 {self.output_dir.absolute()} 目录")

def visualize_from_file(stats_file: str):
    """从文件生成可视化图表"""
    try:
        visualizer = GasFeeVisualizer(stats_file=stats_file)
        visualizer.generate_all_charts()
    except Exception as e:
        print(f"❌ 可视化生成失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        stats_file = sys.argv[1]
        if Path(stats_file).exists():
            visualize_from_file(stats_file)
        else:
            print(f"❌ 文件不存在: {stats_file}")
    else:
        print("📖 使用方法: python visualizer.py <stats_file.json>")
        print("或者在其他脚本中导入使用:")
        print("from visualizer import GasFeeVisualizer")
        print("visualizer = GasFeeVisualizer(stats_data=your_stats)")
        print("visualizer.generate_all_charts()")