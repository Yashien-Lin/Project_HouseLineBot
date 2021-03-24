#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from confluent_kafka import Consumer, KafkaException, KafkaError
import sys
import form_insert_mysql

# 用來接收從Consumer instance發出的error訊息
def error_cb(err):
    print('Error: %s' % err)


# 轉換msgKey或msgValue成為utf-8的字串
def try_decode_utf8(data):
    if data:
        return data.decode('utf-8')
    else:
        return None


# 當發生Re-balance時, 如果有partition被assign時被呼叫
def print_assignment(consumer, partitions):
    result = '[{}]'.format(','.join([p.topic + '-' + str(p.partition) for p in partitions]))
    print('Setting newly assigned partitions:', result)


# 當發生Re-balance時, 之前被assigned的partition會被移除
def print_revoke(consumer, partitions):
    result = '[{}]'.format(','.join([p.topic + '-' + str(p.partition) for p in partitions]))
    print('Revoking previously assigned partitions: ' + result)

# 步驟1.設定要連線到Kafka集群的相關設定
# Consumer configuration
# See https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
# props = {
#     # 'bootstrap.servers': '114.24.22.49:9093',         # Kafka集群在那裡? (置換成要連接的Kafka集群)
#     # 'bootstrap.servers': '192.168.1.120:9092',
#     'bootstrap.servers': 'localhost:9092',
#     # 'group.id': 'teb103',                             # ConsumerGroup的名稱 (置換成你/妳的學員ID)
#     # 'enable.auto.commit': True,
#     # 'auto.offset.reset': 'earliest',               # Offset從最前面開始
#     'error_cb': error_cb                           # 設定接收error訊息的callback函數
# }
props = {
        # 'bootstrap.servers': 'localhost:9092',         # Kafka集群在那裡? (置換成要連接的Kafka集群)
        'bootstrap.servers': 'teb10303.hopto.org:9092',         # Kafka集群在那裡? (置換成要連接的Kafka集群)
        'group.id': 'iiii',                             # ConsumerGroup的名稱 (置換成你/妳的學員ID)
        'auto.offset.reset': 'earliest',               # 是否從這個ConsumerGroup尚未讀取的partition/offset開始讀
        'enable.auto.commit': True,                    # 是否啟動自動commit
        'auto.commit.interval.ms': 5000,               # 自動commit的interval
        # 'on_commit': print_commit_result,              # 設定接收commit訊息的callback函數
        'error_cb': error_cb     
}

def getkafka(fun = None,topicName='member',id='teb103',offset='earliest',commit=True):
    # 步驟2. 產生一個Kafka的Consumer的實例
    # props['group.id']=id
    # props['auto.offset.reset']=offset
    # props['enable.auto.commit']=commit    
    consumer = Consumer(props)
    # 步驟3. 指定想要訂閱訊息的topic名稱
    # topicName = 'ak03.four_partition'
    # topicName = 'test'
    # 步驟4. 讓Consumer向Kafka集群訂閱指定的topic
    consumer.subscribe([topicName], on_assign=print_assignment, on_revoke=print_revoke)

    # 步驟5. 持續的拉取Kafka有進來的訊息
    count=0
    try:
        while True:
            
            if fun != None:
                consumer_method(consumer,fun)
            

    except KeyboardInterrupt as e:
        sys.stderr.write('Aborted by user\n')
    except Exception as e:
        sys.stderr.write(e)

    finally:
        # 步驟6.關掉Consumer實例的連線
        consumer.close()

def consumer_method(cons,fun):
        # 請求Kafka把新的訊息吐出來
    # print(fun('start method'))
    
    records = cons.consume(num_messages=500, timeout=1.0)  # 批次讀取
    
    if records is not None:
        for record in records:
            # 檢查是否有錯誤
            if record is None:
                continue
            if record.error():
                # Error or event
                if record.error().code() == KafkaError._PARTITION_EOF:
                    pass
                    # End of partition event
                    # sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                    #                 (record.topic(), record.partition(), record.offset()))
                    # Error
                else:
                    raise KafkaException(record.error())
            else:
                # ** 在這裡進行商業邏輯與訊息處理 **
                # 取出相關的metadata
                topic = record.topic()
                partition = record.partition()
                offset = record.offset()
                timestamp = record.timestamp()
                # 取出msgKey與msgValue
                msgKey = try_decode_utf8(record.key())
                msgValue = try_decode_utf8(record.value())
                print(msgValue)
                fun(msgValue)
                # 秀出metadata與msgKey & msgValue訊息
                # print('%s-%d-%d : (%s , %s)' % (topic, partition, offset, msgKey, msgValue))

if __name__ == '__main__':
    # print(props)
    consumer = Consumer(props)
    # print(consumer)
    # consumer.subscribe(['member'], on_assign=print_assignment, on_revoke=print_revoke)
    getkafka(form_insert_mysql.form_kafka)