import React from 'react';

import styles from './index.module.scss';

const Component = () => {
  return (
    <div className={styles.container41}>
      <div className={styles.asideSideNavBar}>
        <div className={styles.container4}>
          <div className={styles.background}>
            <img src="../image/mn0jpz5v-ruvzrlh.svg" className={styles.container} />
          </div>
          <div className={styles.container3}>
            <p className={styles.text}>本体结构</p>
            <div className={styles.container2}>
              <p className={styles.text2}>V2.4.0</p>
            </div>
          </div>
        </div>
        <div className={styles.container13}>
          <p className={styles.text3}>核心模型</p>
          <div className={styles.backgroundVerticalBo}>
            <img
              src="../image/mn0jpz5v-4loak0t.svg"
              className={styles.container5}
            />
            <p className={styles.text4}>对象类型</p>
            <div className={styles.margin}>
              <img
                src="../image/mn0jpz5v-fs5jv5l.svg"
                className={styles.container6}
              />
            </div>
          </div>
          <div className={styles.treeSubItems}>
            <div className={styles.overlay}>
              <p className={styles.text4}>航班记录</p>
            </div>
            <p className={styles.text5}>机场设施</p>
            <p className={styles.text5}>乘客名单</p>
          </div>
          <div className={styles.container8}>
            <img
              src="../image/mn0jpz5v-dvgd0a8.svg"
              className={styles.container7}
            />
            <p className={styles.text6}>链接类型</p>
          </div>
          <div className={styles.container10}>
            <img
              src="../image/mn0jpz5v-in0a3v5.svg"
              className={styles.container9}
            />
            <p className={styles.text7}>操作</p>
          </div>
          <div className={styles.container12}>
            <img
              src="../image/mn0jpz5v-1bx9yt0.svg"
              className={styles.container11}
            />
            <p className={styles.text7}>共享</p>
          </div>
        </div>
        <div className={styles.horizontalBorder}>
          <div className={styles.container15}>
            <img
              src="../image/mn0jpz5v-5qm25hw.svg"
              className={styles.container14}
            />
            <p className={styles.text7}>预览</p>
          </div>
          <div className={styles.container17}>
            <img
              src="../image/mn0jpz5v-tdjslbv.svg"
              className={styles.container16}
            />
            <p className={styles.text6}>更改日志</p>
          </div>
        </div>
      </div>
      <div className={styles.mainWorkspaceArea}>
        <div className={styles.breadcrumbs}>
          <p className={styles.text8}>本体</p>
          <img src="../image/mn0jpz5u-nval916.svg" className={styles.container18} />
          <p className={styles.text9}>对象类型</p>
          <img src="../image/mn0jpz5u-nval916.svg" className={styles.container18} />
          <p className={styles.text10}>航班记录 (Flight Record)</p>
        </div>
        <div className={styles.contentContainer}>
          <div className={styles.sectionBasicInfoCard}>
            <div className={styles.heading2}>
              <img
                src="../image/mn0jpz5u-jwv1uq8.svg"
                className={styles.container19}
              />
              <p className={styles.text11}>基本信息</p>
            </div>
            <div className={styles.container26}>
              <div className={styles.container21}>
                <p className={styles.text12}>显示名称</p>
                <div className={styles.container20}>
                  <p className={styles.text13}>航班记录</p>
                </div>
              </div>
              <div className={styles.container23}>
                <p className={styles.text14}>唯一标识符 (API Name)</p>
                <div className={styles.input}>
                  <p className={styles.flightRecord}>flight_record</p>
                  <img
                    src="../image/mn0jpz5u-gnav331.svg"
                    className={styles.container22}
                  />
                </div>
              </div>
              <div className={styles.container25}>
                <p className={styles.text15}>描述</p>
                <div className={styles.container24}>
                  <p className={styles.text16}>输入对象的描述信息...</p>
                </div>
              </div>
            </div>
          </div>
          <div className={styles.propertiesSection}>
            <div className={styles.horizontalBorder2}>
              <div className={styles.heading22}>
                <img
                  src="../image/mn0jpz5u-yk4c4ad.svg"
                  className={styles.container27}
                />
                <p className={styles.text11}>属性列表</p>
              </div>
              <div className={styles.button}>
                <img
                  src="../image/mn0jpz5u-oo0cl4g.svg"
                  className={styles.container28}
                />
                <p className={styles.text17}>添加新属性</p>
              </div>
            </div>
            <div className={styles.table}>
              <div className={styles.headerRow}>
                <div className={styles.cell}>
                  <p className={styles.text18}>字段名</p>
                </div>
                <div className={styles.cell2}>
                  <p className={styles.text18}>显示名</p>
                </div>
                <div className={styles.cell3}>
                  <p className={styles.text19}>数据类型</p>
                </div>
                <div className={styles.cell4}>
                  <p className={styles.text20}>主键</p>
                </div>
                <div className={styles.cell5}>
                  <p className={styles.text20}>索引</p>
                </div>
                <div className={styles.cell4}>
                  <p className={styles.text20}>操作</p>
                </div>
              </div>
              <div className={styles.body}>
                <div className={styles.row}>
                  <div className={styles.data}>
                    <p className={styles.text21}>flight_id</p>
                  </div>
                  <div className={styles.data2}>
                    <p className={styles.text22}>航班号</p>
                  </div>
                  <div className={styles.data3}>
                    <div className={styles.background2}>
                      <p className={styles.text23}>String</p>
                    </div>
                  </div>
                  <img
                    src="../image/mn0jpz5v-ur29lcq.svg"
                    className={styles.data4}
                  />
                  <div className={styles.data5}>
                    <p className={styles.text24}>唯一索引</p>
                  </div>
                  <img
                    src="../image/mn0jpz5v-867m4n7.svg"
                    className={styles.data4}
                  />
                </div>
                <div className={styles.row2}>
                  <div className={styles.data6}>
                    <p className={styles.text25}>departure_time</p>
                  </div>
                  <div className={styles.data7}>
                    <p className={styles.text26}>出发时间</p>
                  </div>
                  <div className={styles.data8}>
                    <div className={styles.background3}>
                      <p className={styles.text27}>Timestamp</p>
                    </div>
                  </div>
                  <img
                    src="../image/mn0jpz5v-9bot8pw.svg"
                    className={styles.data4}
                  />
                  <div className={styles.data5}>
                    <p className={styles.text24}>常规索引</p>
                  </div>
                  <img
                    src="../image/mn0jpz5v-867m4n7.svg"
                    className={styles.data4}
                  />
                </div>
                <div className={styles.row3}>
                  <div className={styles.data9}>
                    <p className={styles.text28}>passenger_count</p>
                  </div>
                  <div className={styles.data7}>
                    <p className={styles.text26}>乘客人数</p>
                  </div>
                  <div className={styles.data10}>
                    <div className={styles.background4}>
                      <p className={styles.text29}>Integer</p>
                    </div>
                  </div>
                  <img
                    src="../image/mn0jpz5v-9bot8pw.svg"
                    className={styles.data4}
                  />
                  <div className={styles.data11}>
                    <p className={styles.text30}>-</p>
                  </div>
                  <img
                    src="../image/mn0jpz5v-867m4n7.svg"
                    className={styles.data4}
                  />
                </div>
                <div className={styles.row4}>
                  <div className={styles.data12}>
                    <p className={styles.text31}>fuel_consumption</p>
                  </div>
                  <div className={styles.data13}>
                    <p className={styles.text26}>燃料消耗</p>
                  </div>
                  <div className={styles.data14}>
                    <div className={styles.background5}>
                      <p className={styles.text32}>Double</p>
                    </div>
                  </div>
                  <img
                    src="../image/mn0jpz5v-y553cij.svg"
                    className={styles.data15}
                  />
                  <div className={styles.data11}>
                    <p className={styles.text30}>-</p>
                  </div>
                  <img
                    src="../image/mn0jpz5v-wkik1if.svg"
                    className={styles.data15}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className={styles.container40}>
        <div className={styles.previewSection}>
          <div className={styles.container30}>
            <p className={styles.text33}>数据预览 (Mock)</p>
            <img
              src="../image/mn0jpz5v-spmlad6.svg"
              className={styles.container29}
            />
          </div>
          <div className={styles.backgroundShadow}>
            <p className={styles.a}>&#123;</p>
            <div className={styles.container31}>
              <p className={styles.aFlightIdAa12344}>
                <span className={styles.aFlightIdAa1234}>"flight_id"</span>
                <span className={styles.aFlightIdAa12342}>:&nbsp;</span>
                <span className={styles.aFlightIdAa12343}>"AA1234"</span>
                <span className={styles.aFlightIdAa12342}>,</span>
              </p>
            </div>
            <div className={styles.container31}>
              <p className={styles.aFlightIdAa12344}>
                <span className={styles.aFlightIdAa1234}>"departure"</span>
                <span className={styles.aFlightIdAa12342}>:&nbsp;</span>
                <span className={styles.aFlightIdAa12343}>
                  "2023-10-27T10:00:00Z"
                </span>
                <span className={styles.aFlightIdAa12342}>,</span>
              </p>
            </div>
            <div className={styles.container32}>
              <p className={styles.aPassengers1862}>
                <span className={styles.aFlightIdAa1234}>"passengers"</span>
                <span className={styles.aFlightIdAa12342}>:&nbsp;</span>
                <span className={styles.aPassengers186}>186</span>
                <span className={styles.aFlightIdAa12342}>,</span>
              </p>
            </div>
            <div className={styles.container32}>
              <p className={styles.aPassengers1862}>
                <span className={styles.aFlightIdAa1234}>"active"</span>
                <span className={styles.aFlightIdAa12342}>:&nbsp;</span>
                <span className={styles.aPassengers186}>true</span>
              </p>
            </div>
            <p className={styles.a2}>&#125;</p>
          </div>
        </div>
        <div className={styles.historySection}>
          <p className={styles.text34}>更改历史</p>
          <div className={styles.container39}>
            <div className={styles.timelineLine} />
            <div className={styles.container35}>
              <div className={styles.margin2}>
                <div className={styles.backgroundBorderShad} />
              </div>
              <div className={styles.container34}>
                <p className={styles.text35}>更新属性 `passenger_count`</p>
                <div className={styles.container33}>
                  <p className={styles.text36}>张经理 · 10分钟前</p>
                </div>
              </div>
            </div>
            <div className={styles.container38}>
              <div className={styles.margin3}>
                <div className={styles.backgroundBorderShad2} />
              </div>
              <div className={styles.container37}>
                <p className={styles.text37}>创建对象 `flight_record`</p>
                <div className={styles.container36}>
                  <p className={styles.text38}>李技术 · 2小时前</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className={styles.publishControls}>
          <div className={styles.button2}>
            <p className={styles.text39}>保存并发布更改</p>
          </div>
          <div className={styles.button3}>
            <p className={styles.text40}>放弃草稿</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Component;
