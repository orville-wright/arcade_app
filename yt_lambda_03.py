#! python3

from arcadepy import Arcade
from arcadepy import AsyncArcade
import asyncio
import dotenv
import json
import os
from pprint import pprint
import random
import re
import time
from typing import Dict, Any

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter

#############################
load_status = dotenv.load_dotenv()

API_KEY = os.getenv("ARCADE_API_KEY")
X_API_KEY = os.getenv("X_API_KEY")
YOUTUBE_USERID = "orville.wrightt@gmail.com"

'''
print (f"Loaded API_KEY:    {API_KEY}" )
print (f"Loaded XAPI_KEY:   {X_API_KEY}" )
print (f"Loaded YT userid:  {YOUTUBE_USERID}\n" )
'''

client = AsyncArcade()

async def main():
    ytt_api = YouTubeTranscriptApi()
    await (yt_search(ytt_api))	# arcade.dev search f CNBC video

#############################
async def yt_search(ytt_api) -> None:
    ytt_api = ytt_api 

    # arcade.dev setup
    _TOOL_NAME = "Youtube.SearchForVideos"
    _tool_input = {
        "keywords": "CNBC Lightning round Jim Cramer",
        "language_code": "en",
        "country_code": "us",
    }
   
    # arcade.dev tool ! : Youtube.SearchForVideos
    response = await client.tools.execute(
        tool_name=_TOOL_NAME,
        input=_tool_input,
        user_id="orville.wrightt@gmail.com"
    )
    out_str = str(response.output)
    pre_split = out_str.split('}, {')     # splt the fill json string into individfual json dicts
    final_list = list()
    
    for ps in pre_split:
        count = 1
        # remove all the YouTube junk
        clean_1 = re.sub(r'Output', "", ps)
        clean_1 = re.sub(r'\(authorization=None', "", clean_1)
        clean_1 = re.sub(r'\, error=None, logs=None, ', "", clean_1)
        clean_1 = re.sub(r'value=', "", clean_1)
        
        pattern = r".*'next_page_token':\s*'[^']*',?\s*\n?"
        clean_1 = re.sub(pattern, "", clean_1)

        clean_1 = re.sub(r'\'videos\'\: ', "", clean_1)
        clean_1 = re.sub(r'\}\]\}\)', "}]", clean_1)
        clean_1 = re.sub(r'\[\{', "{", clean_1)
        clean_1 = re.sub(r'\'\}\]', "'}", clean_1)
        clean_1 = re.sub(r'\}\]', ' }', clean_1)
  
        # wrangle, clean, standardize data as a Valid JSON structre
        json_string = clean_1.replace("'", '"')
        json_string = re.sub(r'\bNone\b', 'null', json_string)
        json_string = re.sub(r'\bTrue\b', 'true', json_string)
        json_string = re.sub(r'\bFalse\b', 'false', json_string)
        
        json_string = re.sub(r': ""', ': "', json_string)
        json_string = re.sub(r'" ', " ", json_string)
        json_string = re.sub(r'\\', "", json_string)

        # fix for strange non-printable chars in id: value sting
        json_string = re.sub(r'"id":.?.?', '"id": "_', json_string)
        
        #punctuation
        json_string = re.sub(r'"s ', "s ", json_string)
        json_string = re.sub(r'"s.', "s ", json_string)
        json_string = re.sub(r'"s', "s ", json_string)
        json_string = re.sub(r'"m', "m", json_string)
        json_string = re.sub(r'"ve', "ve", json_string)
        
        # begin and end JSON package correctly    
        json_string = re.sub(r'"channel:', '{ "channel:', json_string)
        json_string = re.sub(r' }', '" }', json_string)
        json_string = json_string + " }"
        
        final_list.append(json_string)        

    '''
    for _xi, _xv in enumerate(final_list):
        print (f"KEY: {_xi} / VALUE: {_xv}\n")
    ''' 
    #####################################################
    count = 0
    found = len(final_list)-1
    rn = random.randint(0, found)
    for _fl_i, _fl_v in enumerate(final_list):    
        c_fix = re.sub(r'"channel":', '{ "channel":', _fl_v)    # tidy up the root node
        c_fix = re.sub(r'{{ ', '{ ', c_fix)     # tidy up the root node START
        c_fix = re.sub(r'} }', ' }', c_fix)     # tidy up the root node END
        
        #print (f"KEY: {_fl_i} / @: {count} of ({found})\nVALUE: {c_fix}" )
        _fl = json.loads(c_fix)
        data0 = _fl
        print (f"----------------------------------------------")
        print(f"COUNT:          {count} / ({rn}*)" )
        print(f"PUBLISHED:      {data0['published_date']}" )
        print(f"SNIPPET_QUOTE:  {data0['title']}" )
        print(f"STOCK LIST:     {_fl["description"]}" ) 
        print(f"VIDEO_LINK:     {data0['link']}" )
        print(f"VIDEO_ID:       {data0['id']}" )
        print(f"VIDEOS_FOUND:   {found} / working on: {count}" )
        _v = data0['id']
        _v = re.sub(r'^_', '', _v)      # convert safe id element into real id (emove leading "_" )
        print(f"REAL_VIDEO_ID:  {_v}" )
    
        #await yt_get_one(_v)        # arcade.dev tool 2 : Youtube.GetYoutubeVideoDetails
    
        if count == rn:             # randomly print the full transcipt
            #print(f"-------------- {count:02} youtube-python-transcript API  ----------------")
            time.sleep(5)
            # now do JSON formatting...
            '''
            try:
                formatter = JSONFormatter()
                transcript = ytt_api.fetch(_v)      # fropm arcade.dev tool ! : Youtube.SearchForVideos
                json_formatted = formatter.format_transcript(transcript)
                jl = json.loads(json_formatted)
            except Exception as e:
                print (f"Error: jl - json_loads: {e}")
                break
            else:
                conc_trans = ""
                for k, v in enumerate(jl):
                    # print(f"KEY: {k} / VALUE: {v["text"]}" )
                    conc_trans = conc_trans + v["text"] + " "
                    #print(f"KEY: {k} / VALUE: {v["text"]}" )
                print (f"\nTRANSCRIPT:     {conc_trans}\n" )
            '''
            
        count += 1
        print (f" ")

    return

####################################################
# arcade.dev

async def yt_get_one(video_id) -> None:
    TOOL_NAME = "Youtube.GetYoutubeVideoDetails"
    tool_input = {
        "video_id": video_id,
    }

    execute_tool_response = await client.tools.execute(
        tool_name=TOOL_NAME,
        input=tool_input,
        user_id="orville.wrightt@gmail.com"
    )

    #print (f"{execute_tool_response}" )
    return

# ##################################
if __name__ == '__main__':
    asyncio.run(main())
