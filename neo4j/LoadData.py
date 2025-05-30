from neo4j import GraphDatabase
import pandas as pd

# 连接到 Neo4j 数据库
uri = "bolt://192.168.31.200:7687"  # 如果你使用的是默认的 Neo4j 配置
username = "neo4j"
password = "12345678"  # 请根据你的实际密码修改
driver = GraphDatabase.driver(uri, auth=(username, password))

# 读取更新后的Excel文件
file_path_updated = r"./neo4jData.xlsx"
df_updated = pd.read_excel(file_path_updated, sheet_name='Sheet1')


# 定义创建实体和关系的函数
def create_entities(tx, df):
    for _, row in df.iterrows():
        instructors = row['instructor_name'].split('，')  # 多个老师分开
        for instructor in instructors:
            # 为每个老师创建关系
            tx.run("""
                MERGE (s:School {name: $school_name})
                MERGE (i:Instructor {name: $instructor_name})
                MERGE (c:Course {name: $course_name})
                SET c.enrollment_count = $enrollment_count,
                    c.course_open_count = $course_open_count,
                    c.start_date = $start_date,
                    c.end_date = $end_date,
                    c.start_year = $start_year
                MERGE (i)-[:教授]->(c)  
                MERGE (i)-[:隶属于]->(s)  
            """, {
                'school_name': row['school_name'],
                'instructor_name': instructor,
                'course_name': row['course_name'],
                'enrollment_count': row['enrollment_count'],  # 学生人数
                'course_open_count': row['course_open_count'],  # 课程开设次数
                'start_date': row['start_date'],
                'end_date': row['end_date'],
                'start_year': row['start_year']
            })


# 定义课程间的关系（先修课程和同一领域关系）
def create_course_relations(tx, relations):
    for c1, c2, rtype in relations:
        if rtype == "同一领域":
            # 创建无向关系
            tx.run("""
                MATCH (a:Course {name: $c1}), (b:Course {name: $c2})
                MERGE (a)-[:同一领域]-(b)
            """, {"c1": c1, "c2": c2})
        else:
            # 创建有向关系
            tx.run("""
                MATCH (a:Course {name: $c1}), (b:Course {name: $c2})
                MERGE (a)-[:先修课程]->(b)
            """, {"c1": c1, "c2": c2})


# 执行数据导入
with driver.session() as session:
    session.write_transaction(create_entities, df_updated)
    # 添加课程关系
    course_relations = [
        ("工程导论", "工程图学", "先修课程"),
        ("工程图学", "机械设计基础", "先修课程"),
        ("机械设计基础", "机械原理", "先修课程"),
        ("机械原理", "机械设计", "先修课程"),
        ("机械设计", "机械制造基础", "先修课程"),
        ("机械设计基础", "焊接方法与设备", "先修课程"),
        ("焊接方法与设备", "钢结构设计原理", "先修课程"),
        ("机械设计", "机械设计课程设计", "先修课程"),
        ("机械设计课程设计", "电梯选型设计", "先修课程"),
        ("电梯选型设计", "游船游艇创意设计", "先修课程"),
        ("游船游艇创意设计", "塑料成型工艺与三维模具设计", "先修课程"),
        ("塑料成型工艺与三维模具设计", "CAD/CAM技术", "先修课程"),
        ("CAD/CAM技术", "现代控制理论", "先修课程"),
        ("现代控制理论", "电气与PLC技术", "先修课程"),
        ("电气与PLC技术", "电机与拖动-铜与铁的艺术", "先修课程"),
        ("电机与拖动-铜与铁的艺术", "模拟电子技术", "先修课程"),
        ("模拟电子技术", "移动应用程序开发", "先修课程"),
        ("电子电路设计（电路分析基础，电路）", "移动应用程序开发", "先修课程"),

        ("工程导论", "工程图学", "同一领域"),
        ("工程图学", "机械设计基础", "同一领域"),
        ("机械设计基础", "机械原理", "同一领域"),
        ("机械原理", "机械设计", "同一领域"),
        ("机械设计", "机械制造基础", "同一领域"),
        ("焊接方法与设备", "钢结构设计原理", "同一领域"),
        ("机械设计课程设计", "电梯选型设计", "同一领域"),
        ("电梯选型设计", "游船游艇创意设计", "同一领域"),
        ("游船游艇创意设计", "塑料成型工艺与三维模具设计", "同一领域"),
        ("塑料成型工艺与三维模具设计", "CAD/CAM技术", "同一领域"),
        ("CAD/CAM技术", "现代控制理论", "同一领域"),
        ("现代控制理论", "电气与PLC技术", "同一领域"),
        ("电气与PLC技术", "电机与拖动-铜与铁的艺术", "同一领域"),
        ("电机与拖动-铜与铁的艺术", "模拟电子技术", "同一领域"),
        ("模拟电子技术", "移动应用程序开发", "同一领域"),
        ("电子电路设计（电路分析基础，电路）", "移动应用程序开发", "同一领域"),

        ("船舶与海洋工程导论", "船舶流体力学", "先修课程"),
        ("船舶流体力学", "船舶结构力学", "先修课程"),
        ("船舶结构力学", "船舶柴油机构造与原理", "先修课程"),
        ("船舶柴油机构造与原理", "船舶设计原理", "先修课程"),
        ("船舶设计原理", "船舶辅机", "先修课程"),
        ("船舶与海洋工程导论", "近现代船舶工业发展与中国崛起", "先修课程"),

        ("船舶与海洋工程导论", "船舶流体力学", "同一领域"),
        ("船舶流体力学", "船舶结构力学", "同一领域"),
        ("船舶结构力学", "船舶柴油机构造与原理", "同一领域"),
        ("船舶柴油机构造与原理", "船舶设计原理", "同一领域"),
        ("船舶设计原理", "船舶辅机", "同一领域"),
        ("船舶辅机", "近现代船舶工业发展与中国崛起", "同一领域"),
        ("材料性能", "材料结构表征", "先修课程"),
        ("材料结构表征", "材料连接原理", "先修课程"),
        ("材料连接原理", "材料力学", "先修课程"),
        ("材料力学", "材料物理性能", "先修课程"),
        ("材料力学", "新能源材料", "先修课程"),
        ("新能源材料", "薄膜太阳能电池", "先修课程"),
        ("薄膜太阳能电池", "太阳能电池测试及标准", "先修课程"),

        ("材料性能", "材料结构表征", "同一领域"),
        ("材料结构表征", "材料连接原理", "同一领域"),
        ("材料连接原理", "材料力学", "同一领域"),
        ("材料力学", "材料物理性能", "同一领域"),
        ("材料力学", "新能源材料", "同一领域"),
        ("新能源材料", "薄膜太阳能电池", "同一领域"),
        ("薄膜太阳能电池", "太阳能电池测试及标准", "同一领域"),

        ("高等数学A（1）", "高等数学A（2）", "先修课程"),
        ("高等数学A（2）", "高等代数", "先修课程"),
        ("高等代数", "线性代数", "先修课程"),
        ("高等数学A（2）", "数学分析", "先修课程"),
        ("线性代数", "数学物理方法", "先修课程"),
        ("数学分析", "数学物理方法", "先修课程"),
        ("高等代数", "数学分析", "先修课程"),

        ("高等数学A（1）", "高等数学A（2）", "同一领域"),
        ("高等数学A（2）", "高等代数", "同一领域"),
        ("高等代数", "线性代数", "同一领域"),
        ("线性代数", "数学物理方法", "同一领域"),
        ("数学分析", "数学物理方法", "同一领域"),
        ("概率论与数理统计", "数学物理方法", "同一领域"),

        ("计算思维", "面向对象程序设计C++", "先修课程"),
        ("面向对象程序设计C++", "数据结构与算法", "先修课程"),
        ("数据结构与算法", "软件测试与质量保证", "先修课程"),
        ("数据结构与算法", "数据库原理与应用", "先修课程"),
        ("数据结构与算法", "微机原理与接口技术", "先修课程"),
        ("微机原理与接口技术", "微机原理及应用", "先修课程"),
        ("微机原理及应用", "数据库原理与应用", "先修课程"),

        ("计算思维", "面向对象程序设计C++", "同一领域"),
        ("面向对象程序设计C++", "数据结构与算法", "同一领域"),
        ("数据结构与算法", "软件测试与质量保证", "同一领域"),
        ("数据结构与算法", "数据库原理与应用", "同一领域"),
        ("数字电子技术", "微机原理与接口技术", "同一领域"),
        ("微机原理与接口技术", "微机原理及应用", "同一领域"),

        ("生命科学导论", "分子生物学（双语）", "先修课程"),
        ("分子生物学（双语）", "生物化学", "先修课程"),
        ("生命科学导论", "植物学", "先修课程"),
        ("植物学", "微生物学", "先修课程"),
        ("微生物学", "动物学", "先修课程"),
        ("动物学", "动物遗传学", "先修课程"),
        ("生物化学", "人体解剖学", "先修课程"),
        ("微生物学", "动物传染病学", "先修课程"),
        ("人体解剖学", "外科学总论", "先修课程"),
        ("外科学总论", "生物医药企业EHS管理", "先修课程"),

        ("生命科学导论", "分子生物学（双语）", "同一领域"),
        ("分子生物学（双语）", "生物化学", "同一领域"),
        ("生命科学导论", "植物学", "同一领域"),
        ("植物学", "微生物学", "同一领域"),
        ("微生物学", "动物学", "同一领域"),
        ("动物学", "动物遗传学", "同一领域"),
        ("生物化学", "人体解剖学", "同一领域"),
        ("微生物学", "动物传染病学", "同一领域"),
        ("人体解剖学", "外科学总论", "同一领域"),
        ("外科学总论", "生物医药企业EHS管理", "同一领域"),

        ("化工原理实验", "化工原理（下）", "先修课程"),
        ("化工原理（下）", "化工热力学", "先修课程"),
        ("化工热力学", "有机化学实验", "先修课程"),
        ("有机化学实验", "环境监测与仪器分析", "先修课程"),
        ("环境监测与仪器分析", "水污染控制工程（一）", "先修课程"),
        ("水污染控制工程（一）", "水污染控制工程（二）", "先修课程"),
        ("水污染控制工程（二）", "环境保护与可持续发展", "先修课程"),

        ("化工原理实验", "化工原理（下）", "同一领域"),
        ("化工原理（下）", "化工热力学", "同一领域"),
        ("化工热力学", "有机化学实验", "同一领域"),
        ("有机化学实验", "环境监测与仪器分析", "同一领域"),
        ("环境监测与仪器分析", "水污染控制工程（一）", "同一领域"),
        ("水污染控制工程（一）", "水污染控制工程（二）", "同一领域"),
        ("水污染控制工程（二）", "环境保护与可持续发展", "同一领域"),

        ("英语语法", "经典阅读", "先修课程"),
        ("经典阅读", "写作与表达", "先修课程"),
        ("写作与表达", "英语口语交流技巧", "先修课程"),
        ("英语口语交流技巧", "英美诗歌", "先修课程"),
        ("英美诗歌", "英语课程与教学论", "先修课程"),
        ("英语课程与教学论", "中国传统文化", "先修课程"),
        ("中国传统文化", "《史记》女性人物讲读", "先修课程"),
        ("《史记》女性人物讲读", "中国好故事的英文解读", "先修课程"),

        ("英语语法", "经典阅读", "同一领域"),
        ("经典阅读", "写作与表达", "同一领域"),
        ("写作与表达", "英语口语交流技巧", "同一领域"),
        ("英语口语交流技巧", "英美诗歌", "同一领域"),
        ("英美诗歌", "英语课程与教学论", "同一领域"),
        ("英语课程与教学论", "中国传统文化", "同一领域"),
        ("中国传统文化", "《史记》女性人物讲读", "同一领域"),
        ("《史记》女性人物讲读", "中国好故事的英文解读", "同一领域"),

        ("管理学", "企业管理", "先修课程"),
        ("企业管理", "财务管理", "先修课程"),
        ("财务管理", "财务管理：理论与案例", "先修课程"),
        ("财务管理", "管理信息系统", "先修课程"),
        ("管理学", "伦理学", "先修课程"),
        ("伦理学", "环境伦理学", "先修课程"),
        ("法学概论", "工程合同管理", "先修课程"),
        ("城市社会学", "生态学", "先修课程"),
        ("生态学", "城市详细规划", "先修课程"),

        ("管理学", "企业管理", "同一领域"),
        ("企业管理", "财务管理", "同一领域"),
        ("财务管理", "财务管理：理论与案例", "同一领域"),
        ("财务管理", "管理信息系统", "同一领域"),
        ("伦理学", "环境伦理学", "同一领域"),
        ("法学概论", "工程合同管理", "同一领域"),
        ("城市社会学", "生态学", "同一领域"),
        ("生态学", "城市详细规划", "同一领域"),

        ("中学英语课程与教学", "英语进阶2", "先修课程"),
        ("中学思想政治教学论", "职业生涯发展规划及就业指导—意识、认知、决策、行动", "先修课程"),
        ("英语进阶2", "幼儿教育心理学", "先修课程"),
        ("幼儿教育心理学", "体育心理学", "先修课程"),
        ("体育心理学", "职业生涯发展规划及就业指导—意识、认知、决策、行动", "先修课程"),

        ("中学英语课程与教学", "英语进阶2", "同一领域"),
        ("中学思想政治教学论", "职业生涯发展规划及就业指导—意识、认知、决策、行动", "同一领域"),
        ("英语进阶2", "幼儿教育心理学", "同一领域"),
        ("幼儿教育心理学", "体育心理学", "同一领域")
    ]
    session.write_transaction(create_course_relations, course_relations)

# 关闭连接
driver.close()
