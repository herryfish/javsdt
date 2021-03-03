# -*- coding: utf-8 -*-
from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers=['192.168.66.39:9092'])

producer.send('test', '{"times":3,"index":1,"text":"日本語テスト、得点できないでしょうか？","priority":2}'.encode('UTF-8'), b'voice')
producer.send('test', '{"times":2,"index":1,"text":"レベル高い奴だ","priority":1}'.encode('UTF-8'), b'voice')
producer.close()