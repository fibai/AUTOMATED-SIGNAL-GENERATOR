#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 25 02:21:40 2019

@author: kenneth
"""
import time
from STOCK import stock
import os
import requests
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk
from oandapyV20 import API
from mpl_finance import candlestick2_ohlc
from oandapyV20.endpoints.pricing import PricingStream
from threading import Thread
from queue import Queue 
from Automated_Signal_generator import (signalStrategy, Signal,
                                        Run)
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

#%%
#stream live quotes      
class streamer(ttk.Frame):
    def __init__(self, master = None, path = None):
        ttk.Frame.__init__(self, master)
#        self.master = master
        self.path = path
        self.run()
    
    def stream(self):
        try:
            rowDisplaced = 4
            data = pd.read_csv(os.path.join(self.path['mainPath'], "TICKERS/streams.csv")).iloc[:, 1:]
            data.sort_values(['tickers'], inplace = True)
            for enum, (index, row) in enumerate(data.iterrows()):
                if row['direction'] == '^':
                    #--tickers
                    label = tk.Button(self, width = 9, height = 2, \
                                                       text = row['tickers'])
                    label.configure(text= "{}".format(row['tickers']))
                    label.grid(row = enum+rowDisplaced, column =0)
                    #--bids
                    label2 = tk.Button(self, width = 9, height = 2, \
                                                       text = round(row['bids'], 5), bg= "#42f55a")
                    label2.configure(text= "{}".format(round(row['bids'], 5)))
                    label2.grid(row = enum+rowDisplaced, column =1)
                    #--asks
                    label3 = tk.Button(self, width = 9, height = 2, \
                                                       text = round(row['asks'], 5), bg= "#42f55a")
                    label3.configure(text= "{}".format(round(row['asks'], 5)))
                    label3.grid(row = enum+rowDisplaced, column =2)
                    #--direction
                    label4 = tk.Button(self, width = 9, height = 2, \
                                                       text = row['direction'], bg= "#42f55a")
                    label4.configure(text= "{}".format(row['direction']))
                    label4.grid(row = enum+rowDisplaced, column =3)
                elif row['direction'] == 'v':
                    #--tickers
                    label = tk.Button(self, width = 9, height = 2, \
                                                       text = row['tickers'])
                    label.configure(text= "{}".format(row['tickers']))
                    label.grid(row = enum+rowDisplaced, column =0)
                    #--bids
                    label2 = tk.Button(self, width = 9, height = 2, \
                                                       text = round(row['bids'], 5), bg= "#f54242")
                    label2.configure(text= "{}".format(round(row['bids'], 5)))
                    label2.grid(row = enum+rowDisplaced, column =1)
                    #--asks
                    label3 = tk.Button(self, width = 9, height = 2, \
                                                       text = round(row['asks'], 5), bg= "#f54242")
                    label3.configure(text= "{}".format(round(row['asks'], 5)))
                    label3.grid(row = enum+rowDisplaced, column =2)
                    #--direction
                    label4 = tk.Button(self, width = 9, height = 2, \
                                                       text = row['direction'], bg= "#f54242")
                    label4.configure(text= "{}".format(row['direction']))
                    label4.grid(row = enum+rowDisplaced, column =3)
        except:
            pass
        
    def run(self):
        try:
            self.stream()
            self.after(1000, self.run)
        except:
            pass

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
    
#stream and autoupdate signal
class streamSignal(ttk.Frame):
    def __init__(self, master, path):
        ttk.Frame.__init__(self, master)
        self.path = path
        self.frameSettings = ttk.Frame(self, relief=tk.RAISED, borderwidth=1)
        frameGB = ttk.Frame(self.frameSettings)
        style = ttk.Style()
        style.map('TCombobox', fieldbackground=[('readonly','#e3104f')])
        style.map('TCombobox', selectbackground=[('readonly', '#e3104f')])
        style.map('TCombobox', selectforeground=[('readonly', 'white')])
        strategy = tk.Label(frameGB, text = 'Strategy').grid(row = 1, column = 0)
        self.strategyEntry = ttk.Combobox(frameGB, values = self.path['strategy'], state = 'readonly', width = 8)
        self.strategyEntry.current(32)
        self.strategyEntry.focus()
        self.strategyEntry.bind("<<ComboboxSelected>>", self.callback)
        '''Edit Strategy here'''
        self.strategyEntry.grid(row = 1, column = 1, padx = 10, pady = 5)
        deviation = tk.Label(frameGB, text = 'Deviation').grid(row = 2, column = 0, padx = 10, pady = 5)
        self.deviationEntry = tk.Entry(frameGB, width = 10, fg = 'white', bg = '#e3104f')
        self.deviationEntry.insert(tk.END, 2)
        self.deviationEntry.grid(row = 2, column = 1, padx = 10, pady = 5)
        multiplier = tk.Label(frameGB, text = 'Multiplier').grid(row = 3, column = 0, padx = 10, pady = 5)
        self.multiplierEntry = tk.Entry(frameGB, width = 10, fg = 'white', bg = '#e3104f')
        self.multiplierEntry.insert(tk.END, 2)
        self.multiplierEntry.grid(row = 3, column = 1, padx = 10, pady = 5)
        period = tk.Label(frameGB, text = 'Period').grid(row = 4, column = 0, padx = 10, pady = 5)
        self.periodEntry = tk.Entry(frameGB, width = 10, fg = 'white', bg = '#e3104f')
        self.periodEntry.insert(tk.END, 20)
        self.periodEntry.grid(row = 4, column = 1, padx = 10, pady = 5)
        frameGB.grid(row = 1, column = 0, padx = 10, pady = 10)
        #--ATR and RSI
        frameRSI = ttk.Frame(self.frameSettings)
        period_atr = tk.Label(frameRSI, text = 'Period ATR').grid(row = 1, column = 1, padx = 10, pady = 5)
        self.period_atrEntry = tk.Entry(frameRSI, width = 10, fg = 'white', bg = '#e3104f')
        self.period_atrEntry.insert(tk.END, 14)
        self.period_atrEntry.grid(row = 1, column = 2, padx = 10, pady = 5)
        period_alpha = tk.Label(frameRSI, text = 'Period alpha').grid(row = 2, column = 1, padx = 10, pady = 5)
        self.period_alphaE = tk.Entry(frameRSI, width = 10, fg = 'white', bg = '#e3104f')
        self.period_alphaE.insert(tk.END, 10)
        self.period_alphaE.grid(row = 2, column = 2, padx = 10, pady = 5)
        period_beta = tk.Label(frameRSI, text = 'Period beta').grid(row = 3, column = 1, padx = 10, pady = 5)
        self.period_betaE = tk.Entry(frameRSI, width = 10, fg = 'white', bg = '#e3104f')
        self.period_betaE.insert(tk.END, 20)
        self.period_betaE.grid(row = 3, column = 2, padx = 10, pady = 5)
        frameRSI.grid(row = 1, column = 1, padx = 10, pady = 10)

        frameMACD = ttk.Frame(self.frameSettings)
        fast = tk.Label(frameMACD, text = 'Fast').grid(row = 1, column = 2, padx = 10, pady = 5)
        self.fastEntry = tk.Entry(frameMACD, width = 10, fg = 'white', bg = '#e3104f')
        self.fastEntry.insert(tk.END, 12)
        self.fastEntry.grid(row = 1, column = 3, padx = 10, pady = 5)
        slow = tk.Label(frameMACD, text = 'Slow').grid(row = 2, column = 2, padx = 10, pady = 5)
        self.slowEntry = tk.Entry(frameMACD, width = 10, fg = 'white', bg = '#e3104f')
        self.slowEntry.insert(tk.END, 26)
        self.slowEntry.grid(row = 2, column = 3, padx = 10, pady = 5)
        signal = tk.Label(frameMACD, text = 'Signal').grid(row = 3, column = 2, padx = 10, pady = 5)
        self.signalEntry = tk.Entry(frameMACD, width = 10, fg = 'white', bg = '#e3104f')
        self.signalEntry.insert(tk.END, 9)
        self.signalEntry.grid(row = 3, column = 3, padx = 10, pady = 5)
        frameMACD.grid(row = 1, column = 2, padx = 10, pady = 10)

        frameRSI = ttk.Frame(self.frameSettings)
        LB = tk.Label(frameRSI, text = 'Lower bound').grid(row = 1, column = 3, padx = 10, pady = 5)
        self.LBEntry = tk.Entry(frameRSI, width = 10, fg = 'white', bg = '#e3104f')
        self.LBEntry.insert(tk.END, 30)
        self.LBEntry.grid(row = 1, column = 4, padx = 10, pady = 5)
        UB = tk.Label(frameRSI, text = 'Higher bound').grid(row = 2, column = 3, padx = 10, pady = 5)
        self.UBEntry = tk.Entry(frameRSI, width = 10, fg = 'white', bg = '#e3104f')
        self.UBEntry.insert(tk.END, 70)
        self.UBEntry.grid(row = 2, column = 4, padx = 10, pady = 5)
        Midline = tk.Label(frameRSI, text = 'Midline').grid(row = 3, column = 3, padx = 10, pady = 5)
        self.MidlineEntry = tk.Entry(frameRSI, width = 10, fg = 'white', bg = '#e3104f')
        self.MidlineEntry.insert(tk.END, 0)
        self.MidlineEntry.grid(row = 3, column = 4, padx = 10, pady = 5)
        frameRSI.grid(row = 1, column = 4, padx = 10, pady = 10)

        frameTF = ttk.Frame(self.frameSettings)
        timeframe = tk.Label(frameTF, text = 'TimeFrame').grid(row = 1, column = 4)
        self.timeframeEntry = ttk.Combobox(frameTF, values = self.path['timeframes'], width = 8)
        self.timeframeEntry['state'] = 'readonly'
        self.timeframeEntry.current(2)
        self.timeframeEntry.grid(row = 1, column = 5, padx = 10, pady = 5)
        self.timeframeEntry.bind("<<ComboboxSelected>>", self.callback)
        time = tk.Label(frameTF, text = 'Timer').grid(row = 2, column = 4, padx = 10, pady = 5)
        self.timeEntry = ttk.Combobox(frameTF, values = self.path['timeframes'], width = 8)
        self.timeEntry['state'] = 'readonly'
        self.timeEntry.current(1)
        self.timeEntry.grid(row = 2, column = 5, padx = 10, pady = 5)
        self.timeEntry.bind("<<ComboboxSelected>>", self.callback)
        frameTF.grid(row = 1, column = 5, padx = 10, pady = 10)
        #setting frame
        self.frameSettings.grid(row = 0, column = 0)
        
        self.timeframe = timeframe
        return self.runSignal()
    
    #--callback
    def callback(self, eventObject):
        return eventObject.widget.get()
    
    def liveSignal(self):
        '''Docstring
        :params: None
        :Returntype: a list of last signal positions
        '''
        self.pairs = self.path['instruments'].split(',')
        openPositions = []
        for st in self.pairs:
            data = pd.read_csv(os.path.join(self.path['mainPath'], f"{self.path['predicted']}/STRATEGY_{self.strategyEntry.get()}/{self.timeframe}/{st}"+".csv"))
            stockData = stock(data)
            data['ATR'] = stockData.ATR(data, int(self.periodEntry.get()))
            position = data.Position[0]
            time = data.timestamp[0]
            close = data.Close[0]
            atrVal = data.ATR[0]
            for day, pos, cl, atr in zip(data.timestamp.values, data.Position.values, data.Close.values, data.ATR.values):
                if position == pos:
                    pass
                else:
                    position = pos
                    time = day
                    close = cl
                    atrVal = atr
                    if position == 'BUY':
                        if len(str(close).split('.')[0]) > 1:
                            tp1 = round(abs(close + 6*atrVal), 2)
                            tp2 = round(abs(close + 10*atrVal), 2)
                            tp3 = round(abs(close + 15*atrVal), 2)
                            sl = round(abs(close - 2*atrVal), 2)
                        else:
                            tp1 = round(abs(close + 6*atrVal), 5)
                            tp2 = round(abs(close + 10*atrVal), 5)
                            tp3 = round(abs(close + 15*atrVal), 5)
                            sl = round(abs(close - 2*atrVal), 5)
                    elif position == 'SELL':
                        if len(str(close).split('.')[0]) > 1:
                            tp1 = round(abs(close - 6*atrVal), 2)
                            tp2 = round(abs(close - 10*atrVal), 2)
                            tp3 = round(abs(close - 15*atrVal), 2)
                            sl = round(abs(close + 2*atrVal), 2)
                        else:
                            tp1 = round(abs(close - 6*atrVal), 5)
                            tp2 = round(abs(close - 10*atrVal), 5)
                            tp3 = round(abs(close - 15*atrVal), 5)
                            sl = round(abs(close + 2*atrVal), 5)
                    else:
                        if len(str(close).split('.')[0]) > 1:
                            tp1 = round(close, 2)
                            tp2 = round(close, 2)
                            tp3 = round(close, 2)
                            sl = round(close, 2)
                        else:
                            tp1 = round(close, 5)
                            tp2 = round(close, 5)
                            tp3 = round(close, 5)
                            sl = round(close, 5)
            #append result: Store in database & pass to GUI
            openPositions.append([st, position, time, close, tp1, tp2, tp3, sl])
        columns = ['pair', 'position', 'time', 'close', 'tp1', 'tp2', 'tp3', 'sl']
        if not os.path.exists(os.path.join(path['mainPath'], path['signals']+'/signals.csv')):
            signal = pd.DataFrame(openPositions, columns = columns)
            signal.to_csv(os.path.join(path['mainPath'], path['signals']+'/signals.csv'))
            #--Return telegram
            telegramBot(self.path).tgsignal(signal)
        else:
            oldSignal = pd.read_csv(os.path.join(path['mainPath'], path['signals']+'/signals.csv')).iloc[:, 1:]
            newSignal = pd.DataFrame(openPositions, columns = columns)
            if oldSignal['position'].equals(newSignal['position']):
                pass
            else:
                newSignal['update'] = np.where(oldSignal['position'] == newSignal['position'], np.nan, newSignal.position)
                updateSignal = newSignal.dropna().drop(['update'], axis = 1)
                newSignal.drop(['update'], axis = 1, inplace = True)
                newSignal.to_csv(os.path.join(path['mainPath'], path['signals']+'/signals.csv'))
                #--Return telegram
                telegramBot(self.path).tgsignal(updateSignal)
        return openPositions
    
    def signalGUI(self):
        #Run automated signal
        self.strategy = str(self.strategyEntry.get())
        self.pairs = self.path['instruments'].split(',')
        self.dev = int(self.deviationEntry.get())
        self.mul = int(self.multiplierEntry.get())
        self.period = int(self.periodEntry.get())
        self.lwbound = int(self.LBEntry.get())
        self.upbound = int(self.UBEntry.get())
        self.midline = int(self.MidlineEntry.get())
        self.fast = int(self.fastEntry.get())
        self.slow = int(self.slowEntry.get())
        self.signal = int(self.signalEntry.get())
        self.timeframe = str(self.timeframeEntry.get())
        self.palpha = int(self.period_alphaE.get())
        self.pbeta = int(self.period_betaE.get())
        self.periodatr = int(self.period_atrEntry.get())
        #--Run signal
        Run(path = self.path, strategy = self.strategy, STOCKLIST = self.pairs, DEVIATION = self.dev, MULTIPLIER = self.mul, PERIOD = self.period, LOWER_BOUND = self.lwbound,\
            UPPER_BOUND = self.upbound, MIDLINE = self.midline, FAST = self.fast, SLOW = self.slow, SIGNAL = self.signal, TIMEFRAME = self.timeframe,\
            PERIOD_ALPHA = self.palpha, PERIOD_BETA = self.pbeta, PERIODATR = self.periodatr)
        #throw signal
        self.Sigframe = ttk.Frame(self)
        openPositions = self.liveSignal()
        #--return GUI
        rowDisplaced = 6
        for enum, signal in enumerate(openPositions):
            if signal[1] == 'BUY':
                #--buy/sell/EXIT
                #--stock
                butnpair = tk.Button(self.Sigframe, width = 9, height = 2, \
                                                       text = signal[0])
                butnpair.grid(row = enum+rowDisplaced, column =0)
                #--position
                butnPos = tk.Button(self.Sigframe, width = 9, height = 2, \
                                                       text = signal[1], bg= "#42f55a")
                butnPos.configure(text= "{}".format(signal[1]))
                butnPos.grid(row = enum+rowDisplaced, column =1)
                #--datetime
                butnDate = tk.Button(self.Sigframe, width = 20, height = 2, \
                                                       text = signal[2], bg= "#42f55a")
                butnDate.configure(text= "{}".format(signal[2]))
                butnDate.grid(row = enum+rowDisplaced, column =2)
                #--close
                butnClose = tk.Button(self.Sigframe, width = 9, height = 2, \
                                                       text = round(signal[3], 5), bg= "#42f55a")
                butnClose.configure(text= "@{}".format(round(signal[3], 5)))
                butnClose.grid(row = enum+rowDisplaced, column =3)
                #--tp1
                butnTP = tk.Button(self.Sigframe, width = 9, height = 2, \
                                                       text = round(signal[4], 5), bg= "#42f55a")
                butnTP.configure(text= "TP1:{}".format(round(signal[4], 5)))
                butnTP.grid(row = enum+rowDisplaced, column =4)
                #--tp2
                butnTP = tk.Button(self.Sigframe, width = 9, height = 2, \
                                                       text = round(signal[5], 5), bg= "#42f55a")
                butnTP.configure(text= "TP2:{}".format(round(signal[5], 5)))
                butnTP.grid(row = enum+rowDisplaced, column =5)
                #--tp3
                butnTP = tk.Button(self.Sigframe, width = 9, height = 2, \
                                                       text = round(signal[6], 5), bg= "#42f55a")
                butnTP.configure(text= "TP3:{}".format(round(signal[6], 5)))
                butnTP.grid(row = enum+rowDisplaced, column =6)
                #--sl
                butnSL = tk.Button(self.Sigframe, width = 9, height = 2, \
                                                       text = round(signal[7], 5), bg= "#42f55a")
                butnSL.configure(text= "SL:{}".format(round(signal[7], 5)))
                butnSL.grid(row = enum+rowDisplaced, column =7)
                
            elif signal[1] == 'SELL':
                #--stock
                butnpair = tk.Button(self.Sigframe, width = 9, height = 2, \
                                                       text = signal[0])
                butnpair.grid(row = enum+rowDisplaced, column =0)
                #--position
                butnPos = tk.Button(self.Sigframe, width = 9, height = 2, \
                                                       text = signal[1], bg= "#f54242")
                butnPos.configure(text= "{}".format(signal[1]))
                butnPos.grid(row = enum+rowDisplaced, column =1)
                #--datetime
                butnDate = tk.Button(self.Sigframe, width = 20, height = 2, \
                                                       text = signal[2], bg= "#f54242")
                butnDate.configure(text= "{}".format(signal[2]))
                butnDate.grid(row = enum+rowDisplaced, column =2)
                #--close
                butnClose = tk.Button(self.Sigframe, width = 9, height = 2, \
                                                       text = round(signal[3], 5), bg= "#f54242")
                butnClose.configure(text= "@{}".format(round(signal[3], 5)))
                butnClose.grid(row = enum+rowDisplaced, column =3)
                #--tp1
                butnTP = tk.Button(self.Sigframe, width = 9, height = 2, \
                                                       text = round(signal[4], 5), bg= "#f54242")
                butnTP.configure(text= "TP1:{}".format(round(signal[4], 5)))
                butnTP.grid(row = enum+rowDisplaced, column =4)
                #--tp2
                butnTP = tk.Button(self.Sigframe, width = 9, height = 2, \
                                                       text = round(signal[5], 5), bg= "#f54242")
                butnTP.configure(text= "TP2:{}".format(round(signal[5], 5)))
                butnTP.grid(row = enum+rowDisplaced, column =5)
                #--tp3
                butnTP = tk.Button(self.Sigframe, width = 9, height = 2, \
                                                       text = round(signal[6], 5), bg= "#f54242")
                butnTP.configure(text= "TP3:{}".format(round(signal[6], 5)))
                butnTP.grid(row = enum+rowDisplaced, column =6)
                #--sl
                butnSL = tk.Button(self.Sigframe, width = 9, height = 2, \
                                                       text = round(signal[7], 5), bg= "#f54242")
                butnSL.configure(text= "SL:{}".format(round(signal[7], 5)))
                butnSL.grid(row = enum+rowDisplaced, column =7)
            else:
                #--stock
                butnpair = tk.Button(self.Sigframe, width = 9, height = 2, \
                                                       text = signal[0])
                butnpair.grid(row = enum+rowDisplaced, column =0)
                #--position
                butnPos = tk.Button(self.Sigframe, width = 9, height = 2, \
                                                       text = signal[1])
                butnPos.configure(text= "{}".format(signal[1]))
                butnPos.grid(row = enum+rowDisplaced, column =1)
                #--datetime
                butnDate = tk.Button(self.Sigframe, width = 20, height = 2, \
                                                       text = signal[2])
                butnDate.configure(text= "{}".format(signal[2]))
                butnDate.grid(row = enum+rowDisplaced, column =2)
                #--close
                butnClose = tk.Button(self.Sigframe, width = 9, height = 2, \
                                                       text = round(signal[3], 5))
                butnClose.configure(text= "@{}".format(round(signal[3], 5)))
                butnClose.grid(row = enum+rowDisplaced, column =3)
                #--tp1
                butnTP = tk.Button(self.Sigframe, width = 9, height = 2, \
                                                       text = round(signal[4], 5))
                butnTP.configure(text= "TP1:{}".format(round(signal[4], 5)))
                butnTP.grid(row = enum+rowDisplaced, column =4)
                #--tp2
                butnTP = tk.Button(self.Sigframe, width = 9, height = 2, \
                                                       text = round(signal[5], 5))
                butnTP.configure(text= "TP2:{}".format(round(signal[5], 5)))
                butnTP.grid(row = enum+rowDisplaced, column =5)
                #--tp3
                butnTP = tk.Button(self.Sigframe, width = 9, height = 2, \
                                                       text = round(signal[6], 5))
                butnTP.configure(text= "TP3:{}".format(round(signal[6], 5)))
                butnTP.grid(row = enum+rowDisplaced, column =6)
                #--sl
                butnSL = tk.Button(self.Sigframe, width = 9, height = 2, \
                                                       text = round(signal[7], 5))
                butnSL.configure(text= "SL:{}".format(round(signal[7], 5)))
                butnSL.grid(row = enum+rowDisplaced, column =7)
        self.Sigframe.grid(row = 5, column = 0, pady = 5)
    #run auto updates
    def runSignal(self):
        self.timer = str(self.timeEntry.get())
        if self.timer == 'M15':
            self.time = 900000
        elif self.timer == 'M30':
            self.time = 1800000
        elif self.timer == 'H1':
            self.time = 3600000
        elif self.timer == 'H2':
            self.time = 7200000
        elif self.timer == 'H3':
            self.time = 10800000
        elif self.timer == 'H4':
            self.time = 14400000
        elif self.timer == 'H6':
            self.time = 21600000
        elif self.timer == 'H8':
            self.time = 28800000
        elif self.timer == 'H12':
            self.time = 43200000
        elif self.timer == 'D1':
            self.time = 86400000
        else:
            self.time = 900000
        self.signalGUI()
        self.after(self.time, self.runSignal)


#--Quote       
class Quote():
    def __init__(self, path):
        '''Docstring
        params: path: dictionary of mainpath, account path and 
                        token path
        return type: None
        '''
        self.path = path
        self.quoteStreamer()
    
    def accountDetails(self):
        #account -ID
        with open(os.path.join(self.path['mainPath'], self.path['acountPath'])) as acc:
            accountID = acc.readline().strip()
        #token
        with open(os.path.join(self.path['mainPath'], self.path['tokenPath'])) as tok:
            token = tok.readline().strip()
        #account API
        api = API(access_token=token, environment=self.path['environment'])
        return accountID, api
        
    def arrowHead(self, prev, new):
        '''Docstring
        function compares previous bid price with
        new bid and return direction.
        
        :params: prev: previous bid price
        :params: new: new bid price
        :Return type: ^ Up 
                      v Down 
        '''
        if new > prev:
            return '^'
        else:
            return 'v'
     
    def quoteStreamer(self):
        AccID, api = self.accountDetails()
        if not os.path.exists(os.path.join(self.path['mainPath'], 'TICKERS')):
            os.makedirs(os.path.join(self.path['mainPath'], 'TICKERS'))
        try:
            while True:
                n = 0
                s = PricingStream(accountID=AccID, params={"instruments": self.path['instruments']})
                tickers = []
                try:
                    for R in api.request(s):
                        if R['type'] == 'PRICE':
                            rec = {'tickers': R['instrument'], 'bids': R['bids'][0]['price'], 'asks': R['asks'][0]['price'], 'direction': 'v'}
                            if len(tickers)+1 <= len(self.path['instruments'].split(',')):
                                tickers.append(rec)
                            else:
                                for enum, ii in enumerate(tickers):
                                    previous_bid = tickers[enum]['bids']
                                    if tickers[enum]['tickers'] == R['instrument']:
                                        tickers[enum]['bids'] = R['bids'][0]['price']
                                        tickers[enum]['asks'] = R['asks'][0]['price']
                                        tickers[enum]['direction'] = self.arrowHead(previous_bid, tickers[enum]['bids'])
                            df = pd.DataFrame([tic for tic in tickers], columns=['tickers', 'bids', 'asks', 'direction'])
                            df.to_csv(os.path.join(self.path['mainPath'], 'TICKERS/streams.csv'))
                            print(tickers)
                        else:
                            rec = {'tickers': R['instrument'], 'bids': R['bids'][0]['price'], 'asks': R['asks'][0]['price'], 'direction': 'v'}
                            if len(tickers)+1 <= len(self.path['instruments'].split(',')):
                                tickers.append(rec)
                            else:
                                for enum, ii in enumerate(tickers):
                                    previous_bid = tickers[enum]['bids']
                                    if tickers[enum]['tickers'] == R['instrument']:
                                        tickers[enum]['bids'] = R['bids'][0]['price']
                                        tickers[enum]['asks'] = R['asks'][0]['price']
                                        tickers[enum]['direction'] = self.arrowHead(previous_bid, tickers[enum]['bids'])
                            df = pd.DataFrame([x for x in tickers], columns=['tickers', 'bids', 'asks', 'direction'])
                            df.to_csv(os.path.join(self.path['mainPath'], 'TICKERS/streams.csv'))
                            print(tickers)
                except:
                    pass
                n += 1
                try:
                    if n > 10:
                        time.sleep(10)
                except:
                    pass
                continue
        except:
            pass


#--Recommendation
class Returns(ttk.Frame):
    def __init__(self, master, path):
        ttk.Frame.__init__(self, master)
        self.path = path
        self.figsize = (12, 7)
        self.ncol = 8
        optionFrame = ttk.Frame(self)
        style = ttk.Style()
        style.map('TCombobox', fieldbackground=[('readonly','#e3104f')])
        style.map('TCombobox', selectbackground=[('readonly', '#e3104f')])
        style.map('TCombobox', selectforeground=[('readonly', 'white')])
        strategy = tk.Label(optionFrame, text = 'Strategy').grid(row = 1, column = 0)
        self.strategyOption = ttk.Combobox(optionFrame, values = self.path['strategy'], state = 'readonly')
        self.strategyOption.current(32)
        self.strategyOption.focus()
        self.strategyOption.grid(row = 1, column = 1, padx = 20, pady = 10)
        self.strategyOption.bind("<<ComboboxSelected>>", self.callback)
        #timeframe frame
        timframe = tk.Label(optionFrame, text = 'Timeframe').grid(row = 1, column = 2)
        self.timeOption = ttk.Combobox(optionFrame, values = self.path['timeframes'], state = 'readonly')
        self.timeOption.current(2)
        self.timeOption.focus()
        self.timeOption.grid(row = 1, column = 3, padx = 20, pady = 10)
        self.timeOption.bind("<<ComboboxSelected>>", self.callback)
        self.update = tk.Button(optionFrame, text = 'Update', bg = '#a1a09f', command = self.plotReturns).grid(row = 1, column = 4, padx = 20, pady = 10)
        #option frame
        optionFrame.grid(row = 0, column = 0)
        self.plotReturns()
    
    def callback(self, eventObject):
        return eventObject.widget.get() 
    
    def plotReturns(self):
        from collections import Counter
        returnplot = ttk.Frame(self)
        pairs = path['instruments'].split(',')
        grabstrategy = str(self.strategyOption.get())
        grabtimeframe = str(self.timeOption.get())
        Framesort = tk.Frame(self)
        if grabstrategy == str(1):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM, fill = tk.BOTH, expand = True)
        elif grabstrategy == str(2):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(3):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(4):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(5):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(6):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(7):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(8):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(9):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(11):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(22):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(33):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(44):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(55):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(66):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(77):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(88):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(99):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(111):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(222):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(333):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(444):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(555):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(666):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(777):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(888):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(999):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(1111):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(2222):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(3333):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(4444):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(5555):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(6666):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(7777):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(8888):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(9999):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(11111):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(22222):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(33333):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(44444):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        elif grabstrategy == str(55555):
            returns = pd.DataFrame()
            maximum = {}
            highestReturns = []
            for stockPair in pairs:
                data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{grabstrategy}/{grabtimeframe}/{stockPair}"+'.csv'))
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                data = data[data.Position != 'EXIT']
                data['signal'] = np.where(data.Position == 'BUY', 1, 0)
                data['return'] = np.log(data.Close/data.Close.shift(1))
                data['return'] = data['return'] * data.signal.shift(1)
                returns['{}'.format(stockPair)] = np.cumsum(data['return'])
            for ii in returns.columns:
                maximum[ii] = np.mean(returns[ii])
                maximum = Counter(maximum)
            for tradethis in maximum.most_common(5):
                highestReturns.append(tradethis[0])
            label = tk.Button(Framesort, text = 'HIGHEST RETURNS (TOP 5 IN DESCENDING ORDER)', bg = '#42f55a').grid(row = 3, column = 0, padx = 10)
            for enum, ii in enumerate(highestReturns):
                returnCommons = tk.Button(Framesort, bg = '#42f55a')
                returnCommons.configure(text = f'{enum+1}. {ii}')
                returnCommons.grid(row = 3, column = enum+3)
            Framesort.grid(row = 2, column = 0)
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            for ii in returns.columns:
                subplots.plot(np.arange(len(returns)), returns[ii])
            subplots.legend(bbox_to_anchor=(0, 1.01, 1, .102), loc=3, ncol = self.ncol, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, returnplot)
            canvas.draw()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, returnplot)
            toolbar.update()
            canvas.get_tk_widget().pack(side = tk.BOTTOM,fill = tk.BOTH, expand = True)
        else:
            return None
        returnplot.grid(row = 1, column = 0)

#--signal visualization    
class visu(ttk.Frame):
    def __init__(self, master, path):
        ttk.Frame.__init__(self, master)
        self.path = path
        self.figsize = (12, 7)
        optionFrame = ttk.Frame(self)
        style = ttk.Style()
        name = tk.Label(optionFrame, text = 'Pairs')
        name.grid(row = 1, column = 0)
        style.map('TCombobox', fieldbackground=[('readonly','#e3104f')])
        style.map('TCombobox', selectbackground=[('readonly', '#e3104f')])
        style.map('TCombobox', selectforeground=[('readonly', 'white')])
        self.pairs = ttk.Combobox(optionFrame, values = self.path['instruments'].split(','), state = 'readonly')
        self.pairs.current(2)
        self.pairs.focus()
        self.pairs.grid(row = 1, column = 1, padx = 20, pady = 10)
        self.pairs.bind("<<ComboboxSelected>>", self.callback)
        strategy = tk.Label(optionFrame, text = 'Strategy').grid(row = 1, column = 2)
        self.strategyOption = ttk.Combobox(optionFrame, values = self.path['strategy'], state = 'readonly')
        self.strategyOption.current(32)
        self.strategyOption.focus()
        self.strategyOption.bind("<<ComboboxSelected>>", self.callback)
        self.strategyOption.grid(row = 1, column = 3, padx = 20, pady = 10)
        #timeframe frame
        timframe = tk.Label(optionFrame, text = 'Timeframe').grid(row = 1, column = 4)
        self.timeOption = ttk.Combobox(optionFrame, values = self.path['timeframes'], state = 'readonly')
        self.timeOption.current(2)
        self.timeOption.focus()
        self.timeOption.bind("<<ComboboxSelected>>", self.callback)
        self.timeOption.grid(row = 1, column = 5, padx = 20, pady = 10)
        self.update = tk.Button(optionFrame, text = 'Update', bg = '#a1a09f', command = self.plots).grid(row = 1, column = 6)
        #option frame
        optionFrame.grid(row = 0, column = 0)
        self.plots()
        
    def callback(self, eventObject):
        return eventObject.widget.get()
    
    def multiIndicatorSignal(self, df):
        positions = np.array(df.Position)
        signal = np.zeros_like(positions)
        initialPosition = positions[0]
        for ii, pos in enumerate(positions):
            if pos == initialPosition:
                pass
            else:
                initialPosition = pos
                if initialPosition == 'BUY':
                    signal[ii] = 1
                elif initialPosition == 'SELL':
                    signal[ii] = -1
                else:
                    signal[ii] = 2
        df['viewSignal'] = list(signal)
        return df

    def plots(self):
        frameplot = ttk.Frame(self)
        grabpair = str(self.pairs.get())
        grabstrategy = str(self.strategyOption.get())
        grabtimeframe = str(self.timeOption.get())
        data = pd.read_csv(os.path.join(path['mainPath'], f"{path['predicted']}/STRATEGY_{self.strategyOption.get()}/{grabtimeframe}/{grabpair}"+'.csv'))
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        data.dropna(inplace = True)
        candlewidth = 1
        markersize = 7
        #--MA plot
        if grabstrategy == str(1):
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            try:
                columns = [x for x in data.columns if x[:3] == 'EMA']
            except:
                columns = [x for x in data.columns if x[:3] == 'SMA']
            data['viewSignal'] = data.signal.diff()
            candlestick2_ohlc(subplots, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            subplots.plot(np.arange(len(data)), data[columns[0]])
            subplots.plot(np.arange(len(data)), data[columns[1]])
            subplots.plot(data.loc[data.viewSignal == -1.0].index, data[columns[0]][data.viewSignal == -1], 'v', color = 'r', markersize = markersize)
            subplots.plot(data.loc[data.viewSignal == 1.0].index, data[columns[1]][data.viewSignal == 1], '^', color = 'g', markersize = markersize)
            subplots.legend(bbox_to_anchor=(0, 1.02, 1, .102), loc=3, ncol=5, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        #--Bollinger plot
        elif grabstrategy == str(2):
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            data['viewSignal'] = data.signal.diff()
            candlestick2_ohlc(subplots, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            subplots.plot(np.arange(len(data)), data.bollinger_band, LW = 1.)
            subplots.plot(np.arange(len(data)), data.Upper_band, LW = 1.)
            subplots.plot(np.arange(len(data)), data.Lower_band, LW = 1.)
            subplots.plot(data.loc[data.viewSignal == -1.0].index, data[['bollinger_band']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            subplots.plot(data.loc[data.viewSignal == 1.0].index, data[['bollinger_band']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            subplots.legend(bbox_to_anchor=(0, 1.02, 1, .102), loc=3, ncol=5, borderaxespad=0)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        #--MACD plot
        elif grabstrategy == str(3):
            fig = Figure(figsize=self.figsize, dpi = 100)
            ax1, ax2 = fig.subplots(2, 1, sharex = True, gridspec_kw={'height_ratios': [4, 1], 'wspace': 0, 'hspace': 0})
            data['viewSignal'] = data.signal.diff()
            candlestick2_ohlc(ax1, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            ax1.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            ax1.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            ax2.plot(np.arange(len(data)), data.MACD, LW = 1.)
            ax2.plot(np.arange(len(data)), data.MACD_HIST, LW = 1.)
            ax2.plot(np.arange(len(data)), data.MACD_SIGNAL, LW = 1.)
            ax2.fill_between(data.index, data.MACD_HIST, 0, where=(data.MACD_HIST >= 0), facecolor='#0fff97')
            ax2.fill_between(data.index, data.MACD_HIST, 0, where=(data.MACD_HIST <= 0), facecolor='#ff400f')
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        #--RSI plot
        elif grabstrategy == str(4):
            fig = Figure(figsize=self.figsize, dpi = 100)
            ax1, ax2 = fig.subplots(2, 1, sharex = True, gridspec_kw={'height_ratios': [4, 1], 'wspace': 0, 'hspace': 0})
            data['viewSignal'] = data.signal.diff()
            candlestick2_ohlc(ax1, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            ax1.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            ax1.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            ax2.plot(np.arange(len(data)), data.RSI, LW = 1.)
            ax2.fill_between(data.index, y1=30, y2=70, color='#7eebed', alpha='0.3')
            ax2.legend(loc = 1)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        #--SUper Trend plot
        elif grabstrategy == str(5):
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            data['viewSignal'] = data.signal.diff()
            candlestick2_ohlc(subplots, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            subplots.plot(np.arange(len(data)), data.SuperTrend, LW = 1.)
            subplots.plot(data.loc[data.viewSignal == -1.0].index, data[['SuperTrend']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            subplots.plot(data.loc[data.viewSignal == 1.0].index, data[['SuperTrend']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        #--MA vs SUPER_TREND--
        elif grabstrategy == str(6):
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            data = self.multiIndicatorSignal(data)
            candlestick2_ohlc(subplots, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            subplots.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            subplots.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            subplots.plot(data.loc[data.viewSignal == 2.0].index, data[['Close']][data.viewSignal == 2], 'o', markersize = markersize, color = '#181c1c')
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        #-- MA vs MACD ----
        elif grabstrategy == str(7):
            fig = Figure(figsize=self.figsize, dpi = 100)
            ax1, ax2 = fig.subplots(2, 1, sharex = True, gridspec_kw={'height_ratios': [4, 1], 'wspace': 0, 'hspace': 0})
            data = self.multiIndicatorSignal(data)
            candlestick2_ohlc(ax1, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            ax1.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            ax1.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            ax1.plot(data.loc[data.viewSignal == 2.0].index, data[['Close']][data.viewSignal == 2], 'o', markersize = markersize, color = '#181c1c')
            ax2.plot(np.arange(len(data)), data.MACD, LW = 1.)
            ax2.plot(np.arange(len(data)), data.MACD_HIST, LW = 1.)
            ax2.plot(np.arange(len(data)), data.MACD_SIGNAL, LW = 1.)
            ax2.fill_between(data.index, data.MACD_HIST, 0, where=(data.MACD_HIST >= 0), facecolor='#0fff97')
            ax2.fill_between(data.index, data.MACD_HIST, 0, where=(data.MACD_HIST <= 0), facecolor='#ff400f')
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        #--MA vs RSI--
        elif grabstrategy == str(8):
            fig = Figure(figsize=self.figsize, dpi = 100)
            ax1, ax2 = fig.subplots(2, 1, sharex = True, gridspec_kw={'height_ratios': [4, 1], 'wspace': 0, 'hspace': 0})
            data = self.multiIndicatorSignal(data)
            candlestick2_ohlc(ax1, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            ax1.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            ax1.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            ax1.plot(data.loc[data.viewSignal == 2.0].index, data[['Close']][data.viewSignal == 2], 'o', markersize = markersize, color = '#181c1c')
            ax2.plot(np.arange(len(data)), data.RSI, LW = 1.)
            ax2.fill_between(data.index, y1=30, y2=70, color='#7eebed', alpha='0.3')
            ax2.legend(loc = 1)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        #--- MA vs BOLLINGER BAND ---
        elif grabstrategy == str(9):
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            data = self.multiIndicatorSignal(data)
            candlestick2_ohlc(subplots, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            subplots.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            subplots.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            subplots.plot(data.loc[data.viewSignal == 2.0].index, data[['Close']][data.viewSignal == 2], 'o', markersize = markersize, color = '#181c1c')
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        #-- BOLLINGER BAND vs MACD
        elif grabstrategy == str(11):
            fig = Figure(figsize=self.figsize, dpi = 100)
            ax1, ax2 = fig.subplots(2, 1, sharex = True, gridspec_kw={'height_ratios': [4, 1], 'wspace': 0, 'hspace': 0})
            data = self.multiIndicatorSignal(data)
            candlestick2_ohlc(ax1, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            ax1.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            ax1.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            ax1.plot(data.loc[data.viewSignal == 2.0].index, data[['Close']][data.viewSignal == 2], 'o', markersize = markersize, color = '#181c1c')
            ax2.plot(np.arange(len(data)), data.MACD, LW = 1.)
            ax2.plot(np.arange(len(data)), data.MACD_HIST, LW = 1.)
            ax2.plot(np.arange(len(data)), data.MACD_SIGNAL, LW = 1.)
            ax2.fill_between(data.index, data.MACD_HIST, 0, where=(data.MACD_HIST >= 0), facecolor='#0fff97')
            ax2.fill_between(data.index, data.MACD_HIST, 0, where=(data.MACD_HIST <= 0), facecolor='#ff400f')
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        #--BOLLINGER BAND vs RSI--
        elif grabstrategy == str(22):
            fig = Figure(figsize=self.figsize, dpi = 100)
            ax1, ax2 = fig.subplots(2, 1, sharex = True, gridspec_kw={'height_ratios': [4, 1], 'wspace': 0, 'hspace': 0})
            data = self.multiIndicatorSignal(data)
            candlestick2_ohlc(ax1, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            ax1.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            ax1.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            ax1.plot(data.loc[data.viewSignal == 2.0].index, data[['Close']][data.viewSignal == 2], 'o', markersize = markersize, color = '#181c1c')
            ax2.plot(np.arange(len(data)), data.RSI, LW = 1.)
            ax2.fill_between(data.index, y1=30, y2=70, color='#7eebed', alpha='0.3')
            ax2.legend(loc = 1)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        #--BOLLINGER vs SUPERTREND --
        elif grabstrategy == str(33):
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            data = self.multiIndicatorSignal(data)
            candlestick2_ohlc(subplots, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            subplots.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            subplots.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            subplots.plot(data.loc[data.viewSignal == 2.0].index, data[['Close']][data.viewSignal == 2], 'o', markersize = markersize, color = '#181c1c')
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            fig.set_tight_layout(True)
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        #--RSI vs SUPER TREND --
        elif grabstrategy == str(44):
            fig = Figure(figsize=self.figsize, dpi = 100)
            ax1, ax2 = fig.subplots(2, 1, sharex = True, gridspec_kw={'height_ratios': [4, 1], 'wspace': 0, 'hspace': 0})
            data = self.multiIndicatorSignal(data)
            candlestick2_ohlc(ax1, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            ax1.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            ax1.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            ax1.plot(data.loc[data.viewSignal == 2.0].index, data[['Close']][data.viewSignal == 2], 'o', markersize = markersize, color = '#181c1c')
            ax2.plot(np.arange(len(data)), data.RSI, LW = 1.)
            ax2.fill_between(data.index, y1=30, y2=70, color='#7eebed', alpha='0.3')
            ax2.legend(loc = 1)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        #--MOVING AVERAGE vs BOLLINGER BAND vs MACD --
        elif grabstrategy == str(55):
            fig = Figure(figsize=self.figsize, dpi = 100)
            ax1, ax2 = fig.subplots(2, 1, sharex = True, gridspec_kw={'height_ratios': [4, 1], 'wspace': 0, 'hspace': 0})
            data = self.multiIndicatorSignal(data)
            candlestick2_ohlc(ax1, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            ax1.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            ax1.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            ax1.plot(data.loc[data.viewSignal == 2.0].index, data[['Close']][data.viewSignal == 2], 'o', markersize = markersize, color = '#181c1c')
            ax2.plot(np.arange(len(data)), data.MACD, LW = 1.)
            ax2.plot(np.arange(len(data)), data.MACD_HIST, LW = 1.)
            ax2.plot(np.arange(len(data)), data.MACD_SIGNAL, LW = 1.)
            ax2.fill_between(data.index, data.MACD_HIST, 0, where=(data.MACD_HIST >= 0), facecolor='#0fff97')
            ax2.fill_between(data.index, data.MACD_HIST, 0, where=(data.MACD_HIST <= 0), facecolor='#ff400f')
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        #--MOVING AVERAGE vs BOLLINGER BAND vs RSI --
        elif grabstrategy == str(66):
            fig = Figure(figsize=self.figsize, dpi = 100)
            ax1, ax2 = fig.subplots(2, 1, sharex = True, gridspec_kw={'height_ratios': [4, 1], 'wspace': 0, 'hspace': 0})
            data = self.multiIndicatorSignal(data)
            candlestick2_ohlc(ax1, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            ax1.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            ax1.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            ax1.plot(data.loc[data.viewSignal == 2.0].index, data[['Close']][data.viewSignal == 2], 'o', markersize = markersize, color = '#181c1c')
            ax2.plot(np.arange(len(data)), data.RSI, LW = 1.)
            ax2.fill_between(data.index, y1=30, y2=70, color='#7eebed', alpha='0.3')
            ax2.legend(loc = 1)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        #--MOVING AVERAGE vs BOLLINGER BAND vs SUPER TREND --
        elif grabstrategy == str(77):
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            data = self.multiIndicatorSignal(data)
            candlestick2_ohlc(subplots, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            subplots.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            subplots.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            subplots.plot(data.loc[data.viewSignal == 2.0].index, data[['Close']][data.viewSignal == 2], 'o', markersize = markersize, color = '#181c1c')
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        #-------------------------------------------------
        #--MOVING AVERAGE vs RSI vs MACD --
        elif grabstrategy == str(88):
            fig = Figure(figsize=self.figsize, dpi = 100)
            ax1, ax2, ax3 = fig.subplots(3, 1, sharex = True, gridspec_kw={'height_ratios': [1, 3, 1], 'wspace': 0, 'hspace': 0})
            data = self.multiIndicatorSignal(data)
            ax1.plot(np.arange(len(data)), data.MACD, LW = 1.)
            ax1.plot(np.arange(len(data)), data.MACD_HIST, LW = 1.)
            ax1.plot(np.arange(len(data)), data.MACD_SIGNAL, LW = 1.)
            ax1.fill_between(data.index, data.MACD_HIST, 0, where=(data.MACD_HIST >= 0), facecolor='#0fff97')
            ax1.fill_between(data.index, data.MACD_HIST, 0, where=(data.MACD_HIST <= 0), facecolor='#ff400f')
            candlestick2_ohlc(ax2, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            ax2.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            ax2.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            ax2.plot(data.loc[data.viewSignal == 2.0].index, data[['Close']][data.viewSignal == 2], 'o', markersize = markersize, color = '#181c1c')
            ax3.plot(np.arange(len(data)), data.RSI, LW = 1.)
            ax3.fill_between(data.index, y1=30, y2=70, color='#7eebed', alpha='0.3')
            ax3.legend(loc = 1)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        #--MOVING AVERAGE vs RSI vs SUPERTREND --
        elif grabstrategy == str(99):
            fig = Figure(figsize=self.figsize, dpi = 100)
            ax1, ax2 = fig.subplots(2, 1, sharex = True, gridspec_kw={'height_ratios': [4, 1], 'wspace': 0, 'hspace': 0})
            data = self.multiIndicatorSignal(data)
            candlestick2_ohlc(ax1, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            ax1.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            ax1.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            ax1.plot(data.loc[data.viewSignal == 2.0].index, data[['Close']][data.viewSignal == 2], 'o', markersize = markersize, color = '#181c1c')
            ax2.plot(np.arange(len(data)), data.RSI, LW = 1.)
            ax2.fill_between(data.index, y1=30, y2=70, color='#7eebed', alpha='0.3')
            ax2.legend(loc = 1)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        #--MOVING AVERAGE vs MACD vs SUPERTREND --
        elif grabstrategy == str(111):
            fig = Figure(figsize=self.figsize, dpi = 100)
            ax1, ax2 = fig.subplots(2, 1, sharex = True, gridspec_kw={'height_ratios': [4, 1], 'wspace': 0, 'hspace': 0})
            data = self.multiIndicatorSignal(data)
            candlestick2_ohlc(ax1, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            ax1.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            ax1.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            ax1.plot(data.loc[data.viewSignal == 2.0].index, data[['Close']][data.viewSignal == 2], 'o', markersize = markersize, color = '#181c1c')
            ax2.plot(np.arange(len(data)), data.MACD, LW = 1.)
            ax2.plot(np.arange(len(data)), data.MACD_HIST, LW = 1.)
            ax2.plot(np.arange(len(data)), data.MACD_SIGNAL, LW = 1.)
            ax2.fill_between(data.index, data.MACD_HIST, 0, where=(data.MACD_HIST >= 0), facecolor='#0fff97')
            ax2.fill_between(data.index, data.MACD_HIST, 0, where=(data.MACD_HIST <= 0), facecolor='#ff400f')
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        #--MACD vs SUPERTREND vs RSI --
        elif grabstrategy == str(222):
            fig = Figure(figsize=self.figsize, dpi = 100)
            ax1, ax2, ax3 = fig.subplots(3, 1, sharex = True, gridspec_kw={'height_ratios': [1, 3, 1], 'wspace': 0, 'hspace': 0})
            data = self.multiIndicatorSignal(data)
            ax1.plot(np.arange(len(data)), data.MACD, LW = 1.)
            ax1.plot(np.arange(len(data)), data.MACD_HIST, LW = 1.)
            ax1.plot(np.arange(len(data)), data.MACD_SIGNAL, LW = 1.)
            ax1.fill_between(data.index, data.MACD_HIST, 0, where=(data.MACD_HIST >= 0), facecolor='#0fff97')
            ax1.fill_between(data.index, data.MACD_HIST, 0, where=(data.MACD_HIST <= 0), facecolor='#ff400f')
            candlestick2_ohlc(ax2, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            ax2.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            ax2.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            ax2.plot(data.loc[data.viewSignal == 2.0].index, data[['Close']][data.viewSignal == 2], 'o', markersize = markersize, color = '#181c1c')
            ax3.plot(np.arange(len(data)), data.RSI, LW = 1.)
            ax3.fill_between(data.index, y1=30, y2=70, color='#7eebed', alpha='0.3')
            ax3.legend(loc = 1)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        #--MACD vs SUPERTREND vs BOLLINGER BAND --
        elif grabstrategy == str(333):
            fig = Figure(figsize=self.figsize, dpi = 100)
            ax1, ax2 = fig.subplots(2, 1, sharex = True, gridspec_kw={'height_ratios': [4, 1], 'wspace': 0, 'hspace': 0})
            data = self.multiIndicatorSignal(data)
            candlestick2_ohlc(ax1, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            ax1.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            ax1.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            ax1.plot(data.loc[data.viewSignal == 2.0].index, data[['Close']][data.viewSignal == 2], 'o', markersize = markersize, color = '#181c1c')
            ax2.plot(np.arange(len(data)), data.MACD, LW = 1.)
            ax2.plot(np.arange(len(data)), data.MACD_HIST, LW = 1.)
            ax2.plot(np.arange(len(data)), data.MACD_SIGNAL, LW = 1.)
            ax2.fill_between(data.index, data.MACD_HIST, 0, where=(data.MACD_HIST >= 0), facecolor='#0fff97')
            ax2.fill_between(data.index, data.MACD_HIST, 0, where=(data.MACD_HIST <= 0), facecolor='#ff400f')
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        #--------------------------------------------------------------
        #--MOVING AVERAGE vs BOLLINGER BAND vs MACD vs RSI --
        elif grabstrategy == str(444):
            fig = Figure(figsize=self.figsize, dpi = 100)
            ax1, ax2, ax3 = fig.subplots(3, 1, sharex = True, gridspec_kw={'height_ratios': [1, 3, 1], 'wspace': 0, 'hspace': 0})
            data = self.multiIndicatorSignal(data)
            ax1.plot(np.arange(len(data)), data.MACD, LW = 1.)
            ax1.plot(np.arange(len(data)), data.MACD_HIST, LW = 1.)
            ax1.plot(np.arange(len(data)), data.MACD_SIGNAL, LW = 1.)
            ax1.fill_between(data.index, data.MACD_HIST, 0, where=(data.MACD_HIST >= 0), facecolor='#0fff97')
            ax1.fill_between(data.index, data.MACD_HIST, 0, where=(data.MACD_HIST <= 0), facecolor='#ff400f')
            candlestick2_ohlc(ax2, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            ax2.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            ax2.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            ax2.plot(data.loc[data.viewSignal == 2.0].index, data[['Close']][data.viewSignal == 2], 'o', markersize = markersize, color = '#181c1c')
            ax3.plot(np.arange(len(data)), data.RSI, LW = 1.)
            ax3.fill_between(data.index, y1=30, y2=70, color='#7eebed', alpha='0.3')
            ax3.legend(loc = 1)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        #--MOVING AVERAGE vs BOLLINGER BAND vs MACD vs SUPER TREND --
        elif grabstrategy == str(555):
            fig = Figure(figsize=self.figsize, dpi = 100)
            ax1, ax2 = fig.subplots(2, 1, sharex = True, gridspec_kw={'height_ratios': [4, 1], 'wspace': 0, 'hspace': 0})
            data = self.multiIndicatorSignal(data)
            candlestick2_ohlc(ax1, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            ax1.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            ax1.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            ax1.plot(data.loc[data.viewSignal == 2.0].index, data[['Close']][data.viewSignal == 2], 'o', markersize = markersize, color = '#181c1c')
            ax2.plot(np.arange(len(data)), data.MACD, LW = 1.)
            ax2.plot(np.arange(len(data)), data.MACD_HIST, LW = 1.)
            ax2.plot(np.arange(len(data)), data.MACD_SIGNAL, LW = 1.)
            ax2.fill_between(data.index, data.MACD_HIST, 0, where=(data.MACD_HIST >= 0), facecolor='#0fff97')
            ax2.fill_between(data.index, data.MACD_HIST, 0, where=(data.MACD_HIST <= 0), facecolor='#ff400f')
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        #--MOVING AVERAGE vs BOLLINGER BAND vs MACD vs RSI vs SUPER TREND--
        elif grabstrategy == str(666):
            fig = Figure(figsize=self.figsize, dpi = 100)
            ax1, ax2, ax3 = fig.subplots(3, 1, sharex = True, gridspec_kw={'height_ratios': [1, 3, 1], 'wspace': 0, 'hspace': 0})
            data = self.multiIndicatorSignal(data)
            ax1.plot(np.arange(len(data)), data.MACD, LW = 1.)
            ax1.plot(np.arange(len(data)), data.MACD_HIST, LW = 1.)
            ax1.plot(np.arange(len(data)), data.MACD_SIGNAL, LW = 1.)
            ax1.fill_between(data.index, data.MACD_HIST, 0, where=(data.MACD_HIST >= 0), facecolor='#0fff97')
            ax1.fill_between(data.index, data.MACD_HIST, 0, where=(data.MACD_HIST <= 0), facecolor='#ff400f')
            candlestick2_ohlc(ax2, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            ax2.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            ax2.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            ax2.plot(data.loc[data.viewSignal == 2.0].index, data[['Close']][data.viewSignal == 2], 'o', markersize = markersize, color = '#181c1c')
            ax3.plot(np.arange(len(data)), data.RSI, LW = 1.)
            ax3.fill_between(data.index, y1=30, y2=70, color='#7eebed', alpha='0.3')
            ax3.legend(loc = 1)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        elif grabstrategy == str(777):
            fig = Figure(figsize=self.figsize, dpi = 100)
            ax1, ax2, ax3 = fig.subplots(3, 1, sharex = True, gridspec_kw={'height_ratios': [1, 3, 1], 'wspace': 0, 'hspace': 0})
            data = self.multiIndicatorSignal(data)
            ax1.plot(np.arange(len(data)), data.MACD, LW = 1.)
            ax1.plot(np.arange(len(data)), data.MACD_HIST, LW = 1.)
            ax1.plot(np.arange(len(data)), data.MACD_SIGNAL, LW = 1.)
            ax1.fill_between(data.index, data.MACD_HIST, 0, where=(data.MACD_HIST >= 0), facecolor='#0fff97')
            ax1.fill_between(data.index, data.MACD_HIST, 0, where=(data.MACD_HIST <= 0), facecolor='#ff400f')
            candlestick2_ohlc(ax2, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            ax2.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            ax2.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            ax2.plot(data.loc[data.viewSignal == 2.0].index, data[['Close']][data.viewSignal == 2], 'o', markersize = markersize, color = '#181c1c')
            ax3.plot(np.arange(len(data)), data.RSI, LW = 1.)
            ax3.fill_between(data.index, y1=30, y2=70, color='#7eebed', alpha='0.3')
            ax3.legend(loc = 1)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        elif grabstrategy == str(888):
            fig = Figure(figsize=self.figsize, dpi = 100)
            ax1, ax2 = fig.subplots(2, 1, sharex = True, gridspec_kw={'height_ratios': [4, 1], 'wspace': 0, 'hspace': 0})
            data = self.multiIndicatorSignal(data)
            ax2.plot(np.arange(len(data)), data.MACD, LW = 1.)
            ax2.plot(np.arange(len(data)), data.MACD_HIST, LW = 1.)
            ax2.plot(np.arange(len(data)), data.MACD_SIGNAL, LW = 1.)
            ax2.fill_between(data.index, data.MACD_HIST, 0, where=(data.MACD_HIST >= 0), facecolor='#0fff97')
            ax2.fill_between(data.index, data.MACD_HIST, 0, where=(data.MACD_HIST <= 0), facecolor='#ff400f')
            candlestick2_ohlc(ax1, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            ax1.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            ax1.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            ax1.plot(data.loc[data.viewSignal == 2.0].index, data[['Close']][data.viewSignal == 2], 'o', markersize = markersize, color = '#181c1c')
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        elif grabstrategy == str(999):
            fig = Figure(figsize=self.figsize, dpi = 100)
            ax1, ax2 = fig.subplots(2, 1, sharex = True, gridspec_kw={'height_ratios': [4, 1], 'wspace': 0, 'hspace': 0})
            data = self.multiIndicatorSignal(data)
            candlestick2_ohlc(ax1, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            ax1.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            ax1.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            ax1.plot(data.loc[data.viewSignal == 2.0].index, data[['Close']][data.viewSignal == 2], 'o', markersize = markersize, color = '#181c1c')
            ax2.plot(np.arange(len(data)), data.RSI, LW = 1.)
            ax2.fill_between(data.index, y1=30, y2=70, color='#7eebed', alpha='0.3')
            ax2.legend(loc = 1)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        elif grabstrategy == str(1111):
            fig = Figure(figsize=self.figsize, dpi = 100)
            ax1, ax2 = fig.subplots(2, 1, sharex = True, gridspec_kw={'height_ratios': [4, 1], 'wspace': 0, 'hspace': 0})
            data = self.multiIndicatorSignal(data)
            candlestick2_ohlc(ax1, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            ax1.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            ax1.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            ax1.plot(data.loc[data.viewSignal == 2.0].index, data[['Close']][data.viewSignal == 2], 'o', markersize = markersize, color = '#181c1c')
            ax2.plot(np.arange(len(data)), data.RSI, LW = 1., color = '#e64af0')
            ax2.fill_between(data.index, y1=30, y2=70, color='#f6b4fa', alpha='0.3')
            ax2.legend(loc = 1)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        elif grabstrategy == str(2222):
            fig = Figure(figsize=self.figsize, dpi = 100)
            ax1, ax2 = fig.subplots(2, 1, sharex = True, gridspec_kw={'height_ratios': [4, 1], 'wspace': 0, 'hspace': 0})
            data = self.multiIndicatorSignal(data)
            candlestick2_ohlc(ax1, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            ax1.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            ax1.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            ax1.plot(data.loc[data.viewSignal == 2.0].index, data[['Close']][data.viewSignal == 2], 'o', markersize = markersize, color = '#181c1c')
            ax2.plot(np.arange(len(data)), data.MACD, LW = 1.)
            ax2.plot(np.arange(len(data)), data.MACD_HIST, LW = 1.)
            ax2.plot(np.arange(len(data)), data.MACD_SIGNAL, LW = 1.)
            ax2.fill_between(data.index, data.MACD_HIST, 0, where=(data.MACD_HIST >= 0), facecolor='#0fff97')
            ax2.fill_between(data.index, data.MACD_HIST, 0, where=(data.MACD_HIST <= 0), facecolor='#ff400f')
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        elif grabstrategy == str(3333):
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            data = self.multiIndicatorSignal(data)
            candlestick2_ohlc(subplots, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            subplots.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            subplots.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            subplots.plot(data.loc[data.viewSignal == 2.0].index, data[['Close']][data.viewSignal == 2], 'o', markersize = markersize, color = '#181c1c')
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        elif grabstrategy == str(4444):
            fig = Figure(figsize=self.figsize, dpi = 100)
            ax1, ax2 = fig.subplots(2, 1, sharex = True, gridspec_kw={'height_ratios': [4, 1], 'wspace': 0, 'hspace': 0})
            data = self.multiIndicatorSignal(data)
            candlestick2_ohlc(ax1, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            ax1.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            ax1.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            ax1.plot(data.loc[data.viewSignal == 2.0].index, data[['Close']][data.viewSignal == 2], 'o', markersize = markersize, color = '#181c1c')
            ax2.plot(np.arange(len(data)), data.RSI, LW = 1., color = '#e64af0')
            ax2.fill_between(data.index, y1=30, y2=70, color='#f6b4fa', alpha='0.3')
            ax2.legend(loc = 1)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        elif grabstrategy == str(5555):
            fig = Figure(figsize=self.figsize, dpi = 100)
            ax1, ax2 = fig.subplots(2, 1, sharex = True, gridspec_kw={'height_ratios': [4, 1], 'wspace': 0, 'hspace': 0})
            data = self.multiIndicatorSignal(data)
            candlestick2_ohlc(ax1, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            ax1.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            ax1.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            ax1.plot(data.loc[data.viewSignal == 2.0].index, data[['Close']][data.viewSignal == 2], 'o', markersize = markersize, color = '#181c1c')
            ax2.plot(np.arange(len(data)), data.CCI, LW = 1., color = '#e64af0')
            ax2.fill_between(data.index, y1=-100, y2=100, color='#f6b4fa', alpha='0.3')
            ax2.legend(loc = 1)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        elif grabstrategy == str(6666):
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            data['viewSignal'] = data.signal.diff()
            candlestick2_ohlc(subplots, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            subplots.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            subplots.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        elif grabstrategy == str(7777):
            fig = Figure(figsize=self.figsize, dpi = 100)
            ax1, ax2 = fig.subplots(2, 1, sharex = True, gridspec_kw={'height_ratios': [4, 1], 'wspace': 0, 'hspace': 0})
            data = self.multiIndicatorSignal(data)
            candlestick2_ohlc(ax1, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            ax1.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            ax1.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            ax1.plot(data.loc[data.viewSignal == 2.0].index, data[['Close']][data.viewSignal == 2], 'o', markersize = markersize, color = '#181c1c')
            ax2.plot(np.arange(len(data)), data.RSI, LW = 1., color = '#e64af0')
            ax2.fill_between(data.index, y1=30, y2=70, color='#f6b4fa', alpha='0.3')
            ax2.legend(loc = 1)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        elif grabstrategy == str(8888):
            fig = Figure(figsize=self.figsize, dpi = 100)
            ax1, ax2 = fig.subplots(2, 1, sharex = True, gridspec_kw={'height_ratios': [4, 1], 'wspace': 0, 'hspace': 0})
            data = self.multiIndicatorSignal(data)
            candlestick2_ohlc(ax1, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            ax1.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            ax1.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            ax1.plot(data.loc[data.viewSignal == 2.0].index, data[['Close']][data.viewSignal == 2], 'o', markersize = markersize, color = '#181c1c')
            ax2.plot(np.arange(len(data)), data.CCI, LW = 1., color = '#e64af0')
            ax2.fill_between(data.index, y1=-100, y2=100, color='#f6b4fa', alpha='0.3')
            ax2.legend(loc = 1)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        elif grabstrategy == str(9999):
            fig = Figure(figsize=self.figsize)
            subplots = fig.add_subplot(111)
            data = self.multiIndicatorSignal(data)
            candlestick2_ohlc(subplots, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            subplots.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            subplots.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            subplots.plot(data.loc[data.viewSignal == 2.0].index, data[['Close']][data.viewSignal == 2], 'o', markersize = markersize, color = '#181c1c')
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        elif grabstrategy == str(11111):
            fig = Figure(figsize=self.figsize, dpi = 100)
            ax1, ax2 = fig.subplots(2, 1, sharex = True, gridspec_kw={'height_ratios': [4, 1], 'wspace': 0, 'hspace': 0})
            data = self.multiIndicatorSignal(data)
            candlestick2_ohlc(ax1, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            ax1.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            ax1.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            ax1.plot(data.loc[data.viewSignal == 2.0].index, data[['Close']][data.viewSignal == 2], 'o', markersize = markersize, color = '#181c1c')
            ax2.plot(np.arange(len(data)), data.CCI, LW = 1., color = '#e64af0')
            ax2.fill_between(data.index, y1=-100, y2=100, color='#f6b4fa', alpha='0.3')
            ax2.legend(loc = 1)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        elif grabstrategy == str(22222):
            fig = Figure(figsize=self.figsize, dpi = 100)
            ax1, ax2 = fig.subplots(2, 1, sharex = True, gridspec_kw={'height_ratios': [4, 1], 'wspace': 0, 'hspace': 0})
            data = self.multiIndicatorSignal(data)
            candlestick2_ohlc(ax1, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            ax1.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            ax1.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            ax1.plot(data.loc[data.viewSignal == 2.0].index, data[['Close']][data.viewSignal == 2], 'o', markersize = markersize, color = '#181c1c')
            ax2.plot(np.arange(len(data)), data.MACD, LW = 1.)
            ax2.plot(np.arange(len(data)), data.MACD_HIST, LW = .5)
            ax2.plot(np.arange(len(data)), data.MACD_SIGNAL, LW = .5)
            ax2.fill_between(data.index, data.MACD_HIST, 0, where=(data.MACD_HIST >= 0), facecolor='#0fff97')
            ax2.fill_between(data.index, data.MACD_HIST, 0, where=(data.MACD_HIST <= 0), facecolor='#ff400f')
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        elif grabstrategy == str(33333):
            fig = Figure(figsize=self.figsize, dpi = 100)
            ax1, ax2 = fig.subplots(2, 1, sharex = True, gridspec_kw={'height_ratios': [4, 1], 'wspace': 0, 'hspace': 0})
            data = self.multiIndicatorSignal(data)
            candlestick2_ohlc(ax1, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            ax1.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            ax1.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            ax2.plot(np.arange(len(data)), data.HCCI, LW = 1., color = '#e64af0')
            ax2.fill_between(data.index, y1=-100, y2=100, color='#f6b4fa', alpha='0.3')
            ax2.legend(loc = 1)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        elif grabstrategy == str(44444):
            fig = Figure(figsize=self.figsize, dpi = 100)
            ax1, ax2, ax3 = fig.subplots(3, 1, sharex = True, gridspec_kw={'height_ratios': [1, 3, 1], 'wspace': 0, 'hspace': 0})
            data = self.multiIndicatorSignal(data)
            ax1.plot(np.arange(len(data)), data.CCI, LW = 1., color = '#e64af0')
            ax1.fill_between(data.index, y1=-100, y2=100, color='#f6b4fa', alpha='0.3')
            ax1.legend(loc = 1)
            candlestick2_ohlc(ax2, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            ax2.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            ax2.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            ax2.plot(data.loc[data.viewSignal == 2.0].index, data[['Close']][data.viewSignal == 2], 'o', markersize = markersize, color = '#181c1c')
            ax3.plot(np.arange(len(data)), data.HCCI, LW = 1., color = '#e64af0')
            ax3.fill_between(data.index, y1=-100, y2=100, color='#f6b4fa', alpha='0.3')
            ax3.legend(loc = 1)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        elif grabstrategy == str(55555):
            fig = Figure(figsize=self.figsize, dpi = 100)
            ax1, ax2, ax3 = fig.subplots(3, 1, sharex = True, gridspec_kw={'height_ratios': [1, 3, 1], 'wspace': 0, 'hspace': 0})
            data = self.multiIndicatorSignal(data)
            ax1.plot(np.arange(len(data)), data.CCI, LW = 1., color = '#e64af0')
            ax1.fill_between(data.index, y1=-100, y2=100, color='#f6b4fa', alpha='0.3')
            ax1.legend(loc = 1)
            candlestick2_ohlc(ax2, data.Open, data.High, data.Low, data.Close, colorup='g', width = candlewidth)
            ax2.plot(data.loc[data.viewSignal == -1.0].index, data[['Close']][data.viewSignal == -1], 'v', markersize = markersize, color = 'r')
            ax2.plot(data.loc[data.viewSignal == 1.0].index, data[['Close']][data.viewSignal == 1], '^', markersize = markersize, color = 'g')
            ax2.plot(data.loc[data.viewSignal == 2.0].index, data[['Close']][data.viewSignal == 2], 'o', markersize = markersize, color = '#181c1c')
            ax3.plot(np.arange(len(data)), data.HCCI, LW = 1., color = '#e64af0')
            ax3.fill_between(data.index, y1=-100, y2=100, color='#f6b4fa', alpha='0.3')
            ax3.legend(loc = 1)
            fig.set_tight_layout(True)
            canvas = FigureCanvasTkAgg(fig, frameplot)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
            toolbar = NavigationToolbar2Tk(canvas, frameplot)
            toolbar.update()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        else:
            return None
        frameplot.grid(row = 2, column = 0)
        
        
#%%
if __name__ == '__main__':
    import multiprocessing
    import time
    import datetime
    path = {'mainPath': '/home/kenneth/Documents/GIT_PROJECTS/AI-Signal-Generator',
            'acountPath': 'DOCS/account_id.txt',
            'tokenPath': 'DOCS/token.txt',
            'telegram': 'DOCS/telegram.txt',
            'predicted': 'PREDICTED',
            'signals': 'SIGNALS',
            'start': '2019-04-01T00:00:00Z',
            'end': str(datetime.datetime.utcnow().isoformat('T')[:-7] +'Z'),
            'environment': 'live',
            'strategy': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '11',
                         '22', '33', '44', '55', '66', '77', '88', '99', '111',
                         '222', '333', '444', '555', '666', '777', '888', '999', '1111',
                         '2222', '3333', '4444', '5555', '6666', '7777', '8888', '9999',
                         '11111', '22222', '33333', '44444', '55555'],
            'instruments': 'AUD_USD,BCO_USD,BTC_USD,DE30_EUR,EUR_AUD,EUR_JPY,EUR_USD,GBP_JPY,GBP_USD,'+\
                            'NAS100_USD,SPX500_USD,US30_USD,USD_CAD,USD_JPY,XAU_USD',
            'timeframes': ['M15', 'M30', 'H1', 'H2', 'H3', 'H4', 'H6', 'H8',
                           'H12', 'D', 'W']}
    
    #tkinter mainloop
    def steamerloop(path):
        root = tk.Tk()
        root.title("AI Signal Generator")
        root.option_add("*Font", "Calibri 10 bold")
        
        #style
        s = ttk.Style()
        s.theme_create( "MyStyle", parent="alt", settings={
                "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0] } },
                "TNotebook.Tab": {"configure": {"padding": [50, 10],
                                                "font" : ('Calibri', '10', 'bold')},}})
        s.theme_use("MyStyle")
        tabSpace = ttk.Notebook(root)
        firstFrame = ttk.Frame(tabSpace)
        secondFrame = ttk.Frame(tabSpace)
        thirdFrame = ttk.Frame(tabSpace)
        #--signal
        streamSignal(firstFrame, path).pack()
        #--visualization
        visu(secondFrame, path).pack()
        #--Returns
        Returns(thirdFrame, path).pack()
        #--Notebooks
        tabSpace.add(firstFrame, text = 'Automated signal')
        tabSpace.add(secondFrame, text = 'Visualize signals')
        tabSpace.add(thirdFrame, text = 'Recommendation')
        tabSpace.pack()
        root.resizable(0,0)
        root.mainloop()
    
    #queue tkinter app
    def mainloop(function, arg, queue):
        queue.put(function(arg))
        
    q = Queue()
    multiprocessing.Process(target = mainloop, args=(steamerloop, path, q)).start()
     



