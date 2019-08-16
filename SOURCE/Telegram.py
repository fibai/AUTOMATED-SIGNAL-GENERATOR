#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 22:41:09 2019

@author: kenneth
"""


#################################################################################
# MIT License
#
# Copyright (c) 2019 FibAi
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
##################################################################################


import os

#--telegram bot
class telegramBot(object):
    def __init__(self, path):
        self.path = path
        return
    
    def flag(self, code):
        OFFSET = 127462 - ord('A')
        code = code.upper()
        return chr(ord(code[0]) + OFFSET) + chr(ord(code[1]) + OFFSET)
    
    def tgsignal(self, signal):
        '''
        :param:
            signal: dataframe of signals
        '''
        import telegram
        with open(os.path.join(self.path['mainPath'], self.path['telegram'])) as tgt:
            token, chatID= tgt.readlines()
        token = token.strip()
        chatID = chatID.strip()
        bot = telegram.Bot(token = token)
        text = '<b> ✅✅✅✅ AI SIGNAL GENERATOR ✅✅✅✅ </b>\n\n'
        flags = {'AUD_USD': (self.flag('au'), self.flag('us')),
                 'BCO_USD': (self.flag('gb'), self.flag('us')),
                 'BTC_USD': (self.flag('us'), self.flag('us')),
                 'DE30_EUR': (self.flag('de'), self.flag('eu')),
                 'EUR_AUD': (self.flag('eu'), self.flag('au')),
                 'EUR_JPY': (self.flag('eu'), self.flag('jp')),
                 'EUR_USD': (self.flag('eu'), self.flag('us')),
                 'GBP_JPY': (self.flag('gb'), self.flag('jp')),
                 'GBP_USD': (self.flag('gb'), self.flag('us')),
                 'NAS100_USD': (self.flag('us'), self.flag('us')),
                 'SPX500_USD': (self.flag('us'), self.flag('us')),
                 'US30_USD': (self.flag('us'), self.flag('us')),
                 'USD_CAD': (self.flag('us'), self.flag('ca')),
                 'USD_JPY': (self.flag('us'), self.flag('jp')),
                 'XAU_USD': (self.flag('us'), self.flag('us'))}
        for index, sig in signal.iterrows():
            if sig['position'] == 'BUY':
                for ii, ij in flags.items():
                    if sig['pair'] == ii:
                        text += f"<b> {ij[0]}{sig['pair']}{ij[1]}</b>\n\
                                <i>POSITION: 🔵{sig['position']}</i>\n\
                                <i>TIME: 🕖 {sig['time']}</i>\n\
                                <i>@ 🔺{sig['close']}</i>\n\
                                <i>TP1: {sig['tp1']}</i>\n\
                                <i>TP2: {sig['tp2']}</i>\n\
                                <i>TP3: {sig['tp3']}</i>\n\
                                <i>SL: {sig['sl']}</i>\n"
            elif sig['position'] == 'SELL':
                for ii, ij in flags.items():
                    if sig['pair'] == ii:
                        text += f"<b> {ij[0]}{sig['pair']}{ij[1]}</b>\n\
                            <i>POSITION: 🔴{sig['position']}</i>\n\
                            <i>TIME: 🕖 {sig['time']}</i>\n\
                            <i>@ 🔻{sig['close']}</i>\n\
                            <i>TP1: {sig['tp1']}</i>\n\
                            <i>TP2: {sig['tp2']}</i>\n\
                            <i>TP3: {sig['tp3']}</i>\n\
                            <i>SL: {sig['sl']}</i>\n"
            else:
                for ii, ij in flags.items():
                    if sig['pair'] == ii:
                        text += f"<b> {ij[0]}{sig['pair']}{ij[1]}</b>\n\
                                <i>POSITION: ⚫️{sig['position']}</i>\n\
                                <i>TIME: 🕖 {sig['time']}</i>\n\
                                <i>@ {sig['close']}</i>\n"

        return bot.send_message(chat_id=chatID, 
                 text=text, 
                 parse_mode=telegram.ParseMode.HTML)
        
        
if __name__ == '__main__':
    import datetime
    import pandas as pd
    path = {'mainPath': '/home/kenneth/Documents/GIT_PROJECTS/AI-Signal-Generator',
            'acountPath': 'DOCS/account_id.txt',
            'tokenPath': 'DOCS/token.txt',
            'telegram': 'DOCS/telegram.txt',
            'predicted': 'PREDICTED',
            'signals': 'SIGNALS',
            'start': '2019-07-01T00:00:00Z',
            'end': str(datetime.datetime.utcnow().isoformat('T')[:-7] +'Z'),
            'environment': 'practice',
            'strategy': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '11',
                         '22', '33', '44', '55', '66', '77', '88', '99', '111',
                         '222', '333', '444', '555', '666', '777', '888', '999', '1111',
                         '2222', '3333', '4444'],
            'instruments': 'AUD_USD,BCO_USD,BTC_USD,DE30_EUR,EUR_AUD,EUR_JPY,EUR_USD,GBP_JPY,GBP_USD,'+\
                            'NAS100_USD,SPX500_USD,US30_USD,USD_CAD,USD_JPY,XAU_USD',
            'timeframes': ['M15', 'M30', 'H1', 'H2', 'H3', 'H4', 'H6', 'H8',
                           'H12', 'D', 'W']}
    signal = pd.read_csv(os.path.join(path['mainPath'], path['signals']+'/signals.csv')).iloc[:, 1:]
    telegramBot(path).tgsignal(signal)
    
    
    
    