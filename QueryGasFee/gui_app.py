#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QueryGasFee GUI应用

基于tkinter的简单直观可视化操作界面
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import asyncio
import threading
from datetime import datetime, timedelta
import json
from pathlib import Path
import webbrowser
from typing import Dict, List, Optional

# 导入项目模块
from main import GasFeeTracker
from config import config
from config_manager import check_api_keys, check_env_file
from visualizer import GasFeeVisualizer

class GasFeeGUI:
    """Gas费用追踪器GUI主类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Gas Fee Tracker - 区块链Gas费用分析工具")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # 设置样式
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # 初始化变量
        self.tracker = GasFeeTracker()
        self.current_results = None
        self.is_analyzing = False
        
        # 创建界面
        self.create_widgets()
        self.check_configuration()
        
    def create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="🔗 Gas Fee Tracker", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 配置检查状态
        self.config_frame = ttk.LabelFrame(main_frame, text="配置状态", padding="10")
        self.config_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.config_status_label = ttk.Label(self.config_frame, text="检查配置中...")
        self.config_status_label.grid(row=0, column=0, sticky=tk.W)
        
        ttk.Button(self.config_frame, text="重新检查配置", 
                  command=self.check_configuration).grid(row=0, column=1, padx=(10, 0))
        
        # 查询参数框架
        params_frame = ttk.LabelFrame(main_frame, text="查询参数", padding="10")
        params_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        params_frame.columnconfigure(1, weight=1)
        
        # 地址输入
        ttk.Label(params_frame, text="钱包地址:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.address_entry = ttk.Entry(params_frame, width=50)
        self.address_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # 链选择
        ttk.Label(params_frame, text="区块链:").grid(row=1, column=0, sticky=tk.W, pady=2)
        chain_frame = ttk.Frame(params_frame)
        chain_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        self.chain_vars = {}
        chains = ['ethereum', 'bsc', 'polygon', 'arbitrum', 'optimism', 'avalanche']
        chain_names = ['Ethereum', 'BSC', 'Polygon', 'Arbitrum', 'Optimism', 'Avalanche']
        
        for i, (chain, name) in enumerate(zip(chains, chain_names)):
            var = tk.BooleanVar(value=True if chain == 'ethereum' else False)
            self.chain_vars[chain] = var
            ttk.Checkbutton(chain_frame, text=name, variable=var).grid(
                row=i//3, column=i%3, sticky=tk.W, padx=(0, 10))
        
        # 时间范围
        ttk.Label(params_frame, text="时间范围:").grid(row=2, column=0, sticky=tk.W, pady=2)
        time_frame = ttk.Frame(params_frame)
        time_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        self.time_range_var = tk.StringVar(value="last_7_days")
        time_options = [
            ("最近7天", "last_7_days"),
            ("最近30天", "last_30_days"),
            ("最近90天", "last_90_days"),
            ("自定义", "custom")
        ]
        
        for i, (text, value) in enumerate(time_options):
            ttk.Radiobutton(time_frame, text=text, variable=self.time_range_var, 
                           value=value, command=self.on_time_range_change).grid(
                row=0, column=i, sticky=tk.W, padx=(0, 10))
        
        # 自定义时间范围
        self.custom_time_frame = ttk.Frame(params_frame)
        self.custom_time_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        ttk.Label(self.custom_time_frame, text="开始日期:").grid(row=0, column=0, sticky=tk.W)
        self.start_date_entry = ttk.Entry(self.custom_time_frame, width=12)
        self.start_date_entry.grid(row=0, column=1, padx=(5, 10))
        self.start_date_entry.insert(0, (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'))
        
        ttk.Label(self.custom_time_frame, text="结束日期:").grid(row=0, column=2, sticky=tk.W)
        self.end_date_entry = ttk.Entry(self.custom_time_frame, width=12)
        self.end_date_entry.grid(row=0, column=3, padx=(5, 0))
        self.end_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        # 初始隐藏自定义时间框架
        self.custom_time_frame.grid_remove()
        
        # 控制按钮
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        self.analyze_button = ttk.Button(control_frame, text="🔍 开始分析", 
                                        command=self.start_analysis)
        self.analyze_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="⏹ 停止分析", 
                                     command=self.stop_analysis, state='disabled')
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Button(control_frame, text="📊 生成图表", 
                  command=self.generate_charts).grid(row=0, column=2, padx=(0, 10))
        
        ttk.Button(control_frame, text="💾 保存结果", 
                  command=self.save_results).grid(row=0, column=3, padx=(0, 10))
        
        ttk.Button(control_frame, text="📁 打开结果目录", 
                  command=self.open_results_folder).grid(row=0, column=4)
        
        # 结果显示区域
        results_frame = ttk.LabelFrame(main_frame, text="分析结果", padding="10")
        results_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # 创建Notebook用于多标签页
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 概览标签页
        self.summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_frame, text="📊 概览")
        
        self.summary_text = scrolledtext.ScrolledText(self.summary_frame, wrap=tk.WORD, 
                                                     height=15, font=('Consolas', 10))
        self.summary_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.summary_frame.columnconfigure(0, weight=1)
        self.summary_frame.rowconfigure(0, weight=1)
        
        # 详细数据标签页
        self.details_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.details_frame, text="📋 详细数据")
        
        # 创建Treeview显示交易数据
        columns = ('hash', 'chain', 'timestamp', 'gas_fee_eth', 'gas_fee_usd', 'tx_type')
        self.tree = ttk.Treeview(self.details_frame, columns=columns, show='headings', height=15)
        
        # 设置列标题
        self.tree.heading('hash', text='交易哈希')
        self.tree.heading('chain', text='区块链')
        self.tree.heading('timestamp', text='时间')
        self.tree.heading('gas_fee_eth', text='Gas费用(ETH)')
        self.tree.heading('gas_fee_usd', text='Gas费用(USD)')
        self.tree.heading('tx_type', text='交易类型')
        
        # 设置列宽
        self.tree.column('hash', width=150)
        self.tree.column('chain', width=80)
        self.tree.column('timestamp', width=120)
        self.tree.column('gas_fee_eth', width=100)
        self.tree.column('gas_fee_usd', width=100)
        self.tree.column('tx_type', width=80)
        
        # 添加滚动条
        tree_scrollbar = ttk.Scrollbar(self.details_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.details_frame.columnconfigure(0, weight=1)
        self.details_frame.rowconfigure(0, weight=1)
        
        # 日志标签页
        self.log_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.log_frame, text="📝 日志")
        
        self.log_text = scrolledtext.ScrolledText(self.log_frame, wrap=tk.WORD, 
                                                 height=15, font=('Consolas', 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.log_frame.columnconfigure(0, weight=1)
        self.log_frame.rowconfigure(0, weight=1)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def on_time_range_change(self):
        """时间范围选择变化处理"""
        if self.time_range_var.get() == "custom":
            self.custom_time_frame.grid()
        else:
            self.custom_time_frame.grid_remove()
    
    def check_configuration(self):
        """检查配置状态"""
        try:
            env_exists = check_env_file()
            if env_exists:
                api_keys = config.api_config.get_api_keys()
                valid_keys = [k for k in api_keys.values() 
                             if k and k != "YOUR_API_KEY_HERE" and len(k) > 10]
                
                if valid_keys:
                    self.config_status_label.config(
                        text=f"✅ 配置正常 - 发现 {len(valid_keys)} 个有效API密钥",
                        foreground='green'
                    )
                    return True
                else:
                    self.config_status_label.config(
                        text="❌ 未配置API密钥",
                        foreground='red'
                    )
            else:
                self.config_status_label.config(
                    text="❌ .env文件不存在",
                    foreground='red'
                )
        except Exception as e:
            self.config_status_label.config(
                text=f"❌ 配置检查失败: {str(e)}",
                foreground='red'
            )
        return False
    
    def get_selected_chains(self) -> List[str]:
        """获取选中的区块链"""
        return [chain for chain, var in self.chain_vars.items() if var.get()]
    
    def get_time_range(self) -> tuple:
        """获取时间范围"""
        range_type = self.time_range_var.get()
        
        if range_type == "last_7_days":
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
        elif range_type == "last_30_days":
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
        elif range_type == "last_90_days":
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
        elif range_type == "custom":
            try:
                start_date = datetime.strptime(self.start_date_entry.get(), '%Y-%m-%d')
                end_date = datetime.strptime(self.end_date_entry.get(), '%Y-%m-%d')
            except ValueError:
                raise ValueError("日期格式错误，请使用 YYYY-MM-DD 格式")
        else:
            return None, None
        
        return start_date, end_date
    
    def log_message(self, message: str):
        """添加日志消息"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def start_analysis(self):
        """开始分析"""
        # 验证输入
        address = self.address_entry.get().strip()
        if not address:
            messagebox.showerror("错误", "请输入钱包地址")
            return
        
        selected_chains = self.get_selected_chains()
        if not selected_chains:
            messagebox.showerror("错误", "请至少选择一个区块链")
            return
        
        try:
            start_date, end_date = self.get_time_range()
        except ValueError as e:
            messagebox.showerror("错误", str(e))
            return
        
        # 检查配置
        if not self.check_configuration():
            messagebox.showerror("错误", "配置检查失败，请检查API密钥配置")
            return
        
        # 清空之前的结果
        self.summary_text.delete(1.0, tk.END)
        self.log_text.delete(1.0, tk.END)
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 更新UI状态
        self.is_analyzing = True
        self.analyze_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.status_var.set("分析中...")
        
        # 在新线程中运行分析
        self.analysis_thread = threading.Thread(
            target=self.run_analysis,
            args=(address, selected_chains, start_date, end_date)
        )
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
    
    def run_analysis(self, address: str, chains: List[str], start_date, end_date):
        """在后台线程中运行分析"""
        try:
            # 创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            self.log_message(f"开始分析地址: {address}")
            self.log_message(f"选择的链: {', '.join(chains)}")
            if start_date and end_date:
                self.log_message(f"时间范围: {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}")
            
            # 获取API密钥
            api_keys = config.api_config.get_api_keys()
            
            # 运行分析
            async def analyze():
                async with self.tracker:
                    results = await self.tracker.analyze_gas_fees(
                        addresses=[address],
                        chains=chains,
                        api_keys=api_keys,
                        start_date=start_date,
                        end_date=end_date
                    )
                return results
            
            results = loop.run_until_complete(analyze())
            
            # 在主线程中更新UI
            self.root.after(0, self.on_analysis_complete, results)
            
        except Exception as e:
            self.root.after(0, self.on_analysis_error, str(e))
        finally:
            loop.close()
    
    def on_analysis_complete(self, results: Dict):
        """分析完成回调"""
        self.current_results = results
        self.is_analyzing = False
        
        # 更新UI状态
        self.analyze_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_var.set("分析完成")
        
        self.log_message("分析完成！")
        
        # 显示结果
        self.display_results(results)
    
    def on_analysis_error(self, error_msg: str):
        """分析错误回调"""
        self.is_analyzing = False
        
        # 更新UI状态
        self.analyze_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_var.set("分析失败")
        
        self.log_message(f"分析失败: {error_msg}")
        messagebox.showerror("分析失败", f"分析过程中发生错误:\n{error_msg}")
    
    def stop_analysis(self):
        """停止分析"""
        self.is_analyzing = False
        self.analyze_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_var.set("已停止")
        self.log_message("用户停止了分析")
    
    def display_results(self, results: Dict):
        """显示分析结果"""
        if 'error' in results:
            self.summary_text.insert(tk.END, f"错误: {results['error']}")
            return
        
        # 显示概览信息
        stats = results.get('statistics', {})
        summary = stats.get('summary', {})
        
        summary_text = f"""
📊 Gas费用分析报告
{'='*50}

📈 总体统计:
• 总交易数量: {summary.get('total_transactions', 0):,}
• 总Gas费用: {summary.get('total_gas_fee_eth', 0):.6f} ETH
• 平均Gas费用: {summary.get('avg_gas_fee_eth', 0):.6f} ETH
"""
        
        if summary.get('total_gas_fee_usd'):
            summary_text += f"• 总Gas费用: ${summary.get('total_gas_fee_usd', 0):.2f} USD\n"
            summary_text += f"• 平均Gas费用: ${summary.get('avg_gas_fee_usd', 0):.2f} USD\n"
        
        date_range = summary.get('date_range', {})
        if date_range:
            summary_text += f"• 时间范围: {date_range.get('start', 'N/A')} 到 {date_range.get('end', 'N/A')}\n"
        
        # 按链统计
        by_chain = stats.get('by_chain', {})
        if by_chain:
            summary_text += f"\n🔗 按区块链统计:\n"
            for chain, data in by_chain.items():
                summary_text += f"• {chain.upper()}:\n"
                summary_text += f"  - 交易数量: {data.get('transaction_count', 0):,}\n"
                summary_text += f"  - 总费用: {data.get('total_gas_fee_eth', 0):.6f} ETH\n"
                summary_text += f"  - 平均费用: {data.get('avg_gas_fee_eth', 0):.6f} ETH\n"
                summary_text += f"  - 平均Gas价格: {data.get('avg_gas_price_gwei', 0):.2f} Gwei\n\n"
        
        # Gas价格分析
        gas_analysis = stats.get('gas_price_analysis', {})
        if gas_analysis:
            summary_text += f"⛽ Gas价格分析:\n"
            summary_text += f"• 最低: {gas_analysis.get('min_gwei', 0):.2f} Gwei\n"
            summary_text += f"• 最高: {gas_analysis.get('max_gwei', 0):.2f} Gwei\n"
            summary_text += f"• 平均: {gas_analysis.get('avg_gwei', 0):.2f} Gwei\n"
            summary_text += f"• 中位数: {gas_analysis.get('median_gwei', 0):.2f} Gwei\n"
        
        self.summary_text.insert(tk.END, summary_text)
        
        # 显示交易详情
        transactions = results.get('transactions', [])
        for tx in transactions[:1000]:  # 限制显示数量
            timestamp_str = datetime.fromtimestamp(tx['timestamp']).strftime('%Y-%m-%d %H:%M')
            gas_fee_usd = f"${tx['gas_fee_usd']:.4f}" if tx['gas_fee_usd'] else "N/A"
            
            self.tree.insert('', tk.END, values=(
                tx['hash'][:16] + '...',
                tx['chain'].upper(),
                timestamp_str,
                f"{tx['gas_fee_eth']:.6f}",
                gas_fee_usd,
                tx['transaction_type']
            ))
    
    def generate_charts(self):
        """生成图表"""
        if not self.current_results:
            messagebox.showwarning("警告", "请先进行分析")
            return
        
        try:
            self.status_var.set("生成图表中...")
            self.log_message("开始生成图表...")
            
            # 创建可视化器
            visualizer = GasFeeVisualizer(stats_data=self.current_results)
            
            # 生成所有图表
            visualizer.generate_all_charts()
            
            self.status_var.set("图表生成完成")
            self.log_message("图表生成完成！")
            
            # 询问是否打开图表目录
            if messagebox.askyesno("图表生成完成", "图表已生成完成！是否打开图表目录？"):
                self.open_charts_folder()
                
        except Exception as e:
            self.status_var.set("图表生成失败")
            self.log_message(f"图表生成失败: {str(e)}")
            messagebox.showerror("错误", f"图表生成失败:\n{str(e)}")
    
    def save_results(self):
        """保存结果"""
        if not self.current_results:
            messagebox.showwarning("警告", "请先进行分析")
            return
        
        try:
            # 保存结果
            self.tracker.save_results(self.current_results)
            
            self.status_var.set("结果保存完成")
            self.log_message("分析结果已保存到 Data_Save 目录")
            
            # 询问是否打开结果目录
            if messagebox.askyesno("保存完成", "结果已保存！是否打开结果目录？"):
                self.open_results_folder()
                
        except Exception as e:
            self.status_var.set("保存失败")
            self.log_message(f"保存失败: {str(e)}")
            messagebox.showerror("错误", f"保存失败:\n{str(e)}")
    
    def open_results_folder(self):
        """打开结果目录"""
        try:
            data_save_path = Path("Data_Save").absolute()
            if data_save_path.exists():
                import subprocess
                subprocess.run(['explorer', str(data_save_path)], check=True)
            else:
                messagebox.showinfo("提示", "Data_Save目录不存在")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开目录:\n{str(e)}")
    
    def open_charts_folder(self):
        """打开图表目录"""
        try:
            charts_path = Path("charts").absolute()
            if charts_path.exists():
                import subprocess
                subprocess.run(['explorer', str(charts_path)], check=True)
            else:
                messagebox.showinfo("提示", "charts目录不存在")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开目录:\n{str(e)}")

def main():
    """主函数"""
    root = tk.Tk()
    app = GasFeeGUI(root)
    
    # 设置窗口图标（如果有的话）
    try:
        # root.iconbitmap('icon.ico')  # 如果有图标文件
        pass
    except:
        pass
    
    # 启动GUI
    root.mainloop()

if __name__ == "__main__":
    main()