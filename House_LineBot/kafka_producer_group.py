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

from confluent_kafka import Producer
import sys
import time


# 用來接收從Consumer instance發出的error訊息
def error_cb(err):
    print('Error: %s' % err)

# 步驟1. 設定要連線到Kafka集群的相關設定
props = {
    # Kafka集群在那裡?
    'bootstrap.servers': 'localhost:9092',          # <-- 置換成要連接的Kafka集群
    # 'bootstrap.servers': '118.166.45.73:9092',          # <-- 置換成要連接的Kafka集群
    # 'bootstrap.servers': '192.168.1.120:9092',  # <-- 置換成要連接的Kafka集群
    'error_cb': error_cb                            # 設定接收error訊息的callback函數
}

# 主程式進入點
def tokafka(msg,topicName='member'):
    # 步驟2. 產生一個Kafka的Producer的實例
    producer = Producer(props)
    
    try:
        print('Start sending messages ...')
        # produce(topic, [value], [key], [partition], [on_delivery], [timestamp], [headers])
        
        producer.produce(topicName, value=msg)
        producer.poll(0)  # <-- (重要) 呼叫poll來讓client程式去檢查內部的Buffer
        
        # print('Send ' + str(msgCount) + ' messages to Kafka')
    except BufferError as e:
        # 錯誤處理
        sys.stderr.write('%% Local producer queue is full ({} messages awaiting delivery): try again\n'
                         .format(len(producer)))
    except Exception as e:
        print(e)
    # 步驟5. 確認所有在Buffer裡的訊息都己經送出去給Kafka了
    producer.flush(10)
    print('Message sending completed!')


if __name__ == '__main__':
    asd = '{"user_id": "U76c63b4ff5cc34277b98097ba8a2ad4f/", "type": ["\u83ef\u5ec8", "\u96fb\u68af\u5927\u6a13", "\u5957\u623f", "\u5225\u5885"], "parking": "yes", "direction": ["\u671d\u5357", "\u671d\u6771\u5317", "\u671d\u6771\u5357", "\u671d\u897f\u5357"], "floor_lower": "3", "floor_upper": "20", "room_lower": "1", "room_upper": "4", "facility": ["\u8fd1\u516c\u5712", "\u8fd1\u5e02\u5834"], "size_lower": "10", "size_upper": "50", "age_lower": "1", "age_upper": "10", "zone": ["\u677e\u5c71\u5340", "\u5167\u6e56\u5340", "\u5357\u6e2f\u5340", "\u4e2d\u5c71\u5340", "\u842c\u83ef\u5340"]}'
    print(asd)
    tokafka(asd)