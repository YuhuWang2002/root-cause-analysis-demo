import React from 'react';

import styles from './index.module.scss';

const Component = () => {
  return (
    <div className={styles.asideSideNavBar}>
      <div className={styles.container}>
        <p className={styles.text}>配置菜单</p>
        <p className={styles.text2}>工业级架构</p>
      </div>
      <div className={styles.nav}>
        <div className={styles.link}>
          <img src="../image/mn0l1fk5-0nj2h8n.svg" className={styles.container2} />
          <p className={styles.text3}>对象类型</p>
        </div>
        <div className={styles.link2}>
          <img src="../image/mn0l1fk5-l0xvf8m.svg" className={styles.container3} />
          <p className={styles.text3}>链接类型</p>
        </div>
        <div className={styles.linkActiveStateForAc}>
          <img src="../image/mn0l1fk5-db96cuf.svg" className={styles.container4} />
          <p className={styles.text4}>操作</p>
        </div>
        <div className={styles.link3}>
          <img src="../image/mn0l1fk5-d6yz3io.svg" className={styles.container5} />
          <p className={styles.text5}>共享</p>
        </div>
      </div>
    </div>
  );
}

export default Component;
