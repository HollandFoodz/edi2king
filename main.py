import datetime
from pydifact.message import Message

message = Message.from_file("order2.edi")

for segment in message.segments:
    print('Segment tag: {}, content: {}'.format(segment.tag, segment.elements))
    if segment.tag == 'DTM':
        value = datetime.datetime.strptime(segment.elements[0][1], "%Y%m%d")