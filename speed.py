from speedtest import Speedtest
import logging
from Human_Format import human_readable_bytes
from logging_config import logger

def get_speed():
    # imspd = await message.reply("`Running speedtest...`")
    test = Speedtest()
    test.get_best_server()
    test.download()
    test.upload()
    test.results.share()
    result = test.results.dict()
    path = (result['share'])
    string_speed = f'''
__Speedtest Result:-__
Server Name: `{result["server"]["name"]}`
Country: `{result["server"]["country"]}, {result["server"]["cc"]}`
Sponsor: `{result["server"]["sponsor"]}`
Upload: `{human_readable_bytes(result["upload"] / 8)}/s`
Download: `{human_readable_bytes(result["download"] / 8)}/s`
Ping: `{result["ping"]} ms`
ISP: `{result["client"]["isp"]}`
'''
    # imspd.delete()
    # await message.reply(string_speed, parse_mode="markdown")
    logger.error(f'Server Speed result:-\nDL: {human_readable_bytes(result["download"] / 8)}/s UL: {human_readable_bytes(result["upload"] / 8)}/s')
    return string_speed
