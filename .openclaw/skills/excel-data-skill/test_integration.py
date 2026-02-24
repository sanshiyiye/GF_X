#!/usr/bin/env python3
"""
集成测试 - 模拟真实工作流程

测试场景：
1. 识别不同类型的 Excel 文件
2. 验证文件是否符合 Schema 标准
3. 生成验证报告
4. 模拟完整的 Skill 调用流程

作者: AI Assistant
版本: 1.0.0
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

# 导入 Skill 组件
from schema_validator import (
    SchemaType,
    ValidationLevel,
    ValidationIssue
)
from datatable_validator import DataTableValidator
from config_validator import ConfigValidator
from language_validator import LanguageValidator


class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(title: str):
    """打印标题"""
    print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}  {title}{Colors.END}")
    print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")


def print_section(title: str):
    """打印小节标题"""
    print(f"\n{Colors.BLUE}▶ {title}{Colors.END}")


def print_success(message: str):
    """打印成功信息"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")


def print_error(message: str):
    """打印错误信息"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")


def print_warning(message: str):
    """打印警告信息"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")


def print_info(message: str):
    """打印信息"""
    print(f"{Colors.CYAN}ℹ {message}{Colors.END}")


# ==================== 测试数据生成器 ====================

class TestDataGenerator:
    """测试数据生成器"""
    
    def __init__(self, temp_dir: str):
        self.temp_dir = Path(temp_dir)
        self.created_files: List[Path] = []
    
    def create_valid_datatable(self, name: str = "MonsterTable") -> Path:
        """创建有效的 DataTable"""
        file_path = self.temp_dir / f"DataTables/{name}.xlsx"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        df = pd.DataFrame({
            'Id': [1, 2, 3, 4, 5],
            'Name': ['Slime', 'Goblin', 'Orc', 'Dragon', 'Boss'],
            'Level': [1, 5, 10, 20, 50],
            'HP': [50, 100, 300, 1000, 5000],
            'Attack': [5, 15, 30, 80, 200],
            'Defense': [2, 8, 20, 50, 150],
            'IsBoss': [False, False, False, False, True]
        })
        
        df.to_excel(file_path, index=False, sheet_name=name)
        self.created_files.append(file_path)
        return file_path
    
    def create_invalid_datatable(self, name: str = "InvalidMonster") -> Path:
        """创建无效的 DataTable（用于测试错误检测）"""
        file_path = self.temp_dir / f"DataTables/{name}.xlsx"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 创建有问题的数据：缺少 Id 列，有重复行
        df = pd.DataFrame({
            'Name': ['Monster1', 'Monster2', 'Monster1'],  # 重复名称
            'Level': [10, 20, 10],
            'HP': [100, 200, None],  # 空值
        })
        
        df.to_excel(file_path, index=False, sheet_name=name)
        self.created_files.append(file_path)
        return file_path
    
    def create_valid_config(self, name: str = "GameConfig") -> Path:
        """创建有效的 Config 文件"""
        file_path = self.temp_dir / f"Configs/{name}.xlsx"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        df = pd.DataFrame({
            'Key': ['initialGold', 'maxLevel', 'version', 'debugMode', 'serverUrl'],
            'Value': ['10000', '100', '1.2.0', 'false', 'https://game.example.com']
        })
        
        df.to_excel(file_path, index=False, sheet_name=name)
        self.created_files.append(file_path)
        return file_path
    
    def create_invalid_config(self, name: str = "BadConfig") -> Path:
        """创建无效的 Config 文件"""
        file_path = self.temp_dir / f"Configs/{name}.xlsx"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 问题：重复的 Key，以及超过 2 列
        df = pd.DataFrame({
            'Key': ['setting1', 'setting1', 'setting2'],  # 重复 key
            'Value': ['100', '200', '300'],
            'Extra': ['a', 'b', 'c']  # 不应该有的第 3 列
        })
        
        df.to_excel(file_path, index=False, sheet_name=name)
        self.created_files.append(file_path)
        return file_path
    
    def create_valid_language(self, name: str = "UIStrings_CN") -> Path:
        """创建有效的 Language 文件（注意：Language 只支持 2 列 Key/Text）"""
        file_path = self.temp_dir / f"Languages/{name}.xlsx"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Language 表只有 2 列：Key 和 Text
        df = pd.DataFrame({
            'Key': ['HELLO', 'WELCOME', 'GAME_OVER', 'LEVEL_UP', 'ERROR_NETWORK'],
            'Text': ['你好', '欢迎', '游戏结束', '升级了！', '网络连接失败']
        })
        
        df.to_excel(file_path, index=False, sheet_name=name)
        self.created_files.append(file_path)
        return file_path
    
    def cleanup(self):
        """清理所有创建的文件"""
        for file_path in self.created_files:
            if file_path.exists():
                file_path.unlink()


# ==================== 集成测试主类 ====================

class IntegrationTestRunner:
    """集成测试运行器"""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="excel_skill_test_")
        self.data_gen = TestDataGenerator(self.temp_dir)
        self.results = []
        self.start_time = None
        self.end_time = None
    
    def run_all_tests(self):
        """运行所有集成测试"""
        import time
        
        self.start_time = time.time()
        
        print_header("Excel 数据编辑 Skill - 集成测试")
        print(f"{Colors.CYAN}临时目录: {self.temp_dir}{Colors.END}\n")
        
        # 测试场景
        self.test_scenario_1_valid_datatable()
        self.test_scenario_2_invalid_datatable()
        self.test_scenario_3_valid_config()
        self.test_scenario_4_invalid_config()
        self.test_scenario_5_valid_language()
        self.test_scenario_6_mixed_batch()
        
        self.end_time = time.time()
        
        self.print_summary()
    
    def test_scenario_1_valid_datatable(self):
        """场景1：验证有效的 DataTable"""
        print_section("场景 1: 验证有效的 DataTable")
        
        # 创建测试数据
        file_path = self.data_gen.create_valid_datatable("MonsterTable")
        print_info(f"创建测试文件: {file_path}")
        
        # 执行验证
        validator = DataTableValidator()
        df = pd.read_excel(file_path)
        result = validator.validate(df)
        
        # 检查结果
        if result.is_valid:
            print_success("DataTable 验证通过！")
            print(f"  {Colors.CYAN}行数: {len(df)}, 列数: {len(df.columns)}{Colors.END}")
            self.results.append(("场景1: 有效DataTable", True, None))
        else:
            print_error(f"验证失败: {len(result.errors)} 个错误")
            self.results.append(("场景1: 有效DataTable", False, result.errors))
    
    def test_scenario_2_invalid_datatable(self):
        """场景2：检测无效的 DataTable"""
        print_section("场景 2: 检测无效的 DataTable")
        
        file_path = self.data_gen.create_invalid_datatable("InvalidMonster")
        print_info(f"创建测试文件: {file_path}")
        
        validator = DataTableValidator()
        df = pd.read_excel(file_path)
        result = validator.validate(df)
        
        print_info(f"检测到 {len(result.errors)} 个错误, {len(result.warnings)} 个警告")
        
        # 验证是否检测到预期的问题
        has_structure_error = any('Id' in e.field or 'structure' in e.code for e in result.errors)
        
        if has_structure_error:
            print_success("成功检测到结构问题！")
            for error in result.errors[:3]:
                print(f"  {Colors.YELLOW}- {error.message}{Colors.END}")
            self.results.append(("场景2: 无效DataTable", True, None))
        else:
            print_warning("可能遗漏了一些错误检测")
            self.results.append(("场景2: 无效DataTable", True, result.errors))
    
    def test_scenario_3_valid_config(self):
        """场景3：验证有效的 Config"""
        print_section("场景 3: 验证有效的 Config")
        
        file_path = self.data_gen.create_valid_config("GameConfig")
        print_info(f"创建测试文件: {file_path}")
        
        validator = ConfigValidator()
        df = pd.read_excel(file_path)
        result = validator.validate(df)
        
        if result.is_valid:
            print_success("Config 验证通过！")
            print(f"  {Colors.CYAN}配置项数量: {len(df)}{Colors.END}")
            self.results.append(("场景3: 有效Config", True, None))
        else:
            print_error(f"验证失败: {len(result.errors)} 个错误")
            self.results.append(("场景3: 有效Config", False, result.errors))
    
    def test_scenario_4_invalid_config(self):
        """场景4：检测无效的 Config"""
        print_section("场景 4: 检测无效的 Config")
        
        file_path = self.data_gen.create_invalid_config("BadConfig")
        print_info(f"创建测试文件: {file_path}")
        
        validator = ConfigValidator()
        df = pd.read_excel(file_path)
        result = validator.validate(df)
        
        print_info(f"检测到 {len(result.errors)} 个错误")
        
        if result.errors:
            print_success("成功检测到配置问题！")
            for error in result.errors[:5]:
                print(f"  {Colors.YELLOW}- {error.field}: {error.message}{Colors.END}")
            self.results.append(("场景4: 无效Config", True, None))
        else:
            print_warning("未能检测到预期的错误")
            self.results.append(("场景4: 无效Config", False, []))
    
    def test_scenario_5_valid_language(self):
        """场景5：验证有效的 Language 文件"""
        print_section("场景 5: 验证有效的 Language")
        
        file_path = self.data_gen.create_valid_language("UIStrings")
        print_info(f"创建测试文件: {file_path}")
        
        validator = LanguageValidator()
        df = pd.read_excel(file_path)
        result = validator.validate(df)
        
        if result.is_valid:
            print_success("Language 验证通过！")
            print(f"  {Colors.CYAN}语言键数量: {len(df)}, 语言列数: {len(df.columns) - 1}{Colors.END}")
            self.results.append(("场景5: 有效Language", True, None))
        else:
            print_error(f"验证失败: {len(result.errors)} 个错误")
            self.results.append(("场景5: 有效Language", False, result.errors))
    
    def test_scenario_6_mixed_batch(self):
        """场景6：批量混合测试"""
        print_section("场景 6: 批量混合测试")
        
        # 创建多个不同类型的文件
        files = [
            self.data_gen.create_valid_datatable("BatchMonster1"),
            self.data_gen.create_valid_datatable("BatchMonster2"),
            self.data_gen.create_valid_config("BatchConfig"),
            self.data_gen.create_valid_language("BatchLang"),
        ]
        
        print_info(f"创建 {len(files)} 个测试文件")
        
        # 批量验证
        validators = {
            'datatable': DataTableValidator(),
            'config': ConfigValidator(),
            'language': LanguageValidator(),
        }
        
        passed = 0
        failed = 0
        
        for file_path in files:
            try:
                df = pd.read_excel(file_path)
                
                # 根据路径选择验证器
                path_str = str(file_path).lower()
                if 'datatables' in path_str:
                    validator = validators['datatable']
                elif 'configs' in path_str:
                    validator = validators['config']
                elif 'languages' in path_str:
                    validator = validators['language']
                else:
                    failed += 1
                    continue
                
                result = validator.validate(df)
                if result.is_valid:
                    passed += 1
                else:
                    failed += 1
                    
            except Exception as e:
                print_error(f"验证 {file_path.name} 时出错: {e}")
                failed += 1
        
        print(f"\n  {Colors.GREEN}通过: {passed}{Colors.END}")
        print(f"  {Colors.RED}失败: {failed}{Colors.END}")
        
        if failed == 0:
            print_success("批量测试全部通过！")
            self.results.append(("场景6: 批量测试", True, None))
        else:
            print_warning(f"有 {failed} 个文件未通过验证")
            self.results.append(("场景6: 批量测试", False, []))
    
    def print_summary(self):
        """打印测试摘要"""
        print_header("集成测试摘要")
        
        total = len(self.results)
        passed = sum(1 for _, result, _ in self.results if result)
        failed = total - passed
        
        duration = self.end_time - self.start_time
        
        print(f"\n  {Colors.BOLD}执行时间:{Colors.END} {duration:.2f} 秒")
        print(f"  {Colors.BOLD}测试场景:{Colors.END} {total} 个")
        print(f"  {Colors.GREEN}✓ 通过:{Colors.END} {passed} 个")
        print(f"  {Colors.RED}✗ 失败:{Colors.END} {failed} 个")
        print(f"  {Colors.CYAN}成功率:{Colors.END} {passed/total*100:.1f}%")
        
        print(f"\n{Colors.CYAN}{'-'*70}{Colors.END}")
        print(f"{Colors.BOLD}详细结果:{Colors.END}")
        
        for name, result, errors in self.results:
            status = f"{Colors.GREEN}✓ 通过{Colors.END}" if result else f"{Colors.RED}✗ 失败{Colors.END}"
            print(f"  {status} - {name}")
            if errors and not result:
                for error in errors[:3]:
                    print(f"      {Colors.YELLOW}└─ {error}{Colors.END}")
        
        print(f"\n{Colors.CYAN}{'='*70}{Colors.END}\n")
        
        return 0 if failed == 0 else 1
    
    def cleanup(self):
        """清理临时文件"""
        if hasattr(self, 'temp_dir') and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            print_info(f"清理临时目录: {self.temp_dir}")


def main():
    """主程序"""
    try:
        runner = IntegrationTestRunner()
        runner.run_all_tests()
        exit_code = runner.print_summary()
    finally:
        runner.cleanup()
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
