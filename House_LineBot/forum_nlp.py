import pandas as pd
from gensim.models import Word2Vec

from tensorflow.python.keras.layers import Embedding
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
import numpy as np

from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense, Dropout, Activation, LSTM
import tensorflow as tf


# def ForumNlp(zone_data):


all_data = pd.read_csv("./no_cut_recovery_all.csv")
model = Word2Vec.load("./model_Word2Vec")



#建立模型設置
embedding_matrix = np.zeros((len(model.wv.vocab.items()) + 1, model.vector_size))
word2idx = {}
PADDING_LENGTH = 500
vocab_list = [(word, model.wv[word]) for word, _ in model.wv.vocab.items()]

for i, vocab in enumerate(vocab_list):
    word, vec = vocab
    embedding_matrix[i + 1] = vec
    word2idx[word] = i + 1

embedding_layer = Embedding(input_dim=embedding_matrix.shape[0],
                            output_dim=embedding_matrix.shape[1],
                            weights=[embedding_matrix],
                            trainable=False)

#### mapping to index
def text_to_index(corpus):
    new_corpus = []
    for doc in corpus:
        new_doc = []
        for word in doc:
            try:
                new_doc.append(word2idx[word])
            except:
                new_doc.append(0)
        new_corpus.append(new_doc)
    return np.array(new_corpus)

def new_model():
    model = Sequential()
    model.add(embedding_layer)
    model.add(LSTM(128, dropout=0.2, recurrent_dropout=0.2))
    model.add(Dense(2, activation='softmax'))
    
    model.compile(optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['accuracy'])
    return model



# 匯入模型
# load model
json_file = open('./lstm.json', 'r')
lstm_loaded_model_json = json_file.read()
lstm = tf.keras.models.model_from_json(lstm_loaded_model_json)
lstm.load_weights('./lstm.h5')


#建立篩選/計算結果
#篩選他
def create_select_data(data,select):
    # select = input()
    select_id = []
    for i in range(0, len(data)):
        if select in data["title"][i] :
            select_id.append(i)
            #print(i, data["title"][i])
    select_data = data.loc[select_id]
    select_data = select_data.reset_index(drop = True)
    
    return select_data

#幫data加上一個預測完的欄位
def preds_data(data):
    #變成 list
    all_text = data["recovery"].tolist()
    
    #預測他
    X_test = text_to_index(all_text)
    X_test = pad_sequences(X_test, maxlen=PADDING_LENGTH)
    Y_preds = lstm.predict(X_test)
    Y_preds_label = np.argmax(Y_preds, axis=1)
    
    data["Y_preds_label"] = Y_preds_label
    
    return data


#產生 group他計算正負項
#這裡的data必須要有Y_preds_label欄位

def create_count_positivedata_negativedata(data):
    group_total = data.groupby("articleID")["Y_preds_label"].count()
    group_positive = data.groupby("articleID")["Y_preds_label"].sum()
    #合併上面兩個項目(上面是serise)
    group = pd.DataFrame({'total':group_total, 'positive_total':group_positive})
    
    group['articleID'] = group.index
    group = group.reset_index(drop = True)
    
    #負面的有幾個
    group["negative_total"] = group["total"] - group["positive_total"]
    
    count_all_data = pd.merge(group,
                        data[['articleID', 'url', 'title', 'createTime', 'type']],
                        on='articleID',how = 'left')
    
    #刪除重複的資料+重製index
    count_all_data = count_all_data.drop_duplicates(subset='articleID', keep='first', inplace=False)
    count_all_data = count_all_data.reset_index(drop = True)
    
    #出現計算趴數欄位
    count_all_data["positive_percent"] = count_all_data["positive_total"] / count_all_data["total"]
    count_all_data["negative_percent"] = count_all_data["negative_total"] / count_all_data["total"]
    
    #排整齊
    count_all_data = count_all_data[['articleID', 'url', 'title', 'createTime', 'type', 'positive_total', 'negative_total', 'total', 'positive_percent', 'negative_percent']]
    overfive = count_all_data[count_all_data["total"] > 3]
    
    return overfive

#產出moblie01 的正面
def top_moblie01_positive(data):
    moblie01_positive = data[data['type'] == 'moblie01']
    moblie01_positive_top = moblie01_positive.nlargest(1,'positive_percent')
    moblie01_positive_url = moblie01_positive_top["url"].to_list()[0]
    moblie01_positive_percent = moblie01_positive_top["positive_percent"].to_list()[0]
    
    return moblie01_positive_url, moblie01_positive_percent

#產出myhousing的正面
def top_myhousing_positive(data):
    myhousing_positive = data[data['type'] == 'myhousing']
    myhousing_positive_top = myhousing_positive.nlargest(1,'positive_percent')
    myhousing_positive_url = myhousing_positive_top["url"].to_list()[0]
    myhousing_positive_percent = myhousing_positive_top["positive_percent"].to_list()[0]
    
    return myhousing_positive_url, myhousing_positive_percent


#產出moblie01 的負面
def top_moblie01_negative(data):
    moblie01_negative = data[data['type'] == 'moblie01']
    moblie01_negative_top = moblie01_negative.nlargest(1,'negative_percent')
    moblie01_negative_url = moblie01_negative_top["url"].to_list()[0]
    moblie01_negative_percent = moblie01_negative_top["negative_percent"].to_list()[0]
    
    return moblie01_negative_url, moblie01_negative_percent

#產出myhousing的負面
def top_myhousing_negative(data):
    myhousing_negative = data[data['type'] == 'myhousing']
    myhousing_negative_top = myhousing_negative.nlargest(1,'negative_percent')
    myhousing_negative_url = myhousing_negative_top["url"].to_list()[0]
    myhousing_negative_percent = myhousing_negative_top["negative_percent"].to_list()[0]
    
    return myhousing_negative_url, myhousing_negative_percent


#一步到底的感覺
def all_step(select):
    data = all_data
    select_data = create_select_data(data,select)
    preds = preds_data(select_data)
    count = create_count_positivedata_negativedata(preds)
    
    top_moblie01_positive_url,top_moblie01_positive_percent = top_moblie01_positive(count)
    # top_moblie01_positive_url = top_moblie01_positive[0]
    # top_moblie01_positive_percent  = top_moblie01_positive[1]
    
    top_myhousing_positive_url,top_myhousing_positive_percent = top_myhousing_positive(count)
    # top_myhousing_positive_url = top_myhousing_positive(count)[0]
    # top_myhousing_positive_percent = top_myhousing_positive(count)[1]
    
    top_moblie01_negative_url,top_moblie01_negative_percent = top_moblie01_negative(count)
    # top_moblie01_negative_url = top_moblie01_negative(count)[0]
    # top_moblie01_negative_percent = top_moblie01_negative(count)[1]
    
    top_myhousing_negative_url, top_myhousing_negative_percent = top_myhousing_negative(count)
    # top_myhousing_negative_url = top_myhousing_negative(count)[0]
    # top_myhousing_negative_percent = top_myhousing_negative(count)[1]
    
    return top_moblie01_positive_url, top_moblie01_positive_percent, top_myhousing_positive_url, top_myhousing_positive_percent, top_moblie01_negative_url, top_moblie01_negative_percent, top_myhousing_negative_url, top_myhousing_negative_percent 


if __name__ == "__main__":     #在被引用時，以下程式碼不被執行 
    #當程式是直接執行時，__name__的值就是__main__；當程式是被引用時，__name__的值即是模組名稱)
    #使用他
    output = all_step()

    print(output)

    print("moblie01 positive url list：" ,output[0])
    print("moblie01 positive percent list：" ,output[1])

    print("========================")

    print("myhousing positive url list：" ,output[2])
    print("myhousing positive percent list：" ,output[3])

    print("========================")

    print("moblie01 negative url list：" ,output[4])
    print("moblie01 negative percent list：" ,output[5])

    print("========================")

    print("myhousing negative url list：" ,output[6])
    print("myhousing negative percent list：" ,output[7])

    output = all_step('大安區')

    print(output)

    print("moblie01 positive url list：" ,output[0])
    print("moblie01 positive percent list：" ,output[1])

    print("========================")

    print("myhousing positive url list：" ,output[2])
    print("myhousing positive percent list：" ,output[3])

    print("========================")

    print("moblie01 negative url list：" ,output[4])
    print("moblie01 negative percent list：" ,output[5])

    print("========================")

    print("myhousing negative url list：" ,output[6])
    print("myhousing negative percent list：" ,output[7])