import React from 'react';

import styles from './index.module.scss';

const Component = () => {
  return (
    <div className={styles.container44}>
      <div className={styles.leftColumnConfigurat}>
        <div className={styles.container}>
          <div className={styles.nav}>
            <p className={styles.text}>本体列表</p>
            <p className={styles.text2}>/</p>
            <p className={styles.text}>订单管理</p>
            <p className={styles.text2}>/</p>
            <p className={styles.text3}>动作配置</p>
          </div>
          <p className={styles.text4}>动作配置 : 订单自动同步</p>
        </div>
        <div className={styles.section1BasicInfo}>
          <div className={styles.heading3}>
            <p className={styles.text5}>基本信息</p>
          </div>
          <div className={styles.container8}>
            <div className={styles.autoWrapper}>
              <div className={styles.container3}>
                <p className={styles.text}>动作名称</p>
                <div className={styles.container2}>
                  <p className={styles.text6}>订单自动同步</p>
                </div>
              </div>
              <div className={styles.container5}>
                <p className={styles.text7}>API 名称</p>
                <div className={styles.container4}>
                  <p className={styles.orderAutoSync}>order_auto_sync</p>
                </div>
              </div>
            </div>
            <div className={styles.container7}>
              <p className={styles.text8}>描述</p>
              <div className={styles.container6}>
                <p className={styles.text6}>
                  当订单状态更新为已完成时，自动触发后台API将数据推送到ERP系统。
                </p>
              </div>
            </div>
          </div>
        </div>
        <div className={styles.section2TriggerSetti}>
          <div className={styles.heading32}>
            <p className={styles.text9}>触发器设置</p>
          </div>
          <div className={styles.container14}>
            <div className={styles.container10}>
              <p className={styles.text}>事件类型</p>
              <div className={styles.imageFill}>
                <img src="../image/mn0l640c-fwszll6.svg" className={styles.sVg} />
                <div className={styles.container9}>
                  <p className={styles.text10}>对象已更新 (Object Updated)</p>
                </div>
              </div>
            </div>
            <div className={styles.container12}>
              <p className={styles.text11}>源对象</p>
              <div className={styles.background}>
                <img
                  src="../image/mn0l640c-25srlu6.svg"
                  className={styles.margin}
                />
                <div className={styles.container11}>
                  <p className={styles.text12}>订单 (Order)</p>
                </div>
              </div>
            </div>
            <div className={styles.container13}>
              <p className={styles.text}>触发条件</p>
              <div className={styles.background2}>
                <p className={styles.text13}>Status</p>
                <p className={styles.text14}>==</p>
                <p className={styles.text15}>'Completed'</p>
              </div>
            </div>
          </div>
        </div>
        <div className={styles.section3ExecutionLog}>
          <div className={styles.heading3}>
            <p className={styles.text5}>执行逻辑</p>
          </div>
          <div className={styles.container23}>
            <div className={styles.container21}>
              <div className={styles.container18}>
                <p className={styles.text}>逻辑类型</p>
                <div className={styles.container17}>
                  <div className={styles.button}>
                    <img
                      src="../image/mn0l640c-kn3hmsv.svg"
                      className={styles.container15}
                    />
                    <p className={styles.text16}>API 调用</p>
                  </div>
                  <div className={styles.button2}>
                    <img
                      src="../image/mn0l640c-w6339ng.svg"
                      className={styles.container16}
                    />
                    <p className={styles.text17}>脚本执行</p>
                  </div>
                </div>
              </div>
              <div className={styles.container20}>
                <p className={styles.text}>目标系统</p>
                <div className={styles.background3}>
                  <img
                    src="../image/mn0l640c-jp49joq.svg"
                    className={styles.margin2}
                  />
                  <div className={styles.container19}>
                    <p className={styles.text18}>企业资源计划 (ERP)</p>
                  </div>
                </div>
              </div>
            </div>
            <div className={styles.container22}>
              <p className={styles.text19}>参数映射 (Parameter Mapping)</p>
              <div className={styles.table}>
                <div className={styles.row}>
                  <div className={styles.cell}>
                    <p className={styles.text20}>源字段 (Source)</p>
                  </div>
                  <div className={styles.cell2}>
                    <p className={styles.text21}>映射</p>
                  </div>
                  <div className={styles.cell3}>
                    <p className={styles.text22}>目标字段 (Target)</p>
                  </div>
                </div>
                <div className={styles.body}>
                  <div className={styles.row2}>
                    <div className={styles.data}>
                      <p className={styles.text23}>id</p>
                    </div>
                    <img
                      src="../image/mn0l640c-ifv8fmo.svg"
                      className={styles.data2}
                    />
                    <div className={styles.data3}>
                      <p className={styles.text24}>ERP_ID</p>
                    </div>
                  </div>
                  <div className={styles.row3}>
                    <div className={styles.data4}>
                      <p className={styles.text25}>total_amount</p>
                    </div>
                    <img
                      src="../image/mn0l640c-ifv8fmo.svg"
                      className={styles.data2}
                    />
                    <div className={styles.data5}>
                      <p className={styles.text26}>TRANSACTION_VAL</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className={styles.section4InputsOutput}>
          <div className={styles.container25}>
            <div className={styles.heading33}>
              <p className={styles.text27}>输入/输出</p>
            </div>
            <div className={styles.button3}>
              <img
                src="../image/mn0l640c-oyg74je.svg"
                className={styles.container24}
              />
              <p className={styles.text28}>添加变量</p>
            </div>
          </div>
          <div className={styles.table2}>
            <div className={styles.headerRow}>
              <div className={styles.cell4}>
                <p className={styles.text29}>变量名称</p>
              </div>
              <div className={styles.cell5}>
                <p className={styles.text29}>数据类型</p>
              </div>
              <div className={styles.cell6}>
                <p className={styles.text30}>默认值</p>
              </div>
              <div className={styles.cell7}>
                <p className={styles.text31}>操作</p>
              </div>
            </div>
            <div className={styles.body2}>
              <div className={styles.row4}>
                <div className={styles.data6}>
                  <p className={styles.text32}>request_id</p>
                </div>
                <div className={styles.data7}>
                  <div className={styles.background4}>
                    <p className={styles.text33}>String</p>
                  </div>
                </div>
                <div className={styles.data8}>
                  <p className={styles.text34}>None</p>
                </div>
                <div className={styles.data9}>
                  <img
                    src="../image/mn0l640c-wzq4onp.svg"
                    className={styles.button4}
                  />
                </div>
              </div>
              <div className={styles.row5}>
                <div className={styles.data10}>
                  <p className={styles.text35}>retry_count</p>
                </div>
                <div className={styles.data11}>
                  <div className={styles.background5}>
                    <p className={styles.text36}>Number</p>
                  </div>
                </div>
                <div className={styles.data12}>
                  <p className={styles.text37}>3</p>
                </div>
                <div className={styles.data13}>
                  <img
                    src="../image/mn0l640c-wzq4onp.svg"
                    className={styles.button4}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className={styles.rightColumnSummaryAn}>
        <div className={styles.actionSummaryCard}>
          <div className={styles.container26}>
            <p className={styles.text38}>动作摘要</p>
            <div className={styles.background7}>
              <div className={styles.background6} />
              <p className={styles.text39}>已激活</p>
            </div>
          </div>
          <div className={styles.visualFlowDiagram}>
            <div className={styles.verticalDivider} />
            <div className={styles.container30}>
              <div className={styles.backgroundBorderShad}>
                <img
                  src="../image/mn0l640c-7qmiig4.svg"
                  className={styles.container27}
                />
              </div>
              <div className={styles.container29}>
                <div className={styles.container28}>
                  <p className={styles.text40}>触发源</p>
                </div>
                <p className={styles.text41}>订单更新事件</p>
              </div>
            </div>
            <div className={styles.container34}>
              <div className={styles.backgroundShadow}>
                <img
                  src="../image/mn0l640c-8mwoxy3.svg"
                  className={styles.container31}
                />
              </div>
              <div className={styles.container33}>
                <div className={styles.container32}>
                  <p className={styles.text42}>执行逻辑</p>
                </div>
                <p className={styles.text43}>API: POST /sync/erp</p>
              </div>
            </div>
            <div className={styles.container37}>
              <div className={styles.backgroundBorderShad2}>
                <img
                  src="../image/mn0l640c-05iso1z.svg"
                  className={styles.container35}
                />
              </div>
              <div className={styles.container36}>
                <div className={styles.container32}>
                  <p className={styles.text42}>输出结果</p>
                </div>
                <p className={styles.text44}>ERP 响应回执</p>
              </div>
            </div>
          </div>
          <div className={styles.recentExecutions}>
            <div className={styles.container38}>
              <p className={styles.text45}>最近执行</p>
              <p className={styles.text46}>查看全部</p>
            </div>
            <div className={styles.container41}>
              <div className={styles.backgroundBorder}>
                <div className={styles.container39}>
                  <div className={styles.background8} />
                  <p className={styles.text47}>#ORD-9021</p>
                </div>
                <p className={styles.text48}>2 分钟前</p>
              </div>
              <div className={styles.backgroundBorder2}>
                <div className={styles.container39}>
                  <div className={styles.background8} />
                  <p className={styles.text47}>#ORD-8944</p>
                </div>
                <p className={styles.text49}>14 分钟前</p>
              </div>
              <div className={styles.backgroundBorder3}>
                <div className={styles.container40}>
                  <div className={styles.background9} />
                  <p className={styles.text47}>#ORD-8812</p>
                </div>
                <p className={styles.text50}>1 小时前</p>
              </div>
            </div>
          </div>
          <div className={styles.healthMonitoringImag}>
            <div className={styles.background10}>
              <div className={styles.container42}>
                <p className={styles.text51}>执行成功率</p>
                <p className={styles.a984}>98.4%</p>
              </div>
              <div className={styles.gradient} />
              <div className={styles.container43}>
                <div className={styles.overlay} />
                <div className={styles.overlay2} />
                <div className={styles.overlay3} />
                <div className={styles.overlay4} />
                <div className={styles.overlay5} />
                <div className={styles.overlay6} />
                <div className={styles.overlay7} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Component;
