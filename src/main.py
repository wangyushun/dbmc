import sys
import time
import logging
# import io


from lxml import etree
import requests
from selenium import webdriver
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import jieba

# sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030')         #改变标准输出的默认编码

class MovieCrawler(object):
    def __init__(self, movie_name=None, *args, **kwargs):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
        self.browser = webdriver.Chrome(executable_path="../drivers/chromedriver_win32/chromedriver.exe")
        self.comments = []
        self.movie_name = movie_name
        return super(MovieCrawler, self).__init__(*args, **kwargs)

    def get_html(self, url=None, encoding=None):
        '''
        获取静态网页数据
        :param url: 网页地址
        :param encoding: 编码方式
        :return: 网页数据字符串
        '''
        if url:
            resp = requests.get(url, headers=self.headers)
            if resp.status_code != 200:
                # print('抓取网页"{0}"失败！'.format(url))
                logger.info('抓取网页"{0}"失败！'.format(url))
                return None
            if encoding:
                resp.encoding = encoding
            html = resp.text
            return html
        return None

    def get_html_by_browser(self, url=None):
        '''
        获取动态网页
        :param url: 网页地址
        :return:
        '''
        if not url:
            return None
        self.browser.get(url)
        html = self.browser.page_source
        return html

    def get_movie_id_by_name(self, name=None):
        if not name:
            name = self.movie_name
        if name:
            search_url = 'https://movie.douban.com/subject_search?search_text=' + name
            html_str = self.get_html_by_browser(search_url)
            if not html_str:
                # print('抓取电影‘{0}’的搜索结果数据失败！'.format(name))
                logger.info('抓取电影‘{0}’的搜索结果数据失败！'.format(name))
                return None
            html = etree.HTML(html_str)
            movie_link_nodes = html.xpath('//*[@id="root"]//div[@class="item-root"]/a[@class="cover-link"]')
            for node in movie_link_nodes:
                movie_link = node.xpath('./@href')
                movie_name = node.xpath('./img/@alt')
                id = ''
                name = ''
                if movie_link:
                    l = movie_link[0].split('/')
                    id = l[-2]
                if movie_name:
                    name = movie_name[0]
                # print('搜索到电影：{0}, id={1}'.format(name, id))
                logger.info('搜索到电影：{0}, id={1}'.format(name, id))
                r = input('是你要查找的电影吗？ yes or no:')
                r.strip()
                if r == 'n' or r == 'no':
                    continue
                if r == 'y' or r == 'yes':
                    return id
            
        return None

    def get_comments(self, movie_id=None):
        if not movie_id:
            return False

        comment_base_url = 'https://movie.douban.com/subject/{0}/comments'.format(movie_id)
        ok, next = self.get_one_page_comments(base_url=comment_base_url, sub_url='?start=0&limit=20&sort=new_score&status=P')
        while(ok and next):
            ok, next = self.get_one_page_comments(base_url=comment_base_url, sub_url=next)

        if ok:
            if not next:
                # print('已抓取所有评论')
                logger.info('已抓取所有评论')
                return True
        else:
            # print('抓取评论出现错误，已停止抓取')
            logger.info('抓取评论出现错误，已停止抓取')
            return  False

    def get_one_page_comments(self, base_url, sub_url=None):
        '''
        获取一页评论
        :param base_url: 电影评论url
        :param sub_url: 评论页参数
        :return: 元组，第一个item指示是否有错误，第二个下一页评论地址
        '''
        error = (False, '')
        url = base_url + sub_url
        # print('正在抓取：',url)
        logger.info('正在抓取：' + url)
        html_str = self.get_html(url)
        # html_str = self.get_html_by_browser(url)
        if not html_str:
            # print('抓取网页数据失败！')
            return error
        html = etree.HTML(html_str)
        comments = html.xpath('//*[@class="comment-item"]')

        for item in comments:
            try:
                c_user = item.xpath('.//*[@class="avatar"]/a/@title')[0]
                c_text = item.xpath('.//*[@class="comment"]//*[@class="short"]/text()')[0]
            except:
                return error
            comment = {}
            comment['username'] = c_user
            comment['text'] = c_text
            self.comments.append(comment)

        #是否还有下一页
        next = html.xpath('//*[@id="paginator"]/a[@class="next"]/@href')
        if next:
            next = next[0]
        if next:
            return (True, next)
        return (True,'')

    def save_to_txt(self):
        with open('{0}.txt'.format(time.strftime('%Y%m%d %H%M%S')), 'a', encoding="utf-8") as f:
            for comment in self.comments:
                username = comment.get('username', '')
                text = comment.get('text', '')
                line = '{0}: {1}\n'.format(username, text)
                # line = username + ': ' + text + '\n'
                f.writelines(line)
def main():
    #从命令行获取电影名，否则输入一个
    args = sys.argv
    if len(args) >= 2:
        movie_name = args[1]
    else:
        movie_name = input('请输入一个电影名：')
        movie_name.strip()
    if not movie_name:
        return
    #抓取数据       
    mc = MovieCrawler(movie_name=movie_name)
    movie_id = mc.get_movie_id_by_name()
    if movie_id:
        if mc.get_comments(movie_id=movie_id):
            # print('任务已完成')
            logger.info('任务已完成')
        # mc.save_to_txt()
        # print('已抓取评论：', mc.comments.__len__())
        logger.info('已抓取评论：{0}'.format(mc.comments.__len__()))
    else:
        # print('任务已停止')
        logger.info('任务已停止')
    mc.browser.close()

    if len(mc.comments) <= 0:
        return
    # 生成词云图
    text = ' '.join([item['text'] for item in mc.comments])
    # 结巴分词，生成字符串，如果不通过分词，无法直接生成正确的中文词云
    cut_text = " ".join(jieba.cut(text))
    wdcloud = WordCloud(
        # 设置字体，不指定就会出现乱码
        font_path='C:\\Windows\\Fonts\\simfang.ttf',  # 不加这一句显示口字形乱码
        # 设置背景色
        background_color='white',
        # 词云形状
        # mask=color_mask,
        # 允许最大词汇
        max_words=2000,
        # 最大号字体
        max_font_size=40
    ).generate(cut_text)

    plt.imshow(wdcloud)
    plt.axis("off")
    plt.show()


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    # 设置logger的level为DEBUG
    logger.setLevel(logging.INFO)

    # 创建一个输出日志到控制台的StreamHandler
    hdr = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s: %(message)s')#'[%(asctime)s] %(name)s:%(levelname)s: %(message)s'
    hdr.setFormatter(formatter)

    # 给logger添加上handler
    logger.addHandler(hdr)

    main()

    

