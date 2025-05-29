from flask import Flask, jsonify, request, render_template, session, redirect, url_for,send_file
from flask_cors import CORS
from db import get_db, init_db
from werkzeug.utils import secure_filename
from neo4j import GraphDatabase
import pymysql
import logging
import homeText,chart
import json
import os
import pandas as pd


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


data = pd.read_csv("../file/data_final.csv",encoding="gbk")
app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = "token123456"  # 跨域密钥

init_db()

# 这里配置neo4j地址和账户密码
NEO4J_URI = "bolt://192.168.31.200:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "12345678"
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# 首页重定向到登录页
@app.route('/')
def index():
    if 'user_id' in session:
        return render_template('index.html')
    return redirect(url_for('login_page'))


@app.route('/login-page',methods=['GET'])
def login_page():
    return render_template('login.html')


@app.route('/sign-page')
def sign_page():
    return render_template('sign.html')


@app.route('/home-page')
def home_page():
    # 检查是否登录
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('index.html')



@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400

    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, username FROM users WHERE username = %s AND password = %s",
                (username, password)
            )
            user = cursor.fetchone()

            if user:
                # 登录成功，设置session
                session['user_id'] = user['id']
                session['username'] = user['username']

                return jsonify({
                    'success': True,
                    'user': user,
                    'message': '登录成功'
                })
            else:
                return jsonify({'error': '用户名或密码错误'}), 401
    except pymysql.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/api/logout', methods=['POST'])
def logout():
    # 清除session
    session.pop('user_id', None)
    session.pop('username', None)
    return jsonify({'success': True, 'message': '已退出登录'}),200

@app.route('/logout')
def logout_page():
    # 渲染 logout 页面
    return render_template('loginout.html')



@app.route('/api/check-auth')
def check_auth():
    # 检查当前登录状态
    if 'user_id' in session:
        return jsonify({
            'isAuthenticated': True,
            'user': {
                'id': session['user_id'],
                'username': session['username']
            }
        })
    return jsonify({'isAuthenticated': False})


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': '缺少必要字段'}), 400

    conn = get_db()
    try:
        with conn.cursor() as cursor:
            # 检查用户名是否存在
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                return jsonify({'error': '用户名已存在'}), 400

            # 创建新用户
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, password)
            )
            user_id = cursor.lastrowid
            conn.commit()

            return jsonify({
                'success': True,
                'user_id': user_id,
                'message': '注册成功'
            }), 201
    except pymysql.Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()
@app.route('/api/indexSum', methods=['GET'])
def index_sum():
    dataList = homeText.main()
    print(dataList)
    print(type(dataList))
    return jsonify({'success': True, 'data': dataList})
@app.route('/api/chart1', methods=['GET'])
def chart1():
    datajson = chart.classFirstTop10(data)
    # print(datajson)
    data_dict = json.loads(datajson)
    return jsonify({'success': True, 'data': data_dict})
@app.route('/api/chart2', methods=['GET'])
def chart2():
    datajson = chart.classLastTop10(data)
    data_dict = json.loads(datajson)
    data_dict = json.loads(datajson)
    return jsonify({'success': True, 'data': data_dict})
@app.route('/api/chart3', methods=['GET'])
def chart3():
    datajson = chart.teacherSum(data)
    data_dict = json.loads(datajson)
    data_dict = json.loads(datajson)
    return jsonify({'success': True, 'data': data_dict})

@app.route('/api/chart4', methods=['GET'])
def chart4():
    # 假设 datajson 是一个字典，直接使用它
    datajson = chart.count_course_words(data)  # 你的数据字典

    # 如果 datajson 是字典，就直接使用它
    if isinstance(datajson, dict):
        data_dict = datajson
    else:
        # 如果是字符串，解析它
        data_dict = json.loads(datajson)

    # 继续处理数据
    return jsonify(data_dict)
@app.route('/api/chart5', methods=['GET'])
def chart5():
    datajson = chart.count_courses_by_college(data)
    data_dict = json.loads(datajson)
    return jsonify({'success': True, 'data': data_dict})


# @app.route('/api/search')
# def search_course():
#     course_name = request.args.get("course_name")
#     if not course_name:
#         return jsonify([])
#
#     with driver.session() as session:
#         query = """
#         MATCH (c1:Course {name: $name})-[r:先修课程|同一领域]->(c2:Course)
#         RETURN c1.name AS name, c2.name AS related_course, type(r) AS relation_type
#         """
#         result = session.run(query, name=course_name)
#         records = [{"name": record["name"],
#                     "related_course": record["related_course"],
#                     "relation_type": record["relation_type"]} for record in result]
#         return jsonify(records)
#
#
# @app.route('/api/searchTeacher', methods=['GET'])
# def search_teacher():
#     teacher_name = request.args.get("name")
#     if not teacher_name:
#         return jsonify({"error": "教师姓名不能为空"}), 400
#
#     try:
#         with driver.session() as session:
#             query = """
#             MATCH (t:Instructor {name: $name})-[r]-(related)
#             WHERE NOT (related:Instructor)
#             RETURN t as teacher,
#                    type(r) as relation_type,
#                    related,
#                    labels(related) as related_labels
#
#             UNION
#
#             MATCH (t:Instructor {name: $name})-[:教授]->(c:Course)-[r]-(related)
#             WHERE NOT (related:Instructor) AND NOT (related = t)
#             RETURN t as teacher,
#                    type(r) as relation_type,
#                    related,
#                    labels(related) as related_labels
#
#             UNION
#
#             MATCH (t:Instructor {name: $name})-[:隶属于]->(s:School)
#             RETURN t as teacher,
#                    '隶属于' as relation_type,
#                    s as related,
#                    ['School'] as related_labels
#             """
#
#             result = session.run(query, name=teacher_name)
#
#             records = []
#             school_info = None
#
#             for record in result:
#                 related = record["related"]
#                 labels = record["related_labels"]
#
#                 # 处理学校信息
#                 if "School" in labels:
#                     school_info = {
#                         "school_name": related["name"],
#                         "school_id": related.id
#                     }
#                     continue
#
#                 # 处理课程信息
#                 if "Course" in labels:
#                     records.append({
#                         "teacher_name": record["teacher"]["name"],
#                         "course_name": related["name"],
#                         "relation_type": record["relation_type"],
#                         "related_course": related["name"]
#                     })
#
#             # 返回统一格式
#             return jsonify({
#                 "teacher_info": {
#                     "name": teacher_name
#                 },
#                 "school_info": school_info,
#                 "course_relations": records
#             })
#
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

def fetch_course_details(tx, course_name):
    query = """
    MATCH (course:Course {name: $course_name})
    OPTIONAL MATCH (course)<-[r:教授]-(teacher:Instructor)
    OPTIONAL MATCH (course)-[r2:先修课程|同一领域]->(related_course:Course)
    RETURN course.name AS course_name,
           collect(DISTINCT teacher.name) AS teachers,
           collect(DISTINCT related_course.name) AS related_courses,
           collect(DISTINCT r) AS teacher_relationships,
           collect(DISTINCT r2) AS course_relationships
    """
    result = tx.run(query, course_name=course_name)
    record = result.single()
    return record


# API 路由：输入课程名返回有关系的课程和老师，并返回关系类型
@app.route('/api/searchClass', methods=['GET'])
def search_class():
    course_name = request.args.get('course_name')  # 获取课程名称
    if not course_name:
        return jsonify({"error": "Course name is required!"}), 400

    try:
        # 在 Neo4j 中执行查询
        with driver.session() as session:
            course_details = session.read_transaction(fetch_course_details, course_name)

        if not course_details:
            return jsonify({"message": "No details found for the given course."}), 200

        return jsonify({
            "course_name": course_details["course_name"],
            "teachers": course_details["teachers"],
            "related_courses": course_details["related_courses"],
            "teacher_relationships": [str(rel.type) for rel in course_details["teacher_relationships"]],
            "course_relationships": [str(rel.type) for rel in course_details["course_relationships"]]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/searchTeacher', methods=['GET'])
def search_teacher():
    teacher_name = request.args.get('teacher_name')
    if not teacher_name:
        return jsonify({"error": "teacher_name parameter is required"}), 400

    try:
        with driver.session() as session:
            # 查询教师及其关系
            result = session.run("""
                MATCH (teacher:Instructor {name: $teacher_name})
                OPTIONAL MATCH (teacher)-[teaches:教授]->(course:Course)
                OPTIONAL MATCH (teacher)-[belongs:隶属于]->(school:School)
                RETURN teacher.name AS teacher_name,
                       properties(teacher) AS teacher_properties,
                       collect(DISTINCT {
                           course: course.name, 
                           relation: type(teaches)
                       }) AS courses,
                       CASE WHEN school IS NOT NULL THEN {
                           name: school.name,
                           relation: type(belongs)
                       } ELSE null END AS school
                """, teacher_name=teacher_name)

            record = result.single()
            if not record:
                return jsonify({"error": "Teacher not found"}), 404

            # 构建响应数据
            response_data = {
                "teacher": {
                    "name": record["teacher_name"],
                    **record["teacher_properties"]
                },
                "courses": record["courses"],
                "school": record["school"]
            }

            return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# @app.route('/data-prediction', methods=['GET', 'POST'])
# def data_prediction():
#     node_type = request.args.get('node_type', 'Course')  # 获取用户选择的节点类型，默认为课程
#     try:
#         # 使用 f-string 格式化查询语句
#         query = f"""
#             CALL gds.pageRank.stream('educationGraph', {{maxIterations: 20, dampingFactor: 0.85}})
#             YIELD nodeId, score
#             MATCH (n:{node_type}) WHERE id(n) = nodeId
#             RETURN n.name AS NodeName, score
#             ORDER BY score DESC
#             LIMIT 10
#         """
#
#         with driver.session() as session:
#             result = session.run(query)
#             predictions = [{"NodeName": record["NodeName"] if record["NodeName"] else "No Name",
#                             "score": record["score"]} for record in result]
#
#             # 打印查询结果
#             print(f"Predictions: {predictions}")  # 在服务器端打印数据
#
#         return render_template('data_prediction.html', predictions=predictions)  # 渲染正确的模板
#
#     except Exception as e:
#         print(f"Error occurred: {e}")  # 输出错误
#         return jsonify({'error': str(e)}), 500


def query_to_dataframe(typeData):
    # 定义查询语句
    query = """
    CALL gds.pageRank.stream('educationGraph', {maxIterations: 20, dampingFactor: 0.85})
    YIELD nodeId, score
    MATCH (n) WHERE id(n) = nodeId
    WITH n, score,
         CASE 
             WHEN 'Course' IN labels(n) THEN '课程'
             WHEN 'Instructor' IN labels(n) THEN '老师'
             WHEN 'School' IN labels(n) THEN '学校'
             ELSE '其他'
         END AS category
    RETURN category, n.name AS NodeName, score
    ORDER BY score DESC
    """

    # 执行查询
    with driver.session() as session:
        result = session.run(query)

        # 将查询结果转化为字典列表
        records = [{"category": record["category"], "NodeName": record["NodeName"], "score": record["score"]} for record
                   in result]

        # 使用 Pandas 将字典列表转换为 DataFrame
        df = pd.DataFrame(records)

        print("DataFrame 已生成！")

        # 根据类型筛选数据
        if typeData == "school":
            filtered_df = df[df['category'] == '学校']
            return filtered_df
        elif typeData == "class":
            filtered_df1 = df[df['category'] == '课程']
            return filtered_df1
        elif typeData == "teacher":
            filtered_df2 = df[df['category'] == '老师']
            return filtered_df2
        else:
            return 'Type error!!'


# 创建Flask接口
@app.route('/api/searchCourse', methods=['GET'])
def search_course():
    # 获取查询参数
    type_name = request.args.get('type_name', default=None, type=str)

    if type_name is None:
        return jsonify({"error": "No type_name provided"}), 400

    # 调用 query_to_dataframe 函数并获取相应的 DataFrame
    df = query_to_dataframe(type_name)

    if isinstance(df, str):
        # 如果返回了 'Type error!!'，表示错误
        return jsonify({"error": df}), 400
    else:
        # 将 DataFrame 转换为字典格式并返回 JSON
        result = df.to_dict(orient='records')  # 转换为字典列表
        return jsonify(result)

# @app.route("/api/neo4jData"),methods=['POST']



# UPLOAD_FOLDER = 'uploads/'
# ALLOWED_EXTENSIONS = {'csv', 'xlsx'}
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # 确保上传目录存在
# @app.route('/upload-data', methods=['POST'])
# def upload_data():
#     if 'file' not in request.files:
#         return '没有选择文件', 400
#     file = request.files['file']
#     if file.filename == '':
#         return '没有选择文件', 400
#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(filepath)
#
#         # 处理数据导入 Neo4j
#         if filename.endswith('.xlsx'):
#             df = pd.read_excel(filepath)
#         elif filename.endswith('.csv'):
#             df = pd.read_csv(filepath)
#
#         with driver.session() as session:
#             session.write_transaction(create_entities, df)
#
#         return '文件上传并导入成功！', 200
@app.route('/data-management')
def data_management():
    # 检查是否已登录
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('data_manage.html')


# @app.route('/submit-course', methods=['POST'])
# def submit_course():
#     try:
#         # 获取表单提交的数据
#         course_names = request.form.getlist('course_name[]')
#         instructor_names_list = [request.form.getlist(f'instructor_name_{i}[]') for i in range(1, len(course_names) + 1)]
#         school_names = request.form.getlist('school_name[]')
#         start_dates = request.form.getlist('start_date[]')
#         end_dates = request.form.getlist('end_date[]')
#
#         with driver.session() as session:
#             # 遍历所有课程信息
#             for course_name, instructor_names, school_name, start_date, end_date in zip(course_names, instructor_names_list, school_names, start_dates, end_dates):
#                 # 为每个教师与课程建立关系
#                 for instructor_name in instructor_names:
#                     session.write_transaction(create_course, course_name, instructor_name.strip(), school_name, start_date, end_date)
#
#         return jsonify({"success": True, "message": "数据已成功提交！"}), 200
#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)}), 500
#
# def create_course(tx, course_name, instructor_name, school_name, start_date, end_date):
#     tx.run("""
#         MERGE (s:School {name: $school_name})
#         MERGE (i:Instructor {name: $instructor_name})
#         MERGE (c:Course {name: $course_name})
#         SET c.start_date = $start_date,
#             c.end_date = $end_date
#         MERGE (i)-[:教授]->(c)
#         MERGE (i)-[:隶属于]->(s)
#     """, {
#         'course_name': course_name,
#         'instructor_name': instructor_name,
#         'school_name': school_name,
#         'start_date': start_date,
#         'end_date': end_date
#     })

@app.route('/submit-course', methods=['POST'])
def submit_course():
    try:
        data = request.get_json()

        course_names = data.get('course_names', [])
        instructor_names_list = data.get('instructor_names_list', [])
        school_names = data.get('school_names', [])
        start_dates = data.get('start_dates', [])
        end_dates = data.get('end_dates', [])
        enrollment_counts = data.get('enrollment_counts', [])
        course_open_counts = data.get('course_open_counts', [])

        logging.debug(
            f"Received data: {course_names}, {instructor_names_list}, {school_names}, {start_dates}, {end_dates}, {enrollment_counts}, {course_open_counts}")

        with driver.session() as session:
            for course_name, instructor_names, school_name, start_date, end_date, enrollment_count, course_open_count in zip(
                    course_names, instructor_names_list, school_names, start_dates, end_dates, enrollment_counts,
                    course_open_counts):
                logging.debug(
                    f"Processing course: {course_name}, instructors: {instructor_names}, school: {school_name}, start date: {start_date}, end date: {end_date}, enrollment count: {enrollment_count}, open count: {course_open_count}")

                for instructor_name in instructor_names:
                    logging.debug(f"Creating relationship for instructor: {instructor_name}")
                    session.write_transaction(create_course, course_name, instructor_name.strip(), school_name,
                                              start_date, end_date, enrollment_count, course_open_count)

        return jsonify({"success": True, "message": "数据已成功提交！"}), 200
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


def create_course(tx, course_name, instructor_name, school_name, start_date, end_date, enrollment_count,
                  course_open_count):
    try:
        logging.debug(f"Creating course and relationships for {course_name} by {instructor_name} at {school_name}")

        # 使用单个事务处理所有操作
        tx.run("""
            MERGE (s:School {name: $school_name})
            MERGE (i:Instructor {name: $instructor_name})
            MERGE (c:Course {name: $course_name})
            MERGE (i)-[:教授]->(c)
            MERGE (i)-[:隶属于]->(s)
            SET c.start_date = $start_date,
                c.end_date = $end_date,
                c.enrollment_count = $enrollment_count,
                c.course_open_count = $course_open_count
        """, {
            "course_name": course_name,
            "instructor_name": instructor_name,
            "school_name": school_name,
            "start_date": start_date,
            "end_date": end_date,
            "enrollment_count": enrollment_count,
            "course_open_count": course_open_count
        })

        logging.debug(f"Successfully created course: {course_name} and relationships for {instructor_name}")

    except Exception as e:
        logging.error(f"Error while creating course data for {course_name}: {e}")
        raise



if __name__ == '__main__':
    app.run(debug=True)