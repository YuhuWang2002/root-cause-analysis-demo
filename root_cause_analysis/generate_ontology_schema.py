#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成本体Schema文件
"""

from web.ontology_manager import create_manufacturing_ontology, save_ontology_schema


def main():
    """生成ontology_schema.json文件"""
    print("开始生成本体Schema文件...")
    
    # 创建制造企业本体
    ontology_manager = create_manufacturing_ontology()
    
    # 保存为schema文件
    save_ontology_schema(ontology_manager, "ontology_schema.json")
    
    print("本体Schema文件生成完成！")


if __name__ == "__main__":
    main()
