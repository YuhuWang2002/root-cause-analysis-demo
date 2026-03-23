import React from 'react';

import styles from './index.module.scss';

const Component = () => {
  return (
    <div className={styles.container28}>
      <div className={styles.mainWorkspaceCanvas}>
        <div className={styles.workflowCanvasArea}>
          <div className={styles.sVg}>
            <div className={styles.dataSourcesLeft}>
              <div className={styles.backgroundVerticalBo}>
                <img
                  src="../image/mn2vdxcv-a2znr7y.svg"
                  className={styles.container}
                />
                <p className={styles.text}>
                  采购
                  <br />
                  (Procurement)
                </p>
              </div>
              <div className={styles.backgroundVerticalBo2}>
                <img
                  src="../image/mn2vdxcv-rv5shlt.svg"
                  className={styles.container2}
                />
                <div className={styles.container3}>
                  <p className={styles.text2}>
                    仓库
                    <br />
                    (Warehouse)
                  </p>
                </div>
              </div>
              <div className={styles.backgroundVerticalBo3}>
                <img
                  src="../image/mn2vdxcv-3c6hvbk.svg"
                  className={styles.container4}
                />
                <div className={styles.container5}>
                  <p className={styles.text3}>
                    生产
                    <br />
                    (Production)
                  </p>
                </div>
              </div>
              <div className={styles.backgroundVerticalBo4}>
                <img
                  src="../image/mn2vdxcv-togrn8b.svg"
                  className={styles.container4}
                />
                <p className={styles.text4}>销售 (Sales)</p>
              </div>
            </div>
            <div className={styles.processingNodesMiddl}>
              <div className={styles.backgroundBorderShad}>
                <div className={styles.background}>
                  <img
                    src="../image/mn2vdxcv-nmr92dc.svg"
                    className={styles.container6}
                  />
                </div>
                <p className={styles.text5}>关联 (JOIN)</p>
              </div>
              <div className={styles.margin}>
                <div className={styles.backgroundBorderShad2}>
                  <div className={styles.background2}>
                    <img
                      src="../image/mn2vdxcv-1cgx1lh.svg"
                      className={styles.container7}
                    />
                  </div>
                  <p className={styles.text6}>数据清洗 (CLEAN)</p>
                </div>
              </div>
            </div>
            <div className={styles.aggregateNode}>
              <div className={styles.overlayShadow}>
                <div className={styles.background3}>
                  <img
                    src="../image/mn2vdxcv-k0oh96w.svg"
                    className={styles.container8}
                  />
                </div>
                <div className={styles.paragraph}>
                  <p className={styles.text7}>聚合</p>
                  <p className={styles.aAggregate}>(AGGREGATE)</p>
                </div>
              </div>
            </div>
          </div>
          <div className={styles.terminalNodeFinalOut}>
            <div className={styles.overlayShadow2}>
              <img
                src="../image/mn2vdxcv-lcvih81.svg"
                className={styles.container9}
              />
              <div className={styles.container11}>
                <div className={styles.container10}>
                  <p className={styles.text8}>最终输出</p>
                </div>
                <p className={styles.text9}>
                  企业主数据集
                  <br />
                  (Enterprise Master
                  <br />
                  Dataset)
                </p>
              </div>
            </div>
          </div>
        </div>
        <div className={styles.sectionBottomDataPre}>
          <div className={styles.background4}>
            <div className={styles.container13}>
              <img
                src="../image/mn2vdxcv-g6ouj2i.svg"
                className={styles.container12}
              />
              <p className={styles.text10}>数据预览 (实时抽取)</p>
            </div>
            <div className={styles.container16}>
              <div className={styles.button}>
                <img
                  src="../image/mn2vdxcv-0v5hx7m.svg"
                  className={styles.container14}
                />
              </div>
              <div className={styles.button2}>
                <img
                  src="../image/mn2vdxcv-x6kj8dx.svg"
                  className={styles.container15}
                />
              </div>
            </div>
          </div>
          <div className={styles.table}>
            <div className={styles.row}>
              <div className={styles.cell}>
                <p className={styles.text11}>TRANS_ID</p>
              </div>
              <div className={styles.cell2}>
                <p className={styles.text12}>ENTITY_SOURCE</p>
              </div>
              <div className={styles.cell3}>
                <p className={styles.text13}>PRODUCT_GROUP</p>
              </div>
              <div className={styles.cell4}>
                <p className={styles.text14}>QUANTITY</p>
              </div>
              <div className={styles.cell5}>
                <p className={styles.text15}>VALUE_USD</p>
              </div>
            </div>
            <div className={styles.body}>
              <div className={styles.row2}>
                <div className={styles.data}>
                  <p className={styles.text16}>TXN-001293</p>
                </div>
                <div className={styles.data2}>
                  <p className={styles.text17}>PROCUREMENT</p>
                </div>
                <div className={styles.data3}>
                  <p className={styles.text18}>RAW_METAL</p>
                </div>
                <div className={styles.data4}>
                  <p className={styles.text19}>1,240.00</p>
                </div>
                <div className={styles.data5}>
                  <p className={styles.text20}>$14,500.00</p>
                </div>
              </div>
              <div className={styles.row3}>
                <div className={styles.data6}>
                  <p className={styles.text16}>TXN-001294</p>
                </div>
                <div className={styles.data7}>
                  <p className={styles.text21}>SALES</p>
                </div>
                <div className={styles.data8}>
                  <p className={styles.text22}>FINISHED_ENG</p>
                </div>
                <div className={styles.data9}>
                  <p className={styles.text23}>42.00</p>
                </div>
                <div className={styles.data10}>
                  <p className={styles.text20}>$89,200.00</p>
                </div>
              </div>
              <div className={styles.row4}>
                <div className={styles.data6}>
                  <p className={styles.text16}>TXN-001295</p>
                </div>
                <div className={styles.data11}>
                  <p className={styles.text18}>WAREHOUSE</p>
                </div>
                <div className={styles.data12}>
                  <p className={styles.text24}>SEMICON</p>
                </div>
                <div className={styles.data13}>
                  <p className={styles.text19}>8,000.00</p>
                </div>
                <div className={styles.data14}>
                  <p className={styles.text25}>$2,400.00</p>
                </div>
              </div>
              <div className={styles.row5}>
                <div className={styles.data6}>
                  <p className={styles.text16}>TXN-001296</p>
                </div>
                <div className={styles.data15}>
                  <p className={styles.text16}>PRODUCTION</p>
                </div>
                <div className={styles.data16}>
                  <p className={styles.text26}>GEAR_BOX</p>
                </div>
                <div className={styles.data17}>
                  <p className={styles.text27}>120.00</p>
                </div>
                <div className={styles.data10}>
                  <p className={styles.text20}>$15,800.00</p>
                </div>
              </div>
              <div className={styles.row6}>
                <div className={styles.data}>
                  <p className={styles.text16}>TXN-001297</p>
                </div>
                <div className={styles.data18}>
                  <p className={styles.text21}>SALES</p>
                </div>
                <div className={styles.data19}>
                  <p className={styles.text16}>TURBINE_S1</p>
                </div>
                <div className={styles.data20}>
                  <p className={styles.text28}>4.00</p>
                </div>
                <div className={styles.data21}>
                  <p className={styles.text29}>$340,000.00</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className={styles.asideSideNavigationB}>
        <div className={styles.horizontalBorder}>
          <div className={styles.container20}>
            <div className={styles.background5}>
              <img
                src="../image/mn2vdxcv-c2i3vs5.svg"
                className={styles.container17}
              />
            </div>
            <div className={styles.container19}>
              <div className={styles.container18}>
                <p className={styles.text30}>节点资源</p>
              </div>
              <p className={styles.text31}>工业级组件库</p>
            </div>
          </div>
          <div className={styles.buttonMargin}>
            <div className={styles.button3}>
              <p className={styles.text32}>新建节点</p>
            </div>
          </div>
        </div>
        <div className={styles.nav}>
          <div className={styles.link}>
            <img
              src="../image/mn2vdxcv-w6p9idx.svg"
              className={styles.container21}
            />
            <p className={styles.text33}>源数据集</p>
          </div>
          <div className={styles.link2}>
            <img
              src="../image/mn2vdxcv-qi9ztbu.svg"
              className={styles.container22}
            />
            <p className={styles.text34}>转换操作</p>
          </div>
          <div className={styles.link3}>
            <img
              src="../image/mn2vdxcv-j767in9.svg"
              className={styles.container23}
            />
            <p className={styles.text34}>输出结果</p>
          </div>
          <div className={styles.link4}>
            <img
              src="../image/mn2vdxcv-28utli6.svg"
              className={styles.container6}
            />
            <p className={styles.text35}>连接</p>
          </div>
          <div className={styles.link5}>
            <img
              src="../image/mn2vdxcv-e2xul4y.svg"
              className={styles.container24}
            />
            <p className={styles.text35}>过滤</p>
          </div>
          <div className={styles.link6}>
            <img
              src="../image/mn2vdxcv-eui68kp.svg"
              className={styles.container8}
            />
            <p className={styles.text35}>聚合</p>
          </div>
        </div>
      </div>
      <div className={styles.headerTopNavigationB}>
        <div className={styles.container25}>
          <p className={styles.text36}>数据管道建模器</p>
          <div className={styles.nav2}>
            <div className={styles.link7}>
              <p className={styles.text37}>项目预览</p>
            </div>
            <p className={styles.text38}>资源管理</p>
            <p className={styles.text39}>节点库</p>
            <p className={styles.text38}>历史版本</p>
          </div>
        </div>
        <div className={styles.container27}>
          <div className={styles.button4}>
            <img
              src="../image/mn2vdxcv-5mhqdpm.svg"
              className={styles.container26}
            />
          </div>
          <div className={styles.button5}>
            <img
              src="../image/mn2vdxcv-uuir3ma.svg"
              className={styles.container4}
            />
          </div>
          <div className={styles.button5}>
            <img
              src="../image/mn2vdxcv-g54m6z6.svg"
              className={styles.container4}
            />
          </div>
          <div className={styles.margin2}>
            <div className={styles.background6}>
              <img
                src="../image/mn2vdxd7-ciukll5.png"
                className={styles.userProfile}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Component;
