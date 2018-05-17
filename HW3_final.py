# -*- coding: utf-8 -*-
"""
@author: AnaMaria
"""
import nltk
import string
from heapq import nlargest
from nltk.tag import pos_tag
from string import punctuation
from inspect import getsourcefile
from collections import defaultdict
from nltk.tokenize import word_tokenize
from os.path import abspath, join, dirname
from nltk.corpus import wordnet, stopwords
from nltk.tokenize import RegexpTokenizer


"""
Create a list with all the relations of each noun 
"""
def relation_list(nouns):

    relation_list = defaultdict(list)
    
    for k in range (len(nouns)):   
        relation = []
        for syn in wordnet.synsets(nouns[k], pos = wordnet.NOUN):
            for l in syn.lemmas():
                relation.append(l.name())
                if l.antonyms():
                    relation.append(l.antonyms()[0].name())
            for l in syn.hyponyms():
                if l.hyponyms():
                    relation.append(l.hyponyms()[0].name().split('.')[0])
            for l in syn.hypernyms():
                if l.hypernyms():
                    relation.append(l.hypernyms()[0].name().split('.')[0])
        relation_list[nouns[k]].append(relation)
    return relation_list
    


"""
Compute the lexical chain between each noun and their relation and 
apply a threshold of similarity between each word. 
""" 
def create_lexical_chain(nouns, relation_list):
    lexical = []
    threshold = 0.5
    for noun in nouns:
        flag = 0
        for j in range(len(lexical)):
            if flag == 0:
                for key in list(lexical[j]):
                    if key == noun and flag == 0:
                        lexical[j][noun] +=1
                        flag = 1
                    elif key in relation_list[noun][0] and flag == 0:
                        syns1 = wordnet.synsets(key, pos = wordnet.NOUN)
                        syns2 = wordnet.synsets(noun, pos = wordnet.NOUN)
                        if syns1[0].wup_similarity(syns2[0]) >= threshold:
                            lexical[j][noun] = 1
                            flag = 1
                    elif noun in relation_list[key][0] and flag == 0:
                        syns1 = wordnet.synsets(key, pos = wordnet.NOUN)
                        syns2 = wordnet.synsets(noun, pos = wordnet.NOUN)
                        if syns1[0].wup_similarity(syns2[0]) >= threshold:
                            lexical[j][noun] = 1
                            flag = 1
        if flag == 0: 
            dic_nuevo = {}
            dic_nuevo[noun] = 1
            lexical.append(dic_nuevo)
            flag = 1
    return lexical
 

"""
Prune the lexical chain deleting the chains that are more weak with 
just a few words. 
"""       
def prune(lexical):
    final_chain = []
    while lexical:
        result = lexical.pop()
        if len(result.keys()) == 1:
            for value in result.values():
                if value != 1: 
                    final_chain.append(result)
        else:
            final_chain.append(result)
    return final_chain


"""
Class for summarize the text: 
    Input:
        text: The input text that we have read.
        lexical_chain: The final lexical chain with the most important
        n: The number of sentence we want our summary to have. 
    Output:
        summary: the n best sentence.
"""
class Summarizer:
    
    def __init__(self, threshold_min=0.1, threshold_max=0.9):
        self.threshold_min = threshold_min
        self.threshold_max = threshold_max 
        self._stopwords = set(stopwords.words('english') + list(punctuation))
        
        
    """ 
      Compute the frequency of each of word taking into account the 
      lexical chain and the frequency of other words in the same chain. 
      Normalize and filter the frequencies. 
    """
    def return_frequencies(self, words, lexical_chain):
        frequencies = defaultdict(int)
        for word in words:
            for w in word:
                if w not in self._stopwords:
                    flag = 0
                    for i in lexical_chain:
                        if w in list(i.keys()):
                            frequencies[w] = sum(list(i.values()))
                            flag = 1
                            break
                    if flag == 0: 
                        frequencies[w] += 1
        m = float(max(frequencies.values()))
        for w in list(frequencies.keys()):
            frequencies[w] = frequencies[w]/m
            if frequencies[w] >= self.threshold_max or frequencies[w] <= self.threshold_min:
                del frequencies[w]
        return frequencies

    """
      Compute the final summarize using a heap for the most importante 
      sentence and return the n best sentence. 
    """
    def summarize(self, sentence, lexical_chain, n):
        assert n <= len(sentence)
        word_sentence = [word_tokenize(s.lower()) for s in sentence]
        self.frequencies = self.return_frequencies(word_sentence, lexical_chain)
        ranking = defaultdict(int)
        for i,sent in enumerate(word_sentence):
            for word in sent:
                if word in self.frequencies:
                    ranking[i] += self.frequencies[word]
                    idx = self.rank(ranking, n) 
        final_index = sorted(idx)
        return [sentence[j] for j in final_index]

    """
        Create a heap with the best sentence taking into account the 
        frequencie of each word in the sentence and the lexical chain. 
        Return the n best sentence. 
    """
    def rank(self, ranking, n):
        return nlargest(n, ranking, key=ranking.get)



if __name__ == "__main__":
    
    """
    Read the .txt in this folder.
    """
    in_txt = join(dirname(abspath(getsourcefile(lambda:0))) , "input.txt")
    with open(in_txt, "r", encoding="utf-8" ) as f:
        input_txt = f.read() 
        f.close()
        
    """
    Return the nouns of the entire text.
    """
    position = ['NN', 'NNS', 'NNP', 'NNPS']
    
    sentence = nltk.sent_tokenize(input_txt)
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = [tokenizer.tokenize(w) for w in sentence]
    tagged =[pos_tag(tok) for tok in tokens]
    nouns = [word.lower() for i in range(len(tagged)) for word, pos in tagged[i] if pos in position ]
        
    relation = relation_list(nouns)
    lexical = create_lexical_chain(nouns, relation)
    final_chain = prune(lexical)
    """
    Print the lexical chain. 
    """   
    for i in range(len(final_chain)):
        print("Chain "+ str(i+1) + " : " + str(final_chain[i]))
    
    """
    Summarize the text taking into account the lexical chain and the number 
    of sentence we want in the final summary. 
    """      
    if len(sentence) >= 5:
        n = 5
    else: 
        n = 2
    fs = Summarizer()
    for s in fs.summarize(sentence, final_chain, n):
        print(s)