# encoding = utf8
# import pandas as pd
import csv


# 加载实体词典
def load_entity(dic_path):
    entity_list = []
    max_len = 0
    entity_dict = {}

    """ 实体词典: {'大众点评' : 'FPE', '位置信息' : 'SPT', '使用基于位置提供的服务' : 'OPS', 'IP 地址' : 'SPT'} """
    # df = pd.read_csv(dic_path, header=None, names=["entity", "tag"], encoding='ANSI')
    # entity_dict = {entity.strip(): tag.strip() for entity, tag in df.values.tolist()}

    # """ 计算词典中实体的最大长度 """
    # df["len"] = df["entity"].apply(lambda x: len(x))
    # max_len = max(df["len"])

    reader = csv.reader(open(dic_path))
    for line in reader:
        entity, tag = line
        entity_dict[entity] = tag
        if len(entity) > max_len:
            max_len = len(entity)
    return entity_dict, max_len


class BMM:
    def __init__(self, dic_path):
        self.entity_dict, self.max_len = load_entity(dic_path)

    # 前向最大匹配实体标注
    def positive_maximal_matching(self, sent):
        words_pos_seg = []
        sent_len = len(sent)

        while sent_len > 0:

            """ 如果句子长度小于实体最大长度，则切分的最大长度为句子长度 """
            max_len = min(sent_len, self.max_len)

            """ 从左向右截取max_len个字符，去词典中匹配 """
            sub_sent = sent[:max_len]

            while max_len > 0:
                """ 如果切分的词在实体词典中，那就是切出来的实体 """
                if sub_sent in self.entity_dict:
                    tag = self.entity_dict[sub_sent]
                    words_pos_seg.append((sub_sent, tag))
                    break

                elif max_len == 1:
                    """ 如果没有匹配上，那就把单个字切出来，标签为O """
                    tag = "O"
                    words_pos_seg.append((sub_sent, tag))
                    break

                else:
                    """ 如果没有匹配上，又还没剩最后一个字，就去掉右边的字,继续循环 """
                    max_len -= 1
                    sub_sent = sub_sent[:max_len]

            """ 把分出来的词（实体或单个字）去掉，继续切分剩下的句子 """
            sent = sent[max_len:]
            sent_len -= max_len

        return words_pos_seg

    # 后向最大匹配实体标注
    def reverse_maximal_matching(self, sent):
        words_pos_seg = []
        sent_len = len(sent)

        while sent_len > 0:
            """ 如果句子长度小于实体最大长度，则切分的最大长度为句子长度 """
            max_len = min(sent_len, self.max_len)

            """ 从右向左截取max_len个字符，去词典中匹配 """
            sub_sent = sent[-max_len:]

            while max_len > 0:
                """ 如果切分的词在实体词典中，那就是切出来的实体 """
                if sub_sent in self.entity_dict:
                    tag = self.entity_dict[sub_sent]
                    words_pos_seg.append((sub_sent, tag))
                    break

                elif max_len == 1:
                    """ 如果没有匹配上，那就把单个字切出来，标签为O """
                    tag = "O"
                    words_pos_seg.append((sub_sent, tag))
                    break

                else:
                    """ 如果没有匹配上，又还没剩最后一个字，就去掉右边的字,继续循环 """
                    max_len -= 1
                    sub_sent = sub_sent[-max_len:]

            """ 把分出来的词（实体或单个字）去掉，继续切分剩下的句子 """
            sent = sent[:-max_len]
            sent_len -= max_len

        """ 把切分的结果反转 """
        return words_pos_seg[::-1]

    # 双向最大匹配实体标注
    def bidirectional_maximal_matching(self, sent):

        """ 1: 前向和后向的切分结果 """
        words_psg_fw = self.positive_maximal_matching(sent)
        words_psg_bw = self.reverse_maximal_matching(sent)

        """ 2: 前向和后向的词数 """
        words_fw_size = len(words_psg_fw)
        words_bw_size = len(words_psg_bw)

        """ 3: 前向和后向的词数，则取词数较少的那个 """
        if words_fw_size < words_bw_size: return words_psg_fw

        if words_fw_size > words_bw_size: return words_psg_bw

        """ 4: 结果相同，可返回任意一个 """
        if words_psg_fw == words_psg_bw: return words_psg_fw

        """ 5: 结果不同，返回单字较少的那个 """
        fw_single = sum([1 for i in range(words_fw_size) if len(words_psg_fw[i][0]) == 1])
        bw_single = sum([1 for i in range(words_fw_size) if len(words_psg_bw[i][0]) == 1])

        if fw_single < bw_single:
            return words_psg_fw
        else:
            return words_psg_bw


if __name__ == "__main__":
    dict_path = "privacy_ner_dic.csv"
    text = "设备状态，用于确定设备识别码，以保证账号登录的安全性。拒绝授权后，我行手机银行将不读取设备状态，同时可能需要通过其他方式进行账号登录的安全验证。"
    # fp = open('raw_corpus/金融理财/com.cib.cibmb.txt', 'r', encoding='utf8')
    # text = fp.read()
    # print(text)
    seg = BMM(dict_path)
    words_tags = seg.bidirectional_maximal_matching(text)
    # print(tags)
    for word_tag in words_tags:
        if word_tag[1] != 'O':
            print(word_tag)
