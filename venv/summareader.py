# -*- coding: utf-8 -*-

from re import split
from networkx import Graph
from networkx import pagerank
from itertools import combinations
import urllib.request as urlopen
import ssl
import bs4
import re
from textrankr import TextRank
from collections import Counter
from konlpy.tag import Okt
from newspaper import Article



class Sentence(object):

    okt = Okt()

    def __init__(self, text, index=0):
        self.index = index
        self.text = text.strip()
        self.tokens = self.okt.phrases(self.text)
        self.bow = Counter(self.tokens)

    def __str__(self):
        return self.text

    def __hash__(self):
        return self.index


class TextRank(object):

    def __init__(self, text):
        self.text = text.strip()
        self.build()
        self.stopwords = []


    def build(self):
        self._build_sentences()
        self._build_graph()
        self.pageranks = pagerank(self.graph, weight='weight')
        self.reordered = sorted(self.pageranks, key=self.pageranks.get, reverse=True)

    def _build_sentences(self):
        dup = {}
        candidates = split(r'(?:(?<=[^0-9])\.|\n)', self.text)
        self.sentences = []
        index = 0
        for candidate in candidates:
            while len(candidate) and (candidate[-1] == '.' or candidate[-1] == ' '):
                candidate = candidate.strip(' ').strip('.')
            if len(candidate) and candidate not in dup:
                dup[candidate] = True
                self.sentences.append(Sentence(candidate + '.', index))
                index += 1
        del dup
        del candidates

    def _build_graph(self):
        self.graph = Graph()
        self.graph.add_nodes_from(self.sentences)


        for sent1, sent2 in combinations(self.sentences, 2):
            weight = self._jaccard(sent1, sent2)
            if weight:
                self.graph.add_edge(sent1, sent2, weight=weight)

    def _jaccard(self, sent1, sent2):
        p = sum((sent1.bow & sent2.bow).values())
        q = sum((sent1.bow | sent2.bow).values())
        return p / q if q else 0

    def summarize(self, count=6 , verbose=True):
        results = sorted(self.reordered[:count], key=lambda sentence: sentence.index)
        results = [result.text for result in results]
        if verbose:
            return '\n'.join(results)
        else:
            return results

def summareader():

    url="https://news.naver.com"
    context=ssl._create_unverified_context()

    response=urlopen.urlopen(url, context=context)


    objBS= bs4.BeautifulSoup(response, "html.parser")
    news_item=objBS.find_all("ul",{"class":"section_list_ranking"})

    naverurl=[]
    newstitle=[]
    article=[]

    for nws in news_item:
        txt=nws.find_all("a")
        for we in txt:
            k = "https://news.naver.com"+we.get('href')
            title=we.text.strip()
            naverurl.append(k)
            newstitle.append(title)

    for i in range(len(naverurl)):
        url = naverurl[i]
        context2 = ssl._create_unverified_context()
        response2 = urlopen.urlopen(url, context=context)
        objBS2 = bs4.BeautifulSoup(response2, "html.parser")
       
        newstime = str(objBS2.select('.t11'))
        newstime = re.sub('<.+?>', '', newstime, 0, re.I | re.S)
        newscontent = str(objBS2.find("div", {"class": "_article_body_contents"}))
        newscontent = re.sub('<script.*?>.*?</script>', '', newscontent, 0, re.I | re.S)
        text = re.sub('<.+?>', '', newscontent, 0, re.I | re.S)
        articlecontent = text

        textrank = TextRank(articlecontent)
        suma=textrank.summarize(3)
        article.append(suma)
        print(article[i])
        print("--------------------------------------------------------------------------------------------")
    return newstitle, article
summareader()

