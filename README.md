# 教育知识图谱系统 - 大学生课程设计项目

## 项目概述

这是一个基于Neo4j图数据库的教育知识图谱系统，作为大学生课程设计作业开发完成。系统实现了教育领域中的教师、课程和学校等实体之间的关系可视化与智能查询功能。(半成品 仅供参考)

## 技术栈

### 后端技术

- **开发语言**: Python
- **Web框架**: Flask
- **数据库**: Neo4j图数据库
- **数据处理**: Pandas

### 前端技术

- **核心语言**: HTML5, JavaScript
- **数据可视化**: ECharts

## 系统功能

### 1. 知识图谱查询功能

- **教师查询**：通过教师姓名查询其所属学校和教授的课程
- **课程查询**：通过课程名称查询授课教师和相关的其他课程
- **关系展示**：可视化展示实体间的"教授"、"先修课程"、"同一领域"等关系

### 2. 数据可视化分析

- 使用ECharts实现多种数据图表展示：
  - 课程排名分析（前10/后10课程）
  - 教师授课数量统计
  - 课程关键词词频分析
  - 学院课程数量分布

### 3. 数据管理功能

- 课程数据提交
- 实体关系维护

## 系统架构

```
教育知识图谱系统
├── 前端 (HTML5 + JavaScript + ECharts)
│   ├── 用户界面
│   ├── 数据可视化
│   └── API调用
│
├── 后端 (Python + Flask)
│   ├── 路由控制
│   ├── 业务逻辑
│   └── Neo4j数据库操作
│ 	└── Mysql数据库操作
│
└── 数据层 (Neo4j)
    ├── 节点(教师、课程、学校)
    └── 关系(教授、先修、同领域等)
```

## 部署说明

### 环境要求

需要提前安装python3

### 1. 安装项目依赖

1. 克隆项目后进入项目目录：

   ```
   git clone https://github.com/lvfengfree/eduNeo4j.git
   cd eduNeo4j
   ```

2. 安装依赖包：

   ```
   pip install -r requirements.txt
   ```

### 2. 使用 Docker 安装 Neo4j 数据库

#### 运行 Neo4j 容器

1. 拉取 Neo4j 官方镜像：

   ```
   docker pull neo4j:4.4
   ```

2. 启动 Neo4j 容器：

   ```
   docker run \
       --name edu-neo4j \
       -p 7474:7474 -p 7687:7687 \
       -v neo4j_data:/data \
       -v neo4j_logs:/logs \
       -v neo4j_import:/var/lib/neo4j/import \
       --env NEO4J_AUTH=neo4j/12345678 \
       --restart unless-stopped \
       -d neo4j:4.4
   ```

3. 访问 Neo4j 浏览器：

   - 打开 `http://localhost:7474`

### 3. 配置项目连接 Neo4j

修改项目中的数据库配置（`app.py` 的26行-28行配置）：

```
NEO4J_URI = "bolt://localhost:7687" 
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "12345678"
```

### 4. 配置mysql

1. 使用相应软件链接mysql创建库:

   ```mysql
   CREATE DATABASE edu_qa_system;
   ```

2. 更改代码`config.py`中的配置

   ```
   # 数据库配置
   DB_CONFIG = {
       'host': 'localhost',
       'user': 'root',
       'password': '123456',
       'db': 'edu_qa_system',
       'charset': 'utf8mb4'
   }
   ```

3. 更改`homeText.py`第14行-23行

   ```
   def get_user_count():
       # 数据库连接配置
       db_config = {
           'host': 'localhost', 
           'user': 'root',  
           'password': '123456', 
           'database': 'edu_qa_system',  
           'charset': 'utf8mb4',
           'cursorclass': pymysql.cursors.DictCursor
       }
   ```

### 4. 将数据导入neo4j中并且建立关系

运行`neo4j/LoadData.py`

```
python neo4j/LoadData.py
```

### 5. neo4j容器安装GDS

访问此网站自行安装插件[安装 - Neo4j Graph Data Science](https://neo4j.com/docs/graph-data-science/current/installation/)

### 6. 启动应用

```
python app.py
```

访问 `http://localhost:5000` 即可使用系统

------

*注：本项目为课程设计作业，仅用于学习交流目的。*
*数据来源：各大平台*
