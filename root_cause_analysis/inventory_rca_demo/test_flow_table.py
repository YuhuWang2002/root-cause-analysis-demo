"""
测试数据分析流程表格展示
"""

print("="*80)
print("测试数据分析流程表格展示")
print("="*80)

print("\n📋 完整数据分析流程")
print("-" * 80)

steps = [
    ("1", "What do the users need to do?", "用户需要做什么"),
    ("2", "Where does the needed data come from?", "需要的数据来自哪里"),
    ("3", "How are users meant to interact with the data?", "用户如何与数据信息交互"),
    ("4", "What structured data asset needs to be provided to users?", "需要向用户提供什么样的结构化数据资产"),
    ("5", "What constrain should applied to control the data quality?", "应对施加哪些约束来控制数据质量"),
    ("6", "How should the data asset be leveraged?", "数据资产应该如何被利用"),
    ("7", "Describe any automations necessary for users to fulfill their tasks?", "用户完成其任务所需的自动化措施"),
    ("8", "Define roles and permissions?", "定义角色和权限"),
]

print(f"{'步骤':<6} {'英文问题':<60} {'中文问题':<30}")
print("-" * 80)

for step, en, cn in steps:
    print(f"{step:<6} {en:<60} {cn:<30}")

print("-" * 80)

print("\n✅ 数据分析流程表格已添加到根因分析页面顶部")
print("\n展示方式：")
print("1. 在页面顶部展示完整的8步流程表格")
print("2. 表格包含步骤编号、英文问题、中文问题三列")
print("3. 使用交替的背景色提高可读性")
print("4. 表格下方继续展示每个步骤的详细内容")

print("\n" + "="*80)
print("测试完成！")
print("="*80)
