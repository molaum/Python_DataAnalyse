#!usr/bin/env python
# -*-coding:utf-8-*-
import matplotlib.pyplot as mp
import pandas as pd
from wordcloud import WordCloud
import jieba
import matplotlib.ticker as ticker
import matplotlib.gridspec as mg

pd.options.display.max_columns = None
pd.options.display.max_rows = None              # 设置python在显示数据时全部显示
mp.rcParams["font.sans-serif"] = ["SimHei"]
mp.rcParams["font.serif"] = ["SimHei"]              # 设置图表中显示中文
mp.rcParams["axes.unicode_minus"] = False           # 设置坐标轴负号可显示

data = pd.read_csv("doubanTOP250.csv", index_col=False)         # 当第一列为一序列时，未指定index_col，会自动将此列作为索引
# print(data.info())
data.drop("movie_url", inplace=True, axis=1)            # 删除电影URL列数据
# print(data)

fig, axes = mp.subplots(1, 2, num="豆瓣电影TOP250", figsize=[12, 6], facecolor="lightgray")     # 建立一个1行2列图
# fig.tight_layout()
mp.subplots_adjust(left=0.1, bottom=0.2, right=0.9, top=0.9, wspace=0.3, hspace=0.6)        # 调整subplot间距

# a.重复值检查（检查是否有重名电影）
name_is_dupli = data.duplicated("movie_name").value_counts()
# print(name_is_dupli)
# print(data["movie_name"].unique())        # 检测数据中心非重复值

# b.查看国家或地区与电影制作的排名情况（空值部分请替换为‘0’，可以考虑先按列计数，替换空值，再按行汇总。）
countries = data["movie_country"].str.split("/").apply(pd.Series)       # 获取所有国家，并将一行中含有多个国家的多个国家分开
country = countries.apply(pd.value_counts).fillna(0)                    # 对国家进行计数并填充空值
# print(country)
country.columns = ["area1", "area2", "area3", "area4", "area5", "area6"]        # 修改列名
country["area_count"] = country.sum(axis=1)                                     # 新增一列-对前几列求和
country.sort_values("area_count", ascending=False, inplace=True)                    # 以总和列降序排序
# print(country)

mp.subplot(121)
country.area_count.head(10).plot(kind="bar", color="orangered")         # 绘制前10名数据条形图
mp.title("国家参与制作影片数排行TOP10")
mp.xlabel("地区名", fontsize=12)                                       # 设置x轴标签
mp.ylabel("频次", fontsize=12)
mp.yticks(range(0, 180, 20), [0, 20, 40, 60, 80, 100, 120, 140, 160])       # 设置y轴坐标
mp.xticks(range(10), country.head(10).index, rotation=45)                   # 设置x轴坐标，并让x轴坐标标签旋转45度
# axes[0, 0].xaxis.set_major_locator(10)
for x, y in zip(range(10), country.area_count.head(10)):
    mp.text(x, y, "%d" % y, ha="center", va="bottom")                       # 为每个条形图增加文本注释
# mp.show()

# c.获取电影类型数量前10的类型及上榜次数最多的导演
typies = data["movie_type"].str.split("/").apply(pd.Series)             # 获取电影类型数据，并将一行含有多个值的类型分开
# print(typies)
type = typies.apply(pd.value_counts).fillna(0)                          # 计数并填充空=NaN值为0
# print(type)
type.columns = ["type1", "type2", "type3", "type4", "type5", "type6", "type7"]          # 修改列名
type.drop(index=type.index[:7], axis=0, inplace=True)
type.drop(index=["你是我最好的朋友，你是我唯一的朋友", "年度最佳date", "爱并不需要智商"], axis=0, inplace=True)     # 整理数据，删除错误数据
# print(type)
type["type_count"] = type.sum(axis=1)                                   # 新增一计数列，按行对前几列求和
type.sort_values("type_count", ascending=False, inplace=True)               # 按新增列降序排列
# print(type)

mp.subplot(122)
type.type_count.head(10).plot(kind="bar", color="orangered")                # 绘制前10名条形图
mp.title("最受欢迎影片类型TOP10")
mp.xlabel("影片类型", fontsize=12, labelpad=3)
mp.ylabel("频次", fontsize=12)
mp.xticks(range(10), type.head(10).index, rotation=45)
mp.yticks(range(0, 225, 25), range(0, 225, 25))
for x, y in zip(range(10), type.type_count.head(10)):
    mp.text(x, y, "%d" % y, ha="center", va="bottom")
# mp.show()
# mp.savefig("1_豆瓣电影TOP250.png")

# print(data.info())
directors = data["movie_director"].str.split("/").apply(pd.Series)
# print(directors.info())
director = directors.apply(pd.value_counts).fillna(0)
director.columns = ["direc1", "direc2"]
director["direc_count"] = director.sum(axis=1)
director.sort_values("direc_count", ascending=False, inplace=True)
# print(director)

mp.figure("导演与主演排行榜", figsize=(10, 5))              # 新建另一新图
mp.subplots_adjust(left=0.3, hspace=0.5)            # 调整图中坐标相对位置及坐标间间距
# fig.tight_layout(w_pad=1.2)
mp.subplot(211)
director.direc_count.head(10).plot(kind="barh", width=0.5, color="limegreen")           # 绘制前10名横向条形图
mp.title("导演排行TOP10")
mp.xlabel("频次", fontsize=12)
mp.ylabel("导演", fontsize=12)
for x, y in zip(director.direc_count.head(10), range(10)):
    mp.text(x, y, "%d" % x, ha="left", va="center")
# mp.show()

# d. 对榜单电影中主演接演电影数计数
stars = data["movie_star"].str.split().apply(pd.Series)
stars.drop(columns=range(1, 11), axis=1, inplace=True)
star = stars.apply(pd.value_counts).fillna(0)
star.drop(index=["...", "爱德...", "斯科特..."], axis=0, inplace=True)
# print(star)

mp.subplot(212)
star[0].head(10).plot(kind="barh", width=0.5, color="limegreen")
mp.title("主演出演电影次数排行")
mp.xlabel("频次", fontsize=12)
mp.ylabel("主演", fontsize=12)
for x, y in zip(star[0].head(10), range(10)):
    mp.text(x, y, "%d" % x, ha="left", va="center")
# mp.savefig("2_导演与主演排行榜.png")

# e.评分的分布。
mp.figure("评分、上映年份、排名、评价人数关系", figsize=(15, 9))             # 再新建一图
mp.subplots_adjust(wspace=0.5, hspace=0.8)                  # 调整图中坐标相对位置及坐标间间距
gs = mg.GridSpec(4, 3)                  # 生成栅格布局器，方便控制每一坐标位置
mp.subplot(gs[2, 0])                # 在第3行第1列画图
mp.hist(data["movie_score"], bins=15, alpha=0.8)            # 绘制评分直方图
mp.title("影片评分分布")
mp.xlabel("评分", fontsize=12)
mp.ylabel("频次", fontsize=12)
# mp.show()

# f.评分和排名的关系。
score_num_corr = (data["movie_score"]).corr(1/data["movie_num"])        # 计算评分与排名间关系，因排名越大等级越小，故作倒数处理

mp.subplot(gs[1, 0])                # 在第2行第1列绘制
mp.scatter(data["movie_score"], 1 / data["movie_num"],  label="r= " + str("%.2f" % score_num_corr), s=12)
mp.legend(fontsize=8)               # 设置图例
mp.title("评分与排名关系")
mp.xlabel("评分", fontsize=12)
mp.ylabel("排名", fontsize=12)
# mp.show()

# g. 上映年份的分布
year = data["movie_year"].value_counts()
year.drop(index=["1983(中国大陆) / 2019(中国大陆重映)", "1961(中国大陆) / 1964(中国大陆) / 1978(中国大陆) / 2004(中国大陆)"], axis=0, inplace=True)
year.sort_index(inplace=True)
# print(year)

ax1 = mp.subplot(gs[0, 0])          # 在第1行第1列绘制
ax1.plot(year)
ax1.set_title("每年上映电影数")
ax1.tick_params(labelsize=9, rotation=45)           # 设置坐标参数
ax1.xaxis.set_major_locator(ticker.MultipleLocator(5))      # 设置坐标间距，每隔5个显示一个坐标值
# mp.show()

# h. 评分与上映年份关系

data.drop(index=[58, 168], axis=0, inplace=True)
ax2 = mp.subplot(gs[:3, 1])                      # 在第一列绘制占三行高的图
ax2.scatter(data["movie_score"], data["movie_year"])        # 绘制散点图
ax2.yaxis.set_major_locator(ticker.MultipleLocator(5))
ax2.set_xlabel("评分", fontsize=12)
ax2.set_ylabel("上映年份", fontsize=12)
ax3 = mp.subplot(gs[:3, 2])                  # 在第二列绘制占三行高的图
ax3.scatter(data["movie_year"], data["movie_score"])
ax3.xaxis.set_major_locator(ticker.MultipleLocator(5))
ax3.tick_params(labelsize=9, rotation=45)
ax3.set_xlabel("上映年份", fontsize=12)
ax3.set_ylabel("评分", fontsize=12)

ax4 = mp.axes([0.4, 0.1, 0.5, 0.8], zorder=0, facecolor="w", alpha=1)           # 目的是为了给两个散点图设置统一标题
ax4.set_title("评分与上映年份关系")
ax4.set_xticks(())
ax4.set_yticks(())
ax4.patch.set_facecolor("none")             # 设置坐标系无背景颜色
# ax4.patch.set_alpha(0)
ax = mp.gca()                               # 获取当前绘图区域
ax.spines["right"].set_color("none")
ax.spines["left"].set_color("none")
ax.spines["top"].set_color("none")
ax.spines["bottom"].set_color("none")           # 将坐标系四条“脊柱”颜色设为无
# mp.show()

# 评价人数
# print(data.info())
data["movie_comment_count"] = data["movie_comment_count"].str.strip("人评价").astype(int)
# print(data)
num_comment_corr = data["movie_num"].corr(data["movie_comment_count"])
ax5 = mp.subplot(gs[3, :])
ax5.scatter(data["movie_num"], data["movie_comment_count"], s=5, label="%.2f" % num_comment_corr)
ax5.set_title("电影排名与评价人数关系")
ax5.xaxis.set_major_locator(ticker.MultipleLocator(5))
ax5.set_xlim(0, 255)
ax5.tick_params(rotation=45)
ax5.set_xlabel("电影排名", fontsize=12)
ax5.set_ylabel("评价人数", fontsize=12)
ax5.set_yticklabels(())
ax5.legend()
# print(comment_count)
# mp.savefig("3_评分、上映年份、排名、评价人数关系.png")

# i. 对电影类型做词云图
text_type = data["movie_type"].str.split("/").tolist()          # 将获取的电影类型数据做split分割后转为列表
text = "".join(jieba.cut(str(text_type).replace("'", ""), cut_all=False))           # 以空格连接列表并用jieba分词
# print(text)
wc_type = WordCloud(background_color="white", font_path="STXIHEI.TTF", width=900, height=600).generate(text)        # 设置词云图
mp.figure("词云图分析")          # 新建一图
mp.subplot(121)
mp.imshow(wc_type, interpolation="bilinear")            # 绘制热图函数
mp.title("电影类型词云图分析")
mp.axis("off")


# j. 对电影简介作分词处理，并做词云图
text_intro = data["movie_intro"].tolist()
# print(text_intro)
text = "".join(jieba.cut(str(text_intro), cut_all=False))
# print(text)
wc_intro = WordCloud(background_color="white", mode="RGBA", font_path="STXIHEI.TTF", width=1500, height=900).generate(text)
mp.subplot(122)
mp.imshow(wc_intro, interpolation="bilinear")
mp.title("电影简介词频词云分析")
mp.axis("off")
mp.show()
# mp.savefig("4_词云图分析.png")


