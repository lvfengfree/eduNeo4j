import pandas as pd
import json
from collections import Counter
import re
import jieba
# from jieba.lac_small.predict import results

data = pd.read_csv(r"../file/data_final.csv",encoding='gbk')
# print(data)

def classFirstTop10(text):
    gp1 = text.groupby("course_name")['enrollment_count'].sum()
    gp1_sorted = gp1.sort_values(ascending=False).head(10)
    json_result = json.dumps(gp1_sorted.to_dict(), ensure_ascii=False)
    # print(json_result)
    return json_result


def classLastTop10(text):
    gp1 = text.groupby("course_name")['enrollment_count'].sum()
    gp1_sorted = gp1.sort_values(ascending=False).tail(10)
    json_result = json.dumps(gp1_sorted.to_dict(), ensure_ascii=False)
    # print(json_result)
    return json_result


def teacherSum(text):
    instructor_count = text.groupby("instructor_name").size()
    top_10_instructors = instructor_count.sort_values(ascending=False).head(10)
    json_result = top_10_instructors.to_json(orient="index", force_ascii=False)
    return json_result


def count_course_words(text):
    all_names = ' '.join(text['course_name'].astype(str).tolist())
    cleaned_text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', all_names)
    words = jieba.lcut(cleaned_text)
    word_counts = Counter(words)
    word_counts = {word: count for word, count in word_counts.items() if len(word) > 1}
    sorted_items = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    top_10_items = sorted_items[:20]  # 只取前10个
    top_10_dict = dict(top_10_items)
    json_result = json.dumps(top_10_dict, ensure_ascii=False, indent=2)
    print(json_result)
    return top_10_dict

def count_courses_by_college(text):
    college_course_count = text.groupby("school_name")['course_name'].size().sort_values(ascending=False)
    json_result = college_course_count.to_json(orient="index", force_ascii=False)
    print(json_result)
    return json_result

# count_courses_by_college(data)
# count_course_words(data)
# teacherSum(data)
# classLastTop10(data)
# count_courses_by_college(data)


print(classFirstTop10(data))
print(classLastTop10(data))