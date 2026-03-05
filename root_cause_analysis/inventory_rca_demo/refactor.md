本库存根因分析demo应该做如下修改：

页面上只保留场景介绍，和根因分析页面，其他页面应该按流程展示在一起

根因分析页面
要能显示数据分析的一般流程：
 
  1、What do the users need to do ? / 回答 “用户需要做什么”  
  2、Where does the needed data come from ? / 回答 “需要的数据来自哪里”
  3、How are users meant to interact with the data ? / 回答“用户如何与数据信息交互”
  4、What structured data asset needs to be provided to users ？/回答 “需要向用户提供什么样的结构化数据资产”
  5、What constrain should applied to control the data quality ？/ 回答“应对施加哪些约束来控制数据质量”
  6、How should the data asset be leveraged？/ 回答 “数据资产应该如何被利用”
  7、Describe any automations necessary for users to fulfill their tasks？/ 回答“用户完成其任务所需的自动化措施”
  8、Define roles and permissions？/ 回答“定义角色和权限”

以上文案展现在web的顶部，用于给领导展示流程

下面按照步骤进行一步步展示：
  1、What do the users need to do ? / 回答 “用户需要做什么”  
   展示：用户需要进行根因分析，以确定库存高位问题的根本原因。
  2、Where does the needed data come from ? / 回答 “需要的数据来自哪里”
   展示：用户需要从数据库中获取库存数据和相关指标数据。本次演示使用的是模拟数据。
  3、How are users meant to interact with the data ? / 回答“用户如何与数据信息交互”
   展示：本次不演示
  4、What structured data asset needs to be provided to users ？/回答 “需要向用户提供什么样的结构化数据资产”
   展示：向用户展示本体图，可以用可视化工具展示。数据来源于调用root_cause_analysis/web/ontology_api.py 的api（api需要返回json格式的本体图数据，需要自己构造数据），展示方式参考root_cause_analysis/web/app.py 的Agent分析的，本体展示方式
   “产品A 使用 部件A
产品B 使用 部件A1”
  5、What constrain should applied to control the data quality ？/ 回答“应对施加哪些约束来控制数据质量”
   展示：rule： 部件A和部件A1是相同型号，可以通用
  6、How should the data asset be leveraged？/ 回答 “数据资产应该如何被利用”
   展示：用户需要利用数据资产进行根因分析，发现库存高位问题的根本原因。
   6.1 展示：发生了什么？
       这里展示当前的“数据探索”页面，用户可以查看库存数据和指标数据。
       展示：得到结论：当前库存数据显示，有一些商品的库存数量异常高，导致库存高位问题。

   6.2 展示：为什么会发生？
        展示：定义因果因素，展示因果图
        展示：当前的“根因分析”页面，用户可以查看库存高位问题的根本原因。
        展示：当前功能的 “智能解释”，这个智能解释偏向于解释根因是什么，这里需要LLM得出结论“产品B未使用部件A是导致部件A库存积压的、具有决定性影响的核心根因”
   6.3 展示：如何解决？
       展示： 调用LLM生成解决方案，这里LLM根据反事实分析给出的解决方案。

    注意：6.2，6.3 都要使用大模型能力，但6.2 是解释根因，6.3 是生成解决方案，所以要分别调用大模型能力，用不同的prompt。
 7、Describe any automations necessary for users to fulfill their tasks？/ 回答“用户完成其任务所需的自动化措施”
 展示：本次演示不展示
  8、Define roles and permissions？/ 回答“定义角色和权限”
   展示：本次演示不展示

注意看看当前生成的数据是否满足，不满需求的话，需要重新构造数据