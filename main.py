import json
import re
import sys
import os

def main(type, filepath):
    # 第１引数のConfigを読み込み
    try:
        cfg = Config(type)
    except RuntimeError as err:
        print(err)
        return

    # 第２引数の設定ファイルの読み込み
    try:
        file = open(filepath,'r')
    except FileNotFoundError as err:
        print(f'第２引数に指定したファイル({filepath})が見つかりません。')
        return
    
    # ファイル解析
    record = ''
    while True:
        line = file.readline()
        if line == '':
            break
        elif re.match(cfg.inRecStart, line):
            record = line
        elif len(record) != 0:
            if re.match(cfg.inRecEnd, line):
                record += line
#                print(record)
                items = []
                for item in cfg.inRecInput:
                    result = re.search(item, record, re.MULTILINE)
#                    print(f'{item} - {result}')
                    if result:
                        items.append(result.group(1))
                    else:
                        items.append('')
                for i, output in enumerate(items):
                    print(output)
                record = ''
            else: 
                record += line
    file.close()

class Config:
    def __init__(self, type):
        cfgFile = open('config.json', 'r')
        jsoncfg = json.load(cfgFile)

        cfg = None
        for define in jsoncfg['define']:
            if define['type'] == type:
                cfg = define
                break

        if cfg != None:
            self.inRecStart = define['input']['record-start']
            self.inRecEnd = define['input']['record-end']
            self.inRecInput = define['input']['record-item']
            self.outHeader = define['output']['header']
            self.outRecord = define['output']['record']
        else:
            raise RuntimeError(f'第１引数に指定した設定ファイルの形式({type})が見つかりません。')

args = sys.argv
if __name__ == '__main__':
    if len(args) < 3:
        print('引数が足りません。')
        print('第１引数に設定ファイルの形式を、第２引数に設定ファイルのファイルパスを指定してください。')
        print('ex) python mq /home/user/dmpmqmcfg.def')
    else:
        main(args[1], args[2])