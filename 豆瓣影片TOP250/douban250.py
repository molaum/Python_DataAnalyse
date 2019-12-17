#!usr/bin/env python
# -*-coding:utf-8-*-
from pyquery import PyQuery as pq
import requests
import csv
import os
import re
import time

# 定义具有不同功能的函数-获取页面、解析页面、翻页、保存数据


def get_html(url):      # 获取页面
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"
    }           # 构建请求头
    doc = pq(url, headers=headers)      # 请求页面，获取返回url的html
    return doc


def parse_html(doc):        # 解析页面
    li_list = doc(".article .grid_view").find("li")       # 获取影片内容所在区域
    for item in li_list.items():    # 对同一页中每部影片遍历，获取每部影片相关内容
        try:
            movie_poster_src = item(".item .pic a").find("img").attr("src")     # 获取海报的资源地址
            movie_poster_b = requests.get(movie_poster_src).content     # 获取海报，并将图片转为字节
            movie_num = item(".item .pic em").text()        # 获取影片排行的文本值
            movie_url = item(".item .info .hd a").attr("href")          # 获取影片url地址
            movie_name_list = item(".item .info .hd .title").text().split("/")      # 获取影片名称列表
            movie_name = "/".join(clear_strip(movie_name_list))             # 对影片名称去除左右两边空格并以/分开
            movie_score = item(".item .info .bd .star .rating_num").text()          # 获取影片评分
            movie_intro = item(".item .info .bd .quote span").text()           # 获取影片简介
            movie_info = item(".item .info .bd p").text()           # 获取影片中信息集合，利用正则一次获取
            movie_director = "".join(clear_strip(re.findall(r"导演:(.*?)\xa0", movie_info)))        # 去除左右空格并获取导演信息
            movie_star = "".join(re.findall(r"主演:(.*?)\n", movie_info))             # 去除左右空格获取主演信息
            movie_year = "".join(re.findall(r"(\d{4}.*?)\xa0/\xa0", movie_info))            # 获取上映年份信息
            movie_country = "/".join(re.findall(r"\d{4}.*?\xa0/\xa0(.*?)\xa0/\xa0", movie_info)[0].split())        # 去除空格获取拍摄国家信息
            movie_type = "/".join(re.findall(r'\d{4}.*?\xa0/\xa0.*?\xa0/\xa0(.*?)$', movie_info)[0].split()[:-1])      # 去除空格获取拍摄电影类型信息
            movie_comment_count = item(".item .info .bd .star .rating_num").siblings().text().strip()       # 获取评价人数
            yield [movie_num, movie_name, movie_director, movie_star, movie_year, movie_country, movie_type, movie_score,
                   movie_comment_count, movie_intro, movie_url, movie_poster_b]     # 每次循环以列表形式返回值
        except Exception as e:
            print("错误：", repr(e))       # 若出现错误，打印错误信息
            continue
    else:
        print("此页数据爬取成功！")          # 每爬取成功一页打印一次


def next_page(url_r):           # 翻页操作，也是所有函数中的启动操作
    for i in range(10):     # 一共10页
        page = i * 25
        url_next = url_r + "?start=" + str(page) + "&filter="       # 通过观察，此为每页url规律
        doc = get_html(url_next)        # 调用get_html函数，获取页面信息
        for item in parse_html(doc):        # 调用parse_html函数并遍历，把每页每部电影返回的数据打印并保存
            print(item[:-1])
            save_to_file_csv(item)          # 将数据保存到csv文件中
            # save_poster(item)         # 保存影片海报
        time.sleep(1)       # 每次翻页时间间隔为1秒，避免频繁操作
    else:
        print("所有页面爬取成功！")          # 所有页面爬取完，打印信息


def save_to_file_csv(item):
    writer.writerow([item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9], item[10],
                     item[11]])         # 将数据按行的形式保存


def save_poster(item):
    file_path = "D:\\doubanTOP250"          # 保存海报地址
    if not os.path.exists(file_path):           # 判断是否存在该地址，不存在则新建
        os.makedirs(file_path)
    poster_name = str(item[0]) + "_" + item[1] + ".jpg"         # 设置每张海报名称
    with open(file_path + "\\" + poster_name, "wb") as f:
        f.write(item[-1])           # 将海报的二进制内容写入文件


def clear_strip(list_r):      # 将list中每个元素左右空格去除
    new_list = []
    for li in list_r:
        li = li.strip()
        if li:
            new_list.append(li)
    return new_list


url = "https://movie.douban.com/top250"         # 爬取地址
if __name__ == "__main__":
    with open("doubanTOP250.csv", "w", encoding="utf-8",   newline="") as f:       # 创建新文件
        writer = csv.writer(f)              # 利用csv模块写入内容
        writer.writerow(["movie_num", "movie_name", "movie_director", "movie_star", "movie_year", "movie_country",
                         "movie_type", "movie_score", "movie_comment_count", "movie_intro", "movie_url"])       # 创建表头

    file = open("doubanTOP250.csv", "a", encoding="utf-8", newline="")     # 打开上面步骤新建好的文件，"a"为不覆盖添加，调用next_page函数获取并将数据写入文件
    writer = csv.writer(file)
    next_page(url)
    file.close()            # 关闭文件，当不使用with open..时的必要操作



