import React from 'react';

import styles from './index.module.scss';

const Component = () => {
  return (
    <div className={styles.container32}>
      <div className={styles.sectionCenterColumnE}>
        <div className={styles.navBreadcrumbs}>
          <p className={styles.text}>Definitions</p>
          <img src="../image/mn0l12ex-gfj6ngc.svg" className={styles.container} />
          <p className={styles.text2}>Link Types</p>
          <img src="../image/mn0l12ex-gfj6ngc.svg" className={styles.container} />
          <p className={styles.text3}>Flight-Airport</p>
        </div>
        <div className={styles.container2}>
          <p className={styles.text4}>链接配置：航班 - 机场 (Flight to Airport)</p>
          <p className={styles.text5}>
            配置航班记录与其出发/到达机场之间的语义链接和字段映射。
          </p>
        </div>
        <div className={styles.bentoGridLayoutForCo}>
          <div className={styles.autoWrapper}>
            <div className={styles.basicInfoCard}>
              <div className={styles.container4}>
                <div className={styles.heading3}>
                  <img
                    src="../image/mn0l12ex-xd77ubn.svg"
                    className={styles.container3}
                  />
                  <p className={styles.text6}>基本信息</p>
                </div>
                <div className={styles.overlay}>
                  <p className={styles.text7}>ACTIVE</p>
                </div>
              </div>
              <div className={styles.container9}>
                <div className={styles.container6}>
                  <p className={styles.text8}>显示名称</p>
                  <div className={styles.container5}>
                    <p className={styles.text9}>起飞机场</p>
                  </div>
                </div>
                <div className={styles.container8}>
                  <p className={styles.text10}>API 名称</p>
                  <div className={styles.input}>
                    <p className={styles.flightDepartureAirpo}>
                      flight_departure_airport
                    </p>
                    <img
                      src="../image/mn0l12ex-i43lf77.svg"
                      className={styles.container7}
                    />
                  </div>
                </div>
              </div>
            </div>
            <div className={styles.cardinalityCard}>
              <div className={styles.heading32}>
                <img
                  src="../image/mn0l12ex-lgp9dm1.svg"
                  className={styles.container10}
                />
                <p className={styles.text6}>关系配置</p>
              </div>
              <div className={styles.label}>
                <p className={styles.text11}>基数配置 (Cardinality)</p>
              </div>
              <div className={styles.container11}>
                <div className={styles.button}>
                  <p className={styles.text12}>1 : N</p>
                  <p className={styles.text13}>一对多</p>
                </div>
                <div className={styles.button2}>
                  <p className={styles.text14}>N : N</p>
                  <p className={styles.text15}>多对多</p>
                </div>
              </div>
              <div className={styles.container12}>
                <p className={styles.text16}>
                  一个机场可关联多个航班，一个
                  <br />
                  航班仅对应一个出发机场。
                </p>
              </div>
            </div>
          </div>
          <div className={styles.mappingTableCard}>
            <div className={styles.container14}>
              <div className={styles.heading33}>
                <img
                  src="../image/mn0l12ex-26ttj7m.svg"
                  className={styles.container13}
                />
                <p className={styles.text17}>字段映射表 (Field Mapping)</p>
              </div>
              <p className={styles.text18}>添加映射项</p>
            </div>
            <div className={styles.table}>
              <div className={styles.row}>
                <div className={styles.cell}>
                  <p className={styles.text19}>源对象字段 (Flight)</p>
                </div>
                <div className={styles.cell2}>
                  <p className={styles.text20}>目标对象字段 (Airport)</p>
                </div>
                <div className={styles.cell3}>
                  <p className={styles.text21}>转换类型</p>
                </div>
              </div>
              <div className={styles.body}>
                <div className={styles.row2}>
                  <div className={styles.data}>
                    <p className={styles.departureAirportCode}>
                      departure_airport_code
                    </p>
                    <p className={styles.string}>String</p>
                  </div>
                  <img
                    src="../image/mn0l12ex-chchjg2.svg"
                    className={styles.data2}
                  />
                  <div className={styles.data}>
                    <p className={styles.departureAirportCode}>airport_id</p>
                    <p className={styles.string}>Integer</p>
                  </div>
                  <div className={styles.data3}>
                    <div className={styles.background}>
                      <p className={styles.text22}>Exact Match</p>
                    </div>
                  </div>
                  <div className={styles.data4}>
                    <img
                      src="../image/mn0l12ex-sgp7hec.svg"
                      className={styles.button3}
                    />
                  </div>
                </div>
                <div className={styles.row3}>
                  <div className={styles.data}>
                    <p className={styles.departureAirportCode}>scheduled_time</p>
                    <p className={styles.string}>DateTime</p>
                  </div>
                  <img
                    src="../image/mn0l12ex-chchjg2.svg"
                    className={styles.data2}
                  />
                  <div className={styles.data}>
                    <p className={styles.departureAirportCode}>operation_date</p>
                    <p className={styles.string}>Date</p>
                  </div>
                  <div className={styles.data5}>
                    <div className={styles.background2}>
                      <p className={styles.text22}>Cast To Date</p>
                    </div>
                  </div>
                  <div className={styles.data4}>
                    <img
                      src="../image/mn0l12ex-sgp7hec.svg"
                      className={styles.button3}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className={styles.asideRightColumnInsp}>
        <div className={styles.horizontalBorder}>
          <div className={styles.heading34}>
            <img
              src="../image/mn0l12ex-qrjfwxy.svg"
              className={styles.container15}
            />
            <p className={styles.text23}>链接预览 (Link Preview)</p>
          </div>
          <div className={styles.backgroundBorder4}>
            <div className={styles.abstractBackgroundGr} />
            <div className={styles.simplifiedVisualNode}>
              <div className={styles.container17}>
                <div className={styles.backgroundBorder}>
                  <img
                    src="../image/mn0l12ex-236t554.svg"
                    className={styles.container16}
                  />
                </div>
                <p className={styles.text24}>Flight</p>
              </div>
              <div className={styles.autoWrapper2}>
                <div className={styles.container19}>
                  <div className={styles.backgroundBorder2}>
                    <img
                      src="../image/mn0l12ex-s6beewb.svg"
                      className={styles.container18}
                    />
                  </div>
                  <p className={styles.text25}>Airport</p>
                </div>
                <div className={styles.container20}>
                  <div className={styles.horizontalDivider} />
                  <div className={styles.backgroundBorder3}>
                    <p className={styles.text26}>1 : N</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className={styles.button4}>
            <p className={styles.text27}>进入图形编辑器</p>
          </div>
        </div>
        <div className={styles.container29}>
          <div className={styles.heading35}>
            <img
              src="../image/mn0l12ex-nr5m8sg.svg"
              className={styles.container21}
            />
            <p className={styles.text28}>更改记录 (Change History)</p>
          </div>
          <div className={styles.container28}>
            <div className={styles.verticalDivider} />
            <div className={styles.container23}>
              <div className={styles.container22}>
                <p className={styles.text29}>修改了字段映射</p>
                <p className={styles.a202310241430Adminis}>
                  2023-10-24 14:30 · Administrator
                </p>
                <div className={styles.overlay2}>
                  <p className={styles.text30}>
                    Updated mapping for 'scheduled_time'
                  </p>
                </div>
              </div>
              <div className={styles.background4}>
                <div className={styles.background3} />
              </div>
            </div>
            <div className={styles.container25}>
              <div className={styles.container24}>
                <p className={styles.text29}>更改了显示名称</p>
                <p className={styles.a202310241430Adminis}>
                  2023-10-23 09:15 · System
                </p>
              </div>
              <div className={styles.background6}>
                <div className={styles.background5} />
              </div>
            </div>
            <div className={styles.container27}>
              <div className={styles.container26}>
                <p className={styles.text29}>创建了链接类型</p>
                <p className={styles.a202310201640Adminis}>
                  2023-10-20 16:40 · Administrator
                </p>
              </div>
              <div className={styles.background6}>
                <div className={styles.background5} />
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className={styles.stickyFooterActions}>
        <div className={styles.background7}>
          <img src="../image/mn0l12ex-qmisggp.svg" className={styles.container30} />
          <p className={styles.text31}>3 个未保存的更改</p>
        </div>
        <div className={styles.container31}>
          <div className={styles.button5}>
            <p className={styles.text32}>放弃草稿</p>
          </div>
          <div className={styles.button6}>
            <div className={styles.buttonShadow}>
              <p className={styles.text33}>保存并发布更改</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Component;
