from flask import *
from linebot import *
from linebot.models import *
import sqlite3
import datetime
import requests
import json

app = Flask(__name__)
line_bot_api = LineBotApi(
    'IOWcs1kb0OFgIEOEFFc7NhiqzcKaTh6z+G/SpAqkg/6HpEeKTlbRJ71TqThoLvB4vP1/pKDfkpXm7LZX5z5ssK2s5QCuH3BO44nu3E3JDsYIIVPFKEdhXswaujn//Tj50YI7EoJx5uHhCxUByQNg/QdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('c9c30a060a1a698e55e5c6c7e8aded56')


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/webhook', methods=['POST'])
def hello():
    req = request.get_json(silent=True, force=True)
    intent = req['queryResult']['intent']['displayName']
    id_user = req['originalDetectIntentRequest']['payload']['data']['source']['userId']
    reply_token = req['originalDetectIntentRequest']['payload']['data']['replyToken']
    print(req)
    reply(intent, reply_token, req, id_user)
    return req


def reply(intent, reply_token, req, id_user):
    if intent == 'intent-buy - custom':
        id_item = str(req['queryResult']['outputContexts']
                      [0]['parameters']['id_item.original'])
        number = str(req['queryResult']['outputContexts']
                     [0]['parameters']['number.original'])

        conn = sqlite3.connect('product.db')
        c = conn.cursor()
        c.execute("SELECT * FROM items WHERE id_item == '{}'".format(id_item))
        product = c.fetchall()
        if product == []:
            text_message = TextSendMessage(text='ไม่มีรหัสสินค้านี้')
            line_bot_api.reply_message(reply_token, text_message)
        else:
            confirm_template_message = TemplateSendMessage(
                alt_text='Confirm template',
                template=ConfirmTemplate(
                    text='ต้องการซื้อรหัสสินค้า {} จำนวน {} ใช่หรือไม่'.format(
                        id_item, number),
                    actions=[
                        MessageAction(
                            label='ใช่',
                            text='ซื้อสินค้ารหัส {} จำนวน {}'.format(
                                id_item, number)
                        ),
                        MessageAction(
                            label='ไม่ใช่',
                            text='สั่งซื้อสินค้า'
                        )
                    ]
                )
            )
            line_bot_api.reply_message(reply_token, confirm_template_message)

    if intent == 'intent-buy - custom - yes':
        id_item = str(req['queryResult']['outputContexts']
                      [0]['parameters']['id_item.original'])
        number = str(req['queryResult']['outputContexts']
                     [0]['parameters']['number.original'])
        conn = sqlite3.connect('product.db')
        c = conn.cursor()
        c.execute("SELECT * FROM items WHERE id_item == '{}'".format(id_item))
        product = c.fetchall()
        if int(number) > int(product[0][2]):
            text_message = TextSendMessage(text='จำนวนสินค้าไม่พอ')
            line_bot_api.reply_message(reply_token, text_message)
        else:
            total = int(product[0][2]) - int(number)
            conn = sqlite3.connect('product.db')
            c = conn.cursor()
            c.execute("""Update items set sum = ? WHERE id_item = ?""",
                      (total, id_item))
            conn.commit()

            id = None
            date = datetime.datetime.now()
            conn = sqlite3.connect('product.db')
            c = conn.cursor()
            c.execute("""INSERT INTO oder VALUES(?,?,?,?,?)""",
                      (id, id_user, id_item, number, date))
            conn.commit()
            text_message = TextSendMessage(
                text='บักทึกการสั่งซื้อเรียบร้อยแล้ว')
            line_bot_api.reply_message(reply_token, text_message)

    if intent == 'intent-order':
        conn = sqlite3.connect('product.db')
        c = conn.cursor()
        c.execute("""SELECT * FROM oder WHERE id_user == '{}'""".format(id_user))
        product = c.fetchall()
        if product == []:
            text_message = TextSendMessage(text='คุณยังไม่เคยซื้อสินค้า')
            line_bot_api.reply_message(reply_token, text_message)
        else:
            textlist = ''
            for i in product:
                textstring = 'รหัส {} จำนวน {} เวลา {} \n'.format(
                    i[2], i[3], i[4])
                textlist = textlist + textstring

            text_message = TextSendMessage(text=textlist)
            line_bot_api.reply_message(reply_token, text_message)

    if intent == 'intent-items':
        conn = sqlite3.connect('product.db')
        c = conn.cursor()
        c.execute("""SELECT * FROM items""")
        product = c.fetchall()
        if product == []:
            text_message = TextSendMessage(text='ไม่มีสินค้าสินค้า')
            line_bot_api.reply_message(reply_token, text_message)
        else:
            textlist = ''
            for i in product:
                textstring = 'รหัส {} จำนวน {}\n'.format(i[1], i[2])
                textlist = textlist + textstring

            text_message = TextSendMessage(text=textlist)
            line_bot_api.reply_message(reply_token, text_message)

#     if intent == 'intent-talk':
#         line_bot_api.link_rich_menu_to_user(id_user, 'richmenu-6139854e51bc89df43a328d2e9bfdc34')
#         text_message = TextSendMessage(text='พูดคุยกับเราได้เลย')
#         line_bot_api.reply_message(reply_token, text_message)

#     if intent == 'intent-talk-out':
#         confirm_template_message = TemplateSendMessage(
#             alt_text='Confirm template',
#             template=ConfirmTemplate(
#                 text='ต้องการหยุดการสนทนาหรือไม่',
#                 actions=[
#                     MessageAction(
#                         label='ใช่',
#                         text='ใช่'
#                     ),
#                     MessageAction(
#                         label='ไม่ใช่',
#                         text='พูดคุยทั่วไป'
#                     )
#                 ]
#             )
#         )
#         line_bot_api.reply_message(reply_token, confirm_template_message)

#     if intent == 'intent-talk-out - yes':
#         line_bot_api.unlink_rich_menu_from_user(id_user)

    if intent == 'intent-covid19':
        data = requests.get('https://covid19.ddc.moph.go.th/api/open/today')
        json_data = json.loads(data.text)
        print(json_data)
        Confirmed = json_data['Confirmed']  # ติดเชิ้อสะสม
        Recovered = json_data['Recovered']  # หายแล้ว
        Hospitalized = json_data['Hospitalized']  # รักษาใน รพ
        Deaths = json_data['Deaths']  # เสียชีวิต
        NewConfirmed = json_data['NewConfirmed']
        NewDates = json_data['UpdateDate']  # NewConfirmed

        # text_message = TextSendMessage(text='ยอดติดเชื้อสะสม : {}\nหายแล้ว : {}\nรักษาตัวในโรงพยาบาล : {}\n'
        #                                     'เสียชีวิต : {}\nติดเชื้อเพิ่ม : + {}'.format(Confirmed, Recovered,
        #                                                                                   Hospitalized, Deaths,
        #                                                                                   NewConfirmed))
        flex_message = FlexSendMessage(
            alt_text='hello',
            contents={
                "type": "bubble",
                "size": "giga",
                "hero": {
                     "type": "image",
                        "url": "https://image.makewebeasy.net/makeweb/0/pMrtkmxgt/DefaultData/head_covid19_2.jpg?v=202012190947",
                        "size": "full",
                        "aspectMode": "cover",
                        "aspectRatio": "4.5:1.95",
                        "action": {
                            "type": "uri",
                            "label": "Tel.",
                            "uri": "tel://1111"
                        }
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": str(NewDates),
                            "color": "#f8ed33",
                            "size": "32px",
                            "weight": "bold",
                            "align": "center",
                            "margin": "sm"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {
                                                "type": "box",
                                                "layout": "horizontal",
                                                "contents": [
                                                    {
                                                        "type": "box",
                                                        "layout": "vertical",
                                                        "contents": [
                                                            {
                                                                "type": "text",
                                                                "text": "ผู้ติดเชื้อใหม่",
                                                                "color": "#ffffff",
                                                                "offsetStart": "lg",
                                                                "margin": "md",
                                                                "align": "start",
                                                                "size": "md"
                                                            },
                                                            {
                                                                "type": "text",
                                                                "text": str(NewConfirmed),
                                                                "color": "#ffffff",
                                                                "size": "xxl",
                                                                "align": "center",
                                                                "weight": "bold"
                                                            }
                                                        ],
                                                        "backgroundColor": "#1a75bc"
                                                    },
                                                    {
                                                        "type": "separator",
                                                        "color": "#ffffff"
                                                    },
                                                    {
                                                        "type": "box",
                                                        "layout": "vertical",
                                                        "contents": [
                                                            {
                                                                "type": "text",
                                                                "text": "จากเรือนจำ/ที่ต้องขัง",
                                                                "color": "#ffffff",
                                                                "align": "end",
                                                                "margin": "md",
                                                                "offsetEnd": "lg",
                                                                "size": "md"
                                                            },
                                                            {
                                                                "type": "text",
                                                                "text": "xxx",
                                                                "size": "xxl",
                                                                "color": "#ffffff",
                                                                "weight": "bold",
                                                                "align": "center"
                                                            }
                                                        ],
                                                        "backgroundColor": "#1a75bc"
                                                    }
                                                ]
                                            },
                                            {
                                                "type": "box",
                                                "layout": "vertical",
                                                "contents": [
                                                    {
                                                        "type": "separator",
                                                        "color": "#ffffff"
                                                    },
                                                    {
                                                        "type": "text",
                                                        "text": "รวม" + " " + str(Confirmed) + " " + "ราย",
                                                        "color": "#ffffff",
                                                        "size": "xxl",
                                                        "align": "center",
                                                        "weight": "bold",
                                                        "margin": "sm"
                                                    }
                                                ],
                                                "backgroundColor": "#21618C",
                                                "cornerRadius": "none"
                                            },
                                            {
                                                "type": "box",
                                                "layout": "horizontal",
                                                "contents": [
                                                    {
                                                        "type": "box",
                                                        "layout": "vertical",
                                                        "contents": [
                                                            {
                                                                "type": "text",
                                                                "text": "หายป่วยกลับบ้าน",
                                                                "color": "#ffffff",
                                                                "size": "md",
                                                                "align": "start",
                                                                "offsetStart": "lg",
                                                                "margin": "md"
                                                            },
                                                            {
                                                                "type": "text",
                                                                "text": str(Recovered),
                                                                "color": "#ffffff",
                                                                "size": "xxl",
                                                                "weight": "bold",
                                                                "align": "center"
                                                            },
                                                            {
                                                                "type": "text",
                                                                "text": "ราย",
                                                                "size": "md",
                                                                "color": "#ffffff",
                                                                "align": "end",
                                                                "contents": [],
                                                                "offsetEnd": "xl"
                                                            }
                                                        ],
                                                        "backgroundColor": "#029545"
                                                    },
                                                    {
                                                        "type": "separator",
                                                        "color": "#ffffff"
                                                    },
                                                    {
                                                        "type": "box",
                                                        "layout": "vertical",
                                                        "contents": [
                                                            {
                                                                "type": "text",
                                                                "text": "อยู่โรงพยาบาล",
                                                                "color": "#ffffff",
                                                                "size": "md",
                                                                "align": "end",
                                                                "margin": "md",
                                                                "offsetEnd": "lg"
                                                            },
                                                            {
                                                                "type": "text",
                                                                "text": str(Hospitalized),
                                                                "size": "xxl",
                                                                "color": "#ffffff",
                                                                "weight": "bold",
                                                                "align": "center"
                                                            },
                                                            {
                                                                "type": "text",
                                                                "text": "ราย",
                                                                "color": "#ffffff",
                                                                "align": "end",
                                                                "offsetEnd": "xl"
                                                            }
                                                        ],
                                                        "backgroundColor": "#145A32"
                                                    }
                                                ],
                                                "margin": "sm"
                                            },
                                            {
                                                "type": "box",
                                                "layout": "horizontal",
                                                "contents": [
                                                    {
                                                        "type": "box",
                                                        "layout": "vertical",
                                                        "contents": [
                                                            {
                                                                "type": "text",
                                                                "text": "ผู้ป่วยสะสม",
                                                                "color": "#ffffff",
                                                                "offsetStart": "lg",
                                                                "margin": "md",
                                                                "size": "md",
                                                                "align": "start"
                                                            },
                                                            {
                                                                "type": "text",
                                                                "text": "xxx",
                                                                "color": "#ffffff",
                                                                "weight": "bold",
                                                                "size": "xxl",
                                                                "align": "center"
                                                            },
                                                            {
                                                                "type": "text",
                                                                "text": "ราย",
                                                                "align": "end",
                                                                "color": "#ffffff",
                                                                "offsetEnd": "xl",
                                                                "wrap": True
                                                            }
                                                        ],
                                                        "backgroundColor": "#eb9619"
                                                    },
                                                    {
                                                        "type": "separator",
                                                        "color": "#ffffff"
                                                    },
                                                    {
                                                        "type": "box",
                                                        "layout": "vertical",
                                                        "contents": [
                                                            {
                                                                "type": "text",
                                                                "text": "เสียชีวิต",
                                                                "color": "#ffffff",
                                                                "margin": "md",
                                                                "size": "md",
                                                                "align": "end",
                                                                "offsetEnd": "lg"
                                                            },
                                                            {
                                                                "type": "text",
                                                                "text": str(Deaths),
                                                                "color": "#ffffff",
                                                                "size": "xxl",
                                                                "weight": "bold",
                                                                "align": "center"
                                                            },
                                                            {
                                                                "type": "text",
                                                                "text": "ราย",
                                                                "color": "#ffffff",
                                                                "align": "end",
                                                                "offsetEnd": "xl",
                                                                "wrap": True
                                                            }
                                                        ],
                                                        "backgroundColor": "#424244"
                                                    }
                                                ],
                                                "margin": "sm"
                                            }
                                        ],
                                        "cornerRadius": "xl"
                                    }
                            ],
                            "margin": "md"
                        }
                    ],
                    "position": "relative",
                    "paddingTop": "xs",
                    "margin": "none"
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "ข้อมูลจาก : ศูนย์ข้อมูล COVID-19 กรมประชาสัมพันธ์",
                            "color": "#ffffff",
                            "action": {
                                    "type": "uri",
                                    "label": "โทรสายด่วน",
                                    "uri": "tel://1111"
                            },
                            "size": "xs",
                            "align": "end",
                            "offsetEnd": "lg"
                        },
                        {
                            "type": "text",
                            "text": "อ้างอิง : กระทรวงสาธารณสุข 20 พ.ค.64 07.30 น.",
                            "color": "#ffffff",
                            "align": "end",
                            "offsetEnd": "lg",
                            "size": "xs",
                            "margin": "sm"
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                    {
                                        "type": "image",
                                        "url": "https://image.makewebeasy.net/makeweb/0/pMrtkmxgt/DefaultData/Share3_L.png?v=202012190947",
                                        "size": "full",
                                        "aspectRatio": "200:50",
                                        "aspectMode": "cover",
                                        "action": {
                                            "type": "uri",
                                            "label": "Tel.",
                                            "uri": "tel://1111"
                                        }
                                    },
                                {
                                        "type": "image",
                                        "url": "https://image.makewebeasy.net/makeweb/0/pMrtkmxgt/DefaultData/Share3_R.png?v=202012190947",
                                        "size": "full",
                                        "aspectRatio": "200:50",
                                        "aspectMode": "cover",
                                        "action": {
                                            "type": "uri",
                                            "label": "Share",
                                            "uri": "https://www.google.com"
                                        }
                                        }
                            ],
                            "margin": "lg"
                        }
                    ],
                    "paddingBottom": "none"
                },
                "styles": {
                    "hero": {
                        "backgroundColor": "#142d43"
                    },
                    "body": {
                        "backgroundColor": "#142d43"
                    },
                    "footer": {
                        "backgroundColor": "#142d43"
                    }
                }
            }


        )

        line_bot_api.reply_message(reply_token, flex_message)

        # line_bot_api.reply_message(reply_token, text_message)

    if intent == 'intent-googlesheet':
        data = requests.get(
            'https://script.google.com/macros/s/AKfycbzIz33ShjVNmu-Rva9hHq-cZGM3IyNllzsSIzOLxiGWbj9Bw3xIUsARV05JvEKjZR5P/exec')
        json_data = json.loads(data.text)
        print(json_data)
        Typed = json_data[-1]['type']  # ติดเชิ้อสะสม
        Messaged = json_data[-1]['message']  # หายแล้ว
        Cashed = json_data[-1]['cash']  # รักษาใน รพ
        NoteDateTimed = json_data[-1]['noteDateTime']  # เสียชีวิต
        TransactionDated = json_data[-1]['transactionDate']  # NewConfirmed

        # text_message = TextSendMessage(text='ยอดติดเชื้อสะสม : {}\nหายแล้ว : {}\nรักษาตัวในโรงพยาบาล : {}\n'
        #                                     'เสียชีวิต : {}\nติดเชื้อเพิ่ม : + {}'.format(Confirmed, Recovered,
        #                                                                                   Hospitalized, Deaths,
        #
        #                                                                                    NewConfirmed))
        flex_message = FlexSendMessage(
            alt_text='hello',
            contents={
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_6_carousel.png",
                        "size": "full",
                        "aspectRatio": "20:13",
                        "aspectMode": "cover"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                            {
                                "type": "text",
                                "text": str(Messaged),
                                "weight": "bold",
                                "size": "xl",
                                "wrap": True,
                                "contents": []
                            },
                        {
                                "type": "box",
                                "layout": "baseline",
                                "flex": 1,
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": str(Cashed),
                                        "weight": "bold",
                                        "size": "xl",
                                        "flex": 0,
                                        "wrap": True,
                                        "contents": []
                                    }

                                ]
                                },
                        {
                                "type": "text",
                                "text": str(TransactionDated),
                                "size": "xxs",
                                "color": "#FF5551",
                                "flex": 0,
                                "margin": "md",
                                "wrap": True,
                                "contents": []
                                }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                            {
                                "type": "button",
                                "action": {
                                    "type": "uri",
                                    "label": "Add to Cart",
                                    "uri": "https://linecorp.com"
                                },
                                "flex": 2,
                                "color": "#AAAAAA",
                                "style": "primary"
                            },
                        {
                                "type": "button",
                                "action": {
                                    "type": "uri",
                                    "label": "Add to wish list",
                                    "uri": "https://linecorp.com"
                                }
                                }
                    ]
                }
            }
        )

        line_bot_api.reply_message(reply_token, flex_message)

#     if intent == 'intent-liff':
#         text_message = TextSendMessage(text='https://8242f2ea98bd.ngrok.io')
#         line_bot_api.reply_message(reply_token, text_message)
    if intent == 'intent-Ratexchange':
        data = requests.get('http://localhost:8085/api/v2/stock/product')
        json_data = json.loads(data.text)
        print(json_data)
        # productId = json_data['id']
        productName = json_data[15]['name']
        productPrice = json_data[15]['price']
        # productStock = json_data['stock']
        productCrate = json_data[15]['createdAt']
        # productUpdate = json_data['updatedAt']

        flex_message = FlexSendMessage(
            alt_text='hello',
            contents={
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "url": "https://res.cloudinary.com/satjay/image/upload/v1622351776/my_folder/my_sub_folder/fxjsuccm87fnclrpd5kh.jpg",
                    "size": "full",
                    "aspectRatio": "20:13",
                    "aspectMode": "cover"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "text",
                            "text": str(productName),
                            "weight": "bold",
                            "size": "xl",
                            "wrap": True,
                            "contents": []
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "flex": 1,
                            "contents": [
                                {
                                    "type": "text",
                                    "text": str(productPrice),
                                    "weight": "bold",
                                    "size": "xl",
                                    "flex": 0,
                                    "wrap": True,
                                    "contents": []
                                },

                            ]
                        },
                        {
                            "type": "text",
                            "text": str(productCrate),
                            "size": "xxs",
                            "color": "#FF5551",
                            "flex": 0,
                            "margin": "md",
                            "wrap": True,
                            "contents": []
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "Add to Cart",
                                "uri": "https://linecorp.com"
                            },
                            "flex": 2,
                            "color": "#AAAAAA",
                            "style": "primary"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "Add to wish list",
                                "uri": "https://linecorp.com"
                            }
                        }
                    ]
                }
            }
        )
        line_bot_api.reply_message(reply_token, flex_message)

    if intent == 'intent-flextest':
        flex_message = FlexSendMessage(
            alt_text='hello',
            contents={
                "type": "bubble",
                "size": "giga",
                "hero": {
                        "type": "image",
                        "url": "https://image.makewebeasy.net/makeweb/0/pMrtkmxgt/DefaultData/head_covid19_2.jpg?v=202012190947",
                        "size": "full",
                        "aspectMode": "cover",
                        "aspectRatio": "4.5:1.95",
                        "action": {
                            "type": "uri",
                            "label": "Tel.",
                            "uri": "tel://1111"
                        }
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                            {
                                "type": "text",
                                "text": "20 พฤษภาคม 2564",
                                "color": "#f8ed33",
                                "size": "32px",
                                "weight": "bold",
                                "align": "center",
                                "margin": "sm"
                            },
                        {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {
                                                "type": "box",
                                                "layout": "horizontal",
                                                "contents": [
                                                    {
                                                        "type": "box",
                                                        "layout": "vertical",
                                                        "contents": [
                                                            {
                                                                "type": "text",
                                                                "text": "ผู้ติดเชื้อใหม่",
                                                                "color": "#ffffff",
                                                                "offsetStart": "lg",
                                                                "margin": "md",
                                                                "align": "start",
                                                                "size": "md"
                                                            },
                                                            {
                                                                "type": "text",
                                                                "text": "+1,965 ",
                                                                "color": "#ffffff",
                                                                "size": "xxl",
                                                                "align": "center",
                                                                "weight": "bold"
                                                            }
                                                        ],
                                                        "backgroundColor": "#1a75bc"
                                                    },
                                                    {
                                                        "type": "separator",
                                                        "color": "#ffffff"
                                                    },
                                                    {
                                                        "type": "box",
                                                        "layout": "vertical",
                                                        "contents": [
                                                            {
                                                                "type": "text",
                                                                "text": "จากเรือนจำ/ที่ต้องขัง",
                                                                "color": "#ffffff",
                                                                "align": "end",
                                                                "margin": "md",
                                                                "offsetEnd": "lg",
                                                                "size": "md"
                                                            },
                                                            {
                                                                "type": "text",
                                                                "text": "+671",
                                                                "size": "xxl",
                                                                "color": "#ffffff",
                                                                "weight": "bold",
                                                                "align": "center"
                                                            }
                                                        ],
                                                        "backgroundColor": "#1a75bc"
                                                    }
                                                ]
                                            },
                                            {
                                                "type": "box",
                                                "layout": "vertical",
                                                "contents": [
                                                    {
                                                        "type": "separator",
                                                        "color": "#ffffff"
                                                    },
                                                    {
                                                        "type": "text",
                                                        "text": "รวม   +2,636    ราย",
                                                        "color": "#ffffff",
                                                        "size": "xxl",
                                                        "align": "center",
                                                        "weight": "bold",
                                                        "margin": "sm"
                                                    }
                                                ],
                                                "backgroundColor": "#21618C",
                                                "cornerRadius": "none"
                                            },
                                            {
                                                "type": "box",
                                                "layout": "horizontal",
                                                "contents": [
                                                    {
                                                        "type": "box",
                                                        "layout": "vertical",
                                                        "contents": [
                                                            {
                                                                "type": "text",
                                                                "text": "หายป่วยกลับบ้าน",
                                                                "color": "#ffffff",
                                                                "size": "md",
                                                                "align": "start",
                                                                "offsetStart": "lg",
                                                                "margin": "md"
                                                            },
                                                            {
                                                                "type": "text",
                                                                "text": "+2,268",
                                                                "color": "#ffffff",
                                                                "size": "xxl",
                                                                "weight": "bold",
                                                                "align": "center"
                                                            },
                                                            {
                                                                "type": "text",
                                                                "text": "ราย",
                                                                "size": "md",
                                                                "color": "#ffffff",
                                                                "align": "end",
                                                                "contents": [],
                                                                "offsetEnd": "xl"
                                                            }
                                                        ],
                                                        "backgroundColor": "#029545"
                                                    },
                                                    {
                                                        "type": "separator",
                                                        "color": "#ffffff"
                                                    },
                                                    {
                                                        "type": "box",
                                                        "layout": "vertical",
                                                        "contents": [
                                                            {
                                                                "type": "text",
                                                                "text": "หายป่วยสะสม",
                                                                "color": "#ffffff",
                                                                "size": "md",
                                                                "align": "end",
                                                                "margin": "md",
                                                                "offsetEnd": "lg"
                                                            },
                                                            {
                                                                "type": "text",
                                                                "text": "49,210",
                                                                "size": "xxl",
                                                                "color": "#ffffff",
                                                                "weight": "bold",
                                                                "align": "center"
                                                            },
                                                            {
                                                                "type": "text",
                                                                "text": "ราย",
                                                                "color": "#ffffff",
                                                                "align": "end",
                                                                "offsetEnd": "xl"
                                                            }
                                                        ],
                                                        "backgroundColor": "#145A32"
                                                    }
                                                ],
                                                "margin": "sm"
                                            },
                                            {
                                                "type": "box",
                                                "layout": "horizontal",
                                                "contents": [
                                                    {
                                                        "type": "box",
                                                        "layout": "vertical",
                                                        "contents": [
                                                            {
                                                                "type": "text",
                                                                "text": "ผู้ป่วยสะสม",
                                                                "color": "#ffffff",
                                                                "offsetStart": "lg",
                                                                "margin": "md",
                                                                "size": "md",
                                                                "align": "start"
                                                            },
                                                            {
                                                                "type": "text",
                                                                "text": "90,722",
                                                                "color": "#ffffff",
                                                                "weight": "bold",
                                                                "size": "xxl",
                                                                "align": "center"
                                                            },
                                                            {
                                                                "type": "text",
                                                                "text": "ราย",
                                                                "align": "end",
                                                                "color": "#ffffff",
                                                                "offsetEnd": "xl",
                                                                "wrap": True
                                                            }
                                                        ],
                                                        "backgroundColor": "#eb9619"
                                                    },
                                                    {
                                                        "type": "separator",
                                                        "color": "#ffffff"
                                                    },
                                                    {
                                                        "type": "box",
                                                        "layout": "vertical",
                                                        "contents": [
                                                            {
                                                                "type": "text",
                                                                "text": "เสียชีวิต",
                                                                "color": "#ffffff",
                                                                "margin": "md",
                                                                "size": "md",
                                                                "align": "end",
                                                                "offsetEnd": "lg"
                                                            },
                                                            {
                                                                "type": "text",
                                                                "text": "25",
                                                                "color": "#ffffff",
                                                                "size": "xxl",
                                                                "weight": "bold",
                                                                "align": "center"
                                                            },
                                                            {
                                                                "type": "text",
                                                                "text": "ราย",
                                                                "color": "#ffffff",
                                                                "align": "end",
                                                                "offsetEnd": "xl",
                                                                "wrap": True
                                                            }
                                                        ],
                                                        "backgroundColor": "#424244"
                                                    }
                                                ],
                                                "margin": "sm"
                                            }
                                        ],
                                        "cornerRadius": "xl"
                                    }
                                ],
                                "margin": "md"
                            }
                    ],
                    "position": "relative",
                    "paddingTop": "xs",
                    "margin": "none"
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                            {
                                "type": "text",
                                "text": "ข้อมูลจาก : ศูนย์ข้อมูล COVID-19 กรมประชาสัมพันธ์",
                                "color": "#ffffff",
                                "action": {
                                    "type": "uri",
                                    "label": "โทรสายด่วน",
                                    "uri": "tel://1111"
                                },
                                "size": "xs",
                                "align": "end",
                                "offsetEnd": "lg"
                            },
                        {
                                "type": "text",
                                "text": "อ้างอิง : กระทรวงสาธารณสุข 20 พ.ค.64 07.30 น.",
                                "color": "#ffffff",
                                "align": "end",
                                "offsetEnd": "lg",
                                "size": "xs",
                                "margin": "sm"
                            },
                        {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "image",
                                        "url": "https://image.makewebeasy.net/makeweb/0/pMrtkmxgt/DefaultData/Share3_L.png?v=202012190947",
                                        "size": "full",
                                        "aspectRatio": "200:50",
                                        "aspectMode": "cover",
                                        "action": {
                                            "type": "uri",
                                            "label": "Tel.",
                                            "uri": "tel://1111"
                                        }
                                    },
                                    {
                                        "type": "image",
                                        "url": "https://image.makewebeasy.net/makeweb/0/pMrtkmxgt/DefaultData/Share3_R.png?v=202012190947",
                                        "size": "full",
                                        "aspectRatio": "200:50",
                                        "aspectMode": "cover",
                                        "action": {
                                            "type": "uri",
                                            "label": "Share",
                                            "uri": "https://www.google.com"
                                        }
                                    }
                                ],
                                "margin": "lg"
                            }
                    ],
                    "paddingBottom": "none"
                },
                "styles": {
                    "hero": {
                        "backgroundColor": "#142d43"
                    },
                    "body": {
                        "backgroundColor": "#142d43"
                    },
                    "footer": {
                        "backgroundColor": "#142d43"
                    }
                }
            }


        )
        line_bot_api.reply_message(reply_token, flex_message)

    if intent == 'intent-flextest2':
        carousel_template_message = TemplateSendMessage(
            alt_text='Carousel template',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_6_carousel.png',
                        action=PostbackAction(
                            label='postback1',
                            display_text='postback text1',
                            data='action=buy&itemid=1'
                        )
                    ),
                    ImageCarouselColumn(
                        image_url='https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_6_carousel.png',
                        action=PostbackAction(
                            label='postback2',
                            display_text='postback text2',
                            data='action=buy&itemid=2'
                        )
                    )
                ]
            )
        )
        line_bot_api.reply_message(reply_token, carousel_template_message)

    if intent == 'intent-TempDevice':
        data = requests.get('http://localhost:4000/readdht/1')
        json_data = json.loads(data.text)
        print(json_data)
        tempval = json_data[0]['t']
        humidval = json_data[0]['h']
        recordTimed = json_data[0]['recordTime']
      

        flex_message = FlexSendMessage(
            alt_text='hello',
            contents={
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "url": "https://res.cloudinary.com/satjay/image/upload/v1622565799/my_folder/my_sub_folder/nxt60qlc3ch36aa6v2vy.jpg",
                    "size": "full",
                    "aspectRatio": "20:13",
                    "aspectMode": "cover"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "baseline",
                            "flex": 1,
                            "contents": [
                                   {
                                    "type": "text",
                                    "text": "Temp :    ",
                                    "weight": "bold",
                                    "size": "xl",
                                    "flex": 0,
                                    "wrap": True,
                                    "contents": []
                                },
                                {
                                    "type": "text",
                                    "text": str(tempval),
                                    "weight": "bold",
                                    "size": "xl",
                                    "flex": 0,
                                    "wrap": True,
                                    "contents": []
                                },

                            ]
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "flex": 1,
                            "contents": [
                                   {
                                    "type": "text",
                                    "text": "Humid :    ",
                                    "weight": "bold",
                                    "size": "xl",
                                    "flex": 0,
                                    "wrap": True,
                                    "contents": []
                                },
                                {
                                    "type": "text",
                                    "text": str(humidval),
                                    "weight": "bold",
                                    "size": "xl",
                                    "flex": 0,
                                    "wrap": True,
                                    "contents": []
                                },

                            ]
                        },
                        {
                            "type": "text",
                            "text": str(recordTimed),
                            "size": "xxs",
                            "color": "#005CFC",
                            "flex": 0,
                            "margin": "md",
                            "wrap": True,
                            "contents": []
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "Add to Cart",
                                "uri": "https://linecorp.com"
                            },
                            "flex": 2,
                            "color": "#AAAAAA",
                            "style": "primary"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "Add to wish list",
                                "uri": "https://linecorp.com"
                            }
                        }
                    ]
                }
            }
        )
        line_bot_api.reply_message(reply_token, flex_message)

    if intent == 'intent-durianfarm':
        payload={}
        data = requests.get('http://192.168.1.17:8123/api/states',headers={'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJmMTQ5ZGE2NjZlMmM0NDZjOTQxNGRmYjEwMzNmZTMxNiIsImlhdCI6MTY0MjI0MzYzOCwiZXhwIjoxOTU3NjAzNjM4fQ.m9hUG6vVcjI8A7wamNwSwFYFy_5mKPX8mx3CUibym0Q','Content-Type': 'application/json'},data=payload)
        json_data = json.loads(data.text)
        print(json_data)
        # productId = json_data['id']
        deviceName = json_data[5]['entity_id']
        deviceState = json_data[5]['state']
        # productStock = json_data['stock']
        deviceUpdate = json_data[5]['last_changed']
        # productUpdate = json_data['updatedAt']

        flex_message = FlexSendMessage(
            alt_text='hello',
            contents={
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "url": "https://res.cloudinary.com/satjay/image/upload/v1642248851/my_folder/my_sub_folder/durianFarm.jpg",
                    "size": "full",
                    "aspectRatio": "20:13",
                    "aspectMode": "cover"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "text",
                            "text": str(deviceName),
                            "weight": "bold",
                            "size": "xl",
                            "wrap": True,
                            "contents": []
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "flex": 1,
                            "contents": [
                                {
                                    "type": "text",
                                    "text": str(deviceState),
                                    "weight": "bold",
                                    "size": "xl",
                                    "flex": 0,
                                    "wrap": True,
                                    "contents": []
                                },

                            ]
                        },
                        {
                            "type": "text",
                            "text": str(deviceUpdate),
                            "size": "xxs",
                            "color": "#FF5551",
                            "flex": 0,
                            "margin": "md",
                            "wrap": True,
                            "contents": []
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "รดน้ำ",
                                "uri": "https://linecorp.com"
                            },
                            "flex": 2,
                            "style": "primary"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "สถานะการทำงาน",
                                "uri": "https://linecorp.com"
                            }
                        }
                    ]
                }
            }
        )
        line_bot_api.reply_message(reply_token, flex_message)

    if intent == 'intent-coffeefarm':
        payload={}
        data = requests.get('http://192.168.1.17:8123/api/states',headers={'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJmMTQ5ZGE2NjZlMmM0NDZjOTQxNGRmYjEwMzNmZTMxNiIsImlhdCI6MTY0MjI0MzYzOCwiZXhwIjoxOTU3NjAzNjM4fQ.m9hUG6vVcjI8A7wamNwSwFYFy_5mKPX8mx3CUibym0Q','Content-Type': 'application/json'},data=payload)
        json_data = json.loads(data.text)
        #print(json_data)
        # productId = json_data['id']
        deviceTemp = json_data[4]['attributes']['temperature']
        deviceHumid = json_data[4]['attributes']['humidity']
        deviceLight = json_data[4]['attributes']['wind_bearing']

   
        
    
        flex_message = FlexSendMessage(
            alt_text='hello',
            contents={
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "url": "https://mb.com.ph/wp-content/uploads/2021/07/15021.jpeg",
                    "size": "full",
                    "aspectRatio": "20:13",
                    "aspectMode": "cover"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "baseline",
                            "flex": 1,
                            "contents": [
                                   {
                                    "type": "text",
                                    "text": "อุณหภูมิแปลงกาแฟ :    ",
                                    "weight": "bold",
                                    "size": "xl",
                                    "flex": 0,
                                    "wrap": True,
                                    "contents": []
                                },
                                {
                                    "type": "text",
                                    "text": str(deviceTemp),
                                    "weight": "bold",
                                    "size": "xl",
                                    "flex": 0,
                                    "wrap": True,
                                    "contents": []
                                },

                            ]
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "flex": 1,
                            "contents": [
                                   {
                                    "type": "text",
                                    "text": "ความชื้นแปลงกาแฟ :    ",
                                    "weight": "bold",
                                    "size": "xl",
                                    "flex": 0,
                                    "wrap": True,
                                    "contents": []
                                },
                                {
                                    "type": "text",
                                    "text": str(deviceHumid),
                                    "weight": "bold",
                                    "size": "xl",
                                    "flex": 0,
                                    "wrap": True,
                                    "contents": []
                                },

                            ]
                        },
                        {
                            "type": "text",
                            "text": str(deviceLight),
                            "size": "xxs",
                            "color": "#005CFC",
                            "flex": 0,
                            "margin": "md",
                            "wrap": True,
                            "contents": []
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "รดน้ำ",
                                "uri": "https://linecorp.com"
                            },
                            "flex": 2,
                            "color": "#B78A24FF",
                            "style": "primary"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "สถานะการทำงาน",
                                "uri": "https://linecorp.com"
                            }
                        }
                    ]
                }
            }
        )
        line_bot_api.reply_message(reply_token, flex_message)

if __name__ == '__main__':
    app.run(debug=True)
