# coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..')
from base.spider import Spider
import json
import urllib.parse
import re
from lxml import etree
from urllib.parse import urljoin

class Spider(Spider):
    
    def getName(self):
        return "奇优影院"
    
    def init(self, extend):
        pass
    
    def homeContent(self, filter):
        result = {}
        cateManual = {
            "电影": "1",
            "电视剧": "2", 
            "动漫": "3",
            "综艺": "4",
            "午夜": "6"
        }
        classes = [{'type_name': k, 'type_id': v} for k, v in cateManual.items()]
        result['class'] = classes
        
        filters = {
            "1": [{"key": "by", "name": "排序", "value": [{"n": "按时间", "v": "time"}, {"n": "按人气", "v": "hit"}]}],
            "2": [{"key": "by", "name": "排序", "value": [{"n": "按时间", "v": "time"}, {"n": "按人气", "v": "hit"}]}],
            "3": [{"key": "by", "name": "排序", "value": [{"n": "按时间", "v": "time"}, {"n": "按人气", "v": "hit"}]}],
            "4": [{"key": "by", "name": "排序", "value": [{"n": "按时间", "v": "time"}, {"n": "按人气", "v": "hit"}]}],
            "6": [{"key": "by", "name": "排序", "value": [{"n": "按时间", "v": "time"}, {"n": "按人气", "v": "hit"}]}]
        }
        result['filters'] = filters
        return result
    
    def homeVideoContent(self):
        try:
            rsp = self.fetch("http://qiyoudy5.com/")
            root = self.parse_html(rsp.content)
            if not root:
                return {'list': []}
            
            videos = []
            # 轮播图
            for a in root.xpath("//div[contains(@class,'carousel')]//a[contains(@class,'stui-vodlist__thumb')]"):
                try:
                    name = a.xpath(".//span[@class='pic-text text-center']/text()")[0].strip() if a.xpath(".//span[@class='pic-text text-center']/text()") else a.xpath("./@title")[0] if a.xpath("./@title") else "未知"
                    style = a.xpath("./@style")[0] if a.xpath("./@style") else ""
                    pic = re.search(r"background:\s*url\((.*?)\)", style).group(1) if re.search(r"background:\s*url\((.*?)\)", style) else ""
                    sid = a.xpath("./@href")[0] if a.xpath("./@href") else ""
                    videos.append({"vod_id": sid, "vod_name": name, "vod_pic": pic, "vod_remarks": "推荐"})
                except:
                    continue
            
            # 视频列表
            for a in root.xpath("//ul[contains(@class,'stui-vodlist')]//a[contains(@class,'stui-vodlist__thumb')]"):
                try:
                    name = a.xpath("./@title")[0] if a.xpath("./@title") else "未知"
                    pic = a.xpath("./@data-original")[0] if a.xpath("./@data-original") else ""
                    sid = a.xpath("./@href")[0] if a.xpath("./@href") else ""
                    remark = a.xpath(".//span[@class='pic-text text-right']/text()")[0] if a.xpath(".//span[@class='pic-text text-right']/text()") else ""
                    videos.append({"vod_id": sid, "vod_name": name, "vod_pic": pic, "vod_remarks": remark})
                except:
                    continue
            
            return {'list': videos}
        except:
            return {'list': []}
    
    def categoryContent(self, tid, pg, filter, extend):
        result = {}
        try:
            order = extend.get('by', 'time') if extend else 'time'
            url = f'http://qiyoudy5.com/list/{tid}_{pg}.html?order={order}'
            rsp = self.fetch(url)
            root = self.parse_html(rsp.content)
            
            if not root:
                return {'list': [], 'page': pg, 'pagecount': 1, 'limit': 90, 'total': 0}
            
            videos = []
            for a in root.xpath("//a[contains(@class,'stui-vodlist__thumb')]"):
                try:
                    name = a.xpath("./@title")[0] if a.xpath("./@title") else "未知"
                    pic = a.xpath("./@data-original")[0] if a.xpath("./@data-original") else ""
                    sid = a.xpath("./@href")[0] if a.xpath("./@href") else ""
                    remark = a.xpath(".//span[@class='pic-text text-right']/text()")[0] if a.xpath(".//span[@class='pic-text text-right']/text()") else ""
                    videos.append({"vod_id": sid, "vod_name": name, "vod_pic": pic, "vod_remarks": remark})
                except:
                    continue
            
            current_page = int(root.xpath("//ul[contains(@class,'stui-page')]//a[@class='active']/text()")[0]) if root.xpath("//ul[contains(@class,'stui-page')]//a[@class='active']/text()") else pg
            
            page_numbers = []
            for link in root.xpath("//ul[contains(@class,'stui-page')]//a[contains(@href,'list')]/@href"):
                match = re.search(r'list/\d+_(\d+)\.html', link)
                if match:
                    page_numbers.append(int(match.group(1)))
            total_page = max(page_numbers) if page_numbers else 1
            
            return {
                'list': videos,
                'page': current_page,
                'pagecount': total_page if total_page > 0 else 9999,
                'limit': 90,
                'total': 999999
            }
        except:
            return {'list': [], 'page': pg, 'pagecount': 1, 'limit': 90, 'total': 0}
    
    def detailContent(self, array):
        try:
            tid = array[0]
            url = f'http://qiyoudy5.com{tid}'
            rsp = self.fetch(url)
            root = self.parse_html(rsp.content)
            
            if not root:
                return {'list': []}
            
            # 基本信息
            detail_node = root.xpath("//div[contains(@class,'stui-content__detail')]") or r