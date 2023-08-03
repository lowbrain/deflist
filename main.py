import json
import re
import sys

#
# main
#
def main(args):
    # 必須引数の読み込み
    try:
        cfg = readcfg('config.json', args[1])
        defFile = open(args[2],'r')
    except FileNotFoundError as err:
        print(f'第２引数に指定したファイル({args[2]})が見つかりません。')
        return
    except RuntimeError as err:
        print(err)
        return

    # 第３引数以降の読み込み
    consts = dict()
    for const in args[3:]:
        result = re.search('^(.+)=(.+)', const)
        if result:
            consts[result.groups(0)[0]] = result.groups(0)[1]
    
    # メインの処理を実行
    extractDefItem(cfg, defFile, consts)
    defFile.close()

#
# configファイルを読み込み指定の形式に該当するjsonを返却
#
def readcfg(cfgFilePath, type):
    cfgFile = open(cfgFilePath, 'r')
    jsoncfg = json.load(cfgFile)
    cfgFile.close()

    cfg = None
    for define in jsoncfg['define']:
        if define['type'] == type:
            cfg = define
            break

    if cfg == None:
        raise RuntimeError(f'指定のtype({type})がconfigファイル({cfgFilePath})に存在しません。')
    
    return cfg

#
# 設定ファイルの値をconfigファイルの定義をもとに抽出
#
def extractDefItem(cfg, defFile, consts):
    print(cfg['output']['header'])
    record = ''
    while True: 
        line = defFile.readline()
        if line == '':
            # ファイルの最終行だったらループを抜ける
            break
        elif re.match(cfg['input']['record-start'], line):
            # 開始レコードを示す文字列を発見したら文字列バッファに文字列を格納
            record = line
        elif len(record) != 0:
            if re.match(cfg['input']['record-end'], line):
                # 終了レコードを示す文字列を発見したらレコードを抽出し出力
                record += line
                items = extractItem(record, cfg, consts)
                print(cfg['output']['record'].format(*tuple(items)))
                record = ''
            else: 
                # 途上レコード文字列であったら文字列バッファに文字列を格納
                record += line

#
# レコードの抽出
#
def extractItem(record, cfg, consts):
    items = []
    for item in cfg['input']['record-item']:
        if re.search('\(.+\)', item):
            # 抽出対象
            result = re.search(item, record, re.MULTILINE)
            if result:
                items.append(result.group(1))
            else:
                items.append('')
        else:
            # 定数
            if item in consts:
                items.append(consts[item])
            else:
                items.append('')
    return items

#
# 
#
args = sys.argv
if __name__ == '__main__':
    if len(args) < 3:
        print(f'Useage: python {args[0]} type filepath [const-value]...')
        print(f'  type:        filepathの形式に基づき\"config.json\"に定義されるtypeの値を指定')
        print(f'  filepath:    読み込む定義ファイルのパスを指定')
        print(f'  const-value: 当プログラムにて扱いたい定数をname=value形式で指定')
        print(f'  ex) python {args[0]} mq /home/user/dmpmqmcfg.def HOSNNAME=myhostname ITEM1=value1')
    else:
        main(args)