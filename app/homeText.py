import pandas as pd
import pymysql

data = pd.read_csv("../file/data_final.csv",encoding='gbk')
# print(data)

def teacherSum(text): # 传入数据源
    return text["instructor_name"].nunique()

def classSum(text):
    return text["course_name"].nunique()


def get_user_count():
    # 数据库连接配置
    db_config = {
        'host': 'localhost',  # 数据库地址
        'user': 'root',  # 数据库用户名
        'password': '123456',  # 数据库密码
        'database': 'edu_qa_system',  # 数据库名
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }

    connection = None
    try:
        # 建立数据库连接
        connection = pymysql.connect(**db_config)

        with connection.cursor() as cursor:
            # 执行SQL查询
            sql = "SELECT COUNT(*) as user_count FROM users"
            cursor.execute(sql)

            # 获取查询结果
            result = cursor.fetchone()
            return result['user_count']  # 返回用户数量

    except Exception as e:
        print(f"数据库查询出错: {e}")
        return None  # 出错时返回None

    finally:
        # 确保关闭数据库连接
        if connection:
            connection.close()

def main():
    # 获取用户数量
    userCount = get_user_count()

    # 获取教师数量
    sumTeacher = teacherSum(data)

    # 获取课程数量
    sumClass = classSum(data)

    return [userCount, sumTeacher, sumClass, 250]

# 调用 main 函数并打印结果
if __name__ == "__main__":
    result = main()
    print(result)



