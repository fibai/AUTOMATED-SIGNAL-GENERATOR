# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 18:04:29 2019

@author: kennedy
"""
import os
from STOCK import stock, loc
import pandas as pd
pd.options.mode.chained_assignment = None
import numpy as np
from datetime import datetime


#%% SIGNAL GENERATOR --> MACD, BOLLINGER BAND, RSI, etc
  
#Moving average signals
class signalStrategy(object):
    def __init__(self):
        return
    
    def ls_STOK(self):
      '''
      :Return:
        List of stock in dataset
      '''
      DIR_OBJ = os.listdir()
      STOK_list_ = []
      for x in range(len(DIR_OBJ)):
        STOK_list_.append(DIR_OBJ[x].strip('.csv'))
        
      return STOK_list_
  
    def MA_signal(self, STK_data, ema = None, sma = None, period_alpha = None,
                  period_beta = None):
      '''
      :Params:
        :STK_data: Stock data
        :ema: defaul is None. if True, function uses ema instead of sma
        :sma: default is None. if True, fucntion uses sma instead of ema
        :period_alpha: first moving average
        :period_beta: first moving average
      '''
      stock_data = stock(STK_data)
      df = stock_data.OHLC()
      df['Close'] = stock_data.c
      if sma and ema:
        raise ValueError('sma and ema cannot be true at same time')
      elif ema:
        assert period_alpha < period_beta, 'Ensure period_alpha is less than period beta'
        alpha = stock_data.ema(stock_data.Close, period_alpha)
        beta = stock_data.ema(stock_data.Close, period_beta)
        df['signal'] = np.where(beta > alpha, 0, 1)
      elif sma:
        assert period_alpha < period_beta, 'Ensure period_alpha is less than period beta'
        alpha = stock_data.sma(stock_data.Close, period_alpha)
        beta = stock_data.sma(stock_data.Close, period_beta)
        df['signal'] = np.where(beta > alpha, 0, 1)
      #return siganl
      return df
      
    ##RSI signal
    def RSI_signal(self, STK_data, period, lw_bound, up_bound):
      '''
      :Arguments:
        df: stock data
      :Return type:
        signal
      '''
      stock_data = stock(STK_data)
      OHLC = stock_data.OHLC()
      df = stock_data.CutlerRSI(OHLC, period)
      
      assert isinstance(df, pd.Series) or isinstance(df, pd.DataFrame)
      #convert to dataframe
      if isinstance(df, pd.Series):
        df = df.to_frame()
      else:
        pass
      #get signal
      #1--> indicates buy position
      #0 --> indicates sell posotion
      df['signal'] = np.zeros(df.shape[0])
      pos = 0
      for ij in df.loc[:, ['RSI_Cutler_'+str(period)]].values:
        print(df.loc[:, ['RSI_Cutler_'+str(period)]].values[pos])
        if df.loc[:, ['RSI_Cutler_'+str(period)]].values[pos] >= up_bound:
          df['signal'][pos:] = 1 #uptrend
        elif df.loc[:, ['RSI_Cutler_'+str(period)]].values[pos] <= lw_bound:
          df['signal'][pos:] = 0 #downtrend
        pos +=1
      print('*'*40)
      print('RSI Signal Generation completed')
      print('*'*40)
      return df
      
    #RSI Signal
    def macd_crossOver(self, STK_data, fast, slow, signal):
      '''
      :Argument:
        MACD dataframe
      :Return type:
        MACD with Crossover signal
      '''
      stock_data = stock(STK_data)
      df = stock_data.MACD(fast, slow, signal)
      try:
        assert isinstance(df, pd.DataFrame) or isinstance(df, pd.Series)
        #dataframe
        if isinstance(df, pd.Series):
          df = df.to_frame()
        else:
          pass
        #1--> indicates buy position
        #0 --> indicates sell posotion
        df['Close'] = stock_data.c
        df['signal'] = np.where(df.MACD > df.MACD_SIGNAL, 1, 0)
      except IOError as e:
        raise('Dataframe required {}' .format(e))
      finally:
        print('*'*40)
        print('MACD signal generated')
        print('*'*40)
      return df
    
    #SuperTrend Signal 
    def SuperTrend_signal(self, STK_data, multiplier, period):
      '''
      :Argument:
        SuperTrend dataframe
      :Return type:
        Super trend signal
      '''
      stock_data = stock(STK_data)
      #--Call superTrend function
      df = stock_data.SuperTrend(STK_data, multiplier, period)
      try:
        assert isinstance(df, pd.DataFrame) or isinstance(df, pd.Series)
        #dataframe
        if isinstance(df, pd.Series):
          df = df.to_frame()
        else:
          pass
        #1--> indicates buy position
        #0 --> indicates sell posotion
        df = df.fillna(0)
        df['Close'] = stock_data.c
        df['signal'] = np.where(stock_data.Close >= df.SuperTrend, 1, 0)
      except IOError as e:
        raise('Dataframe required {}' .format(e))
      finally:
        print('*'*40)
        print('SuperTrend Signal generated')
        print('*'*40)
      return df
    
    #Bollinger band signal
    def bollinger_band_signal(self, STK_data, period, deviation):
        '''
        :Argument:
            df: stock data
        :Return type:
            :bollinger band signal
        '''
        stock_data = stock(STK_data)
        Close = stock_data.Close
        df = stock_data.Bolinger_Band(period, deviation)
        df = df.fillna(value = 0)
        assert isinstance(df, pd.DataFrame) or isinstance(df, pd.Series)
        #dataframe
        if isinstance(df, pd.Series):
            df = df.to_frame()
        #get signal
        #1--> indicates buy position
        #0 --> indicates sell posotion
        df['signal'] = np.zeros(df.shape[0])
        pos = 0
        for ii in Close:
          print(Close[pos])
          if Close[pos] >= df.Upper_band.values[pos]:
            df['signal'][pos:] = 1
          elif Close[pos] <= df.Lower_band.values[pos]:
            df['signal'][pos:] = 0
          pos += 1
        df['Close'] = Close
        print('*'*40)
        print('Bollinger Signal Generation completed')
        print('*'*40)
        return df

#Trading Algorithm
class Signal(object):
    def __init__(self):
        return
    
    def tradingSignal(self, STK_data, RSI = None, MACD = None, Bollinger_Band = None, SuperTrend = None, MA = None, strategy = None):
        '''
        STRATEGIES
        ========================
        [1] MA CROSS-OVER
        [2] BOLLINGER BAND
        [3] MACD
        [4] RSI
        [5] SUPER TREND
        [6] MA vs SUPER_TREND
        [7] MA vs MACD
        [8] MA vs RSI
        [9] MA vs BOLLINGER BAND
        [11] BOLLINGER BAND vs MACD
        [22] BOLLINGER BAND vs RSI
        [33] BOLLINGER vs SUPERTREND
        [44] RSI vs SUPER TREND
        [55] MOVING AVERAGE vs BOLLINGER BAND vs MACD
        [66] MOVING AVERAGE vs BOLLINGER BAND vs RSI
        [77] MOVING AVERAGE vs BOLLINGER BAND vs SUPER TREND
        [88] MOVING AVERAGE vs BOLLINGER BAND vs MACD vs RSI
        [99] MOVING AVERAGE vs BOLLINGER BAND vs MACD vs SUPER TREND
        [111] MOVING AVERAGE vs BOLLINGER BAND vs MACD vs RSI vs SUPER TREND
        ------------------------------------------------------------------------
        :Arguments:
            :MACD:
                dataframe containing MACD signal
            :Bollinger_Band:
                dataframe containing Bollinger band signal
            :RSI:
                dataframe containing RSI signal
            :Return Type:
                Buy Sell or Hold signal
        '''
        stock_data = stock(STK_data)
        OHLC = stock_data.OHLC()
        #--define strategy
        #--MA---
        if strategy == '1':
            Moving_avg = MA.signal
            MA['Position'] = ''
            for ii in range(MA.shape[0]):
                if Moving_avg[ii] == 1:
                    MA.Position[ii] = 'BUY'
                elif Moving_avg[ii] == 0:
                    MA.Position[ii] = 'SELL'
            return MA
        #-- Bollinger Band---
        elif strategy == '2':
            BB_signal = Bollinger_Band.signal.values
            Bollinger_Band['Position'] = ''
            for ii in range(BB_signal.shape[0]):
                if BB_signal[ii] == 1:
                    Bollinger_Band.Position[ii] = 'BUY'
                elif BB_signal[ii] == 0:
                    Bollinger_Band.Position[ii] = 'SELL'
            return Bollinger_Band
        #-- MACD ----
        elif strategy == '3':
            MACD_signal = MACD.signal.values
            MACD['Position'] = ''
            for ii in range(MACD.shape[0]):
                if MACD_signal[ii] == 1:
                    MACD.Position[ii] = 'BUY'
                elif MACD_signal[ii] == 0:
                    MACD.Position[ii] = 'SELL'
            return MACD
        #-- RSI----
        elif strategy == '4':
            RSI_signal = RSI.signal.values
            RSI['Position'] = ''
            for ii in range(RSI.shape[0]):
                if RSI_signal[ii] == 1:
                    RSI.Position[ii] = 'BUY'
                elif RSI_signal[ii] == 0:
                    RSI.Position[ii] = 'SELL'
            return RSI
        #-- SuperTrend_Signal ---
        elif strategy == '5':
            SuperTrend_Signal = SuperTrend.signal.values
            SuperTrend['Position'] = ''
            for ii in range(SuperTrend.shape[0]):
                if SuperTrend_Signal[ii] == 1:
                    SuperTrend.Position[ii] = 'BUY'
                elif SuperTrend_Signal[ii] == 0:
                    SuperTrend.Position[ii] = 'SELL'
            return SuperTrend
        #--MA vs SUPER_TREND--
        elif strategy == '6':
            SuperTrend_Signal = SuperTrend.signal.values
            Moving_avg = MA.signal
            OHLC['Position'] = ''
            for ii in range(OHLC.shape[0]):
                if Moving_avg[ii] == 1 and SuperTrend_Signal[ii] == 1:
                    OHLC.Position[ii] = 'BUY'
                elif Moving_avg[ii] == 0 and SuperTrend_Signal[ii] == 0:
                    OHLC.Position[ii] = 'SELL'
                else:
                    OHLC.Position[ii] = 'HOLD'
            return OHLC
        #-- MA vs MACD ----
        elif strategy == '7':
            Moving_avg = MA.signal
            MACD_signal = MACD.signal.values
            OHLC['Position'] = ''
            for ii in range(OHLC.shape[0]):
                if Moving_avg[ii] == 1 and MACD_signal[ii] == 1:
                    OHLC.Position[ii] = 'BUY'
                elif Moving_avg[ii] == 0 and MACD_signal[ii] == 0:
                    OHLC.Position[ii] = 'SELL'
                else:
                    OHLC.Position[ii] = 'HOLD'
            return OHLC
        #--MA vs RSI--
        elif strategy == '8':
            Moving_avg = MA.signal
            RSI_signal = RSI.signal.values
            OHLC['Position'] = ''
            for ii in range(Moving_avg.shape[0]):
                if Moving_avg[ii] == 1 and RSI_signal[ii] == 1:
                    OHLC.Position[ii] = 'BUY'
                elif Moving_avg[ii] == 0 and RSI_signal[ii] == 0:
                    OHLC.Position[ii] = 'SELL'
                else:
                    OHLC.Position[ii] = 'HOLD'
            return OHLC
        #--- MA vs BOLLINGER BAND ---
        elif strategy == '9':
            Moving_avg = MA.signal
            BB_signal = Bollinger_Band.signal.values
            OHLC['Position'] = ''
            for ii in range(Moving_avg.shape[0]):
                if Moving_avg[ii] == 1 and BB_signal[ii] == 1:
                    OHLC.Position[ii] = 'BUY'
                elif Moving_avg[ii] == 0 and BB_signal[ii] == 0:
                    OHLC.Position[ii] = 'SELL'
                else:
                    OHLC.Position[ii] = 'HOLD'
            return OHLC
        #-- BOLLINGER BAND vs MACD
        elif strategy == '11':
            BB_signal = Bollinger_Band.signal.values
            MACD_signal = MACD.signal.values
            OHLC['Position'] = ''
            for ii in range(BB_signal.shape[0]):
                if BB_signal[ii] == 1 and MACD_signal[ii] == 1:
                    OHLC.Position[ii] = 'BUY'
                elif BB_signal[ii] == 0 and MACD_signal[ii] == 0:
                    OHLC.Position[ii] = 'SELL'
                else:
                    OHLC.Position[ii] = 'HOLD'
            return OHLC
        #--BOLLINGER BAND vs RSI--
        elif strategy == '22':
            BB_signal = Bollinger_Band.signal.values
            RSI_signal = RSI.signal.values
            OHLC['Position'] = ''
            for ii in range(BB_signal.shape[0]):
                if BB_signal[ii] == 1 and RSI_signal[ii] == 1:
                    OHLC.Position[ii] = 'BUY'
                elif BB_signal[ii] == 0 and RSI_signal[ii] == 0:
                    OHLC.Position[ii] = 'SELL'
                else:
                    OHLC.Position[ii] = 'HOLD'
            return OHLC
        #--BOLLINGER vs SUPERTREND --
        elif strategy == '33':
            BB_signal = Bollinger_Band.signal.values
            SuperTrend_Signal = SuperTrend.signal.values
            OHLC['Position'] = ''
            for ii in range(BB_signal.shape[0]):
                if BB_signal[ii] == 1 and SuperTrend_Signal[ii] == 1:
                    OHLC.Position[ii] = 'BUY'
                elif BB_signal[ii] == 0 and SuperTrend_Signal[ii] == 0:
                    OHLC.Position[ii] = 'SELL'
                else:
                    OHLC.Position[ii] = 'HOLD'
            return OHLC
        #--RSI vs SUPER TREND --
        elif strategy == '44':
            RSI_signal = RSI.signal.values
            SuperTrend_Signal = SuperTrend.signal.values
            OHLC['Position'] = ''
            for ii in range(BB_signal.shape[0]):
                if RSI_signal[ii] == 1 and SuperTrend_Signal[ii] == 1:
                    OHLC.Position[ii] = 'BUY'
                elif RSI_signal[ii] == 0 and SuperTrend_Signal[ii] == 0:
                    OHLC.Position[ii] = 'SELL'
                else:
                    OHLC.Position[ii] = 'HOLD'
            return OHLC
        #--MOVING AVERAGE vs BOLLINGER BAND vs MACD --
        elif strategy == '55':
            Moving_avg = MA.signal
            BB_signal = Bollinger_Band.signal.values
            MACD_signal = MACD.signal.values
            OHLC['Position'] = ''
            for ii in range(BB_signal.shape[0]):
                if Moving_avg[ii] == 1 and BB_signal[ii] == 1 and\
                    MACD_signal[ii] == 1:
                    OHLC.Position[ii] = 'BUY'
                elif Moving_avg[ii] == 0 and BB_signal[ii] == 0 and\
                    MACD_signal[ii] == 0:
                    OHLC.Position[ii] = 'SELL'
                else:
                    OHLC.Position[ii] = 'HOLD'
            return OHLC
        #--MOVING AVERAGE vs BOLLINGER BAND vs RSI --
        elif strategy == '66':
            Moving_avg = MA.signal
            BB_signal = Bollinger_Band.signal.values
            RSI_signal = RSI.signal.values
            OHLC['Position'] = ''
            for ii in range(BB_signal.shape[0]):
                if Moving_avg[ii] == 1 and BB_signal[ii] == 1 and\
                    RSI_signal[ii] == 1:
                    OHLC.Position[ii] = 'BUY'
                elif Moving_avg[ii] == 0 and BB_signal[ii] == 0 and\
                    RSI_signal[ii] == 0:
                    OHLC.Position[ii] = 'SELL'
                else:
                    OHLC.Position[ii] = 'HOLD'
            return OHLC
        #--MOVING AVERAGE vs BOLLINGER BAND vs SUPER TREND --
        elif strategy == '77':
            Moving_avg = MA.signal
            BB_signal = Bollinger_Band.signal.values
            SuperTrend_Signal = SuperTrend.signal.values
            OHLC['Position'] = ''
            for ii in range(BB_signal.shape[0]):
                if Moving_avg[ii] == 1 and BB_signal[ii] == 1 and\
                    SuperTrend_Signal[ii] == 1:
                    OHLC.Position[ii] = 'BUY'
                elif Moving_avg[ii] == 0 and BB_signal[ii] == 0 and\
                    SuperTrend_Signal[ii] == 0:
                    OHLC.Position[ii] = 'SELL'
                else:
                    OHLC.Position[ii] = 'HOLD'
            return OHLC
        #--MOVING AVERAGE vs BOLLINGER BAND vs MACD vs RSI --
        elif strategy == '88':
            Moving_avg = MA.signal
            BB_signal = Bollinger_Band.signal.values
            MACD_signal = MACD.signal.values
            RSI_signal = RSI.signal.values
            OHLC['Position'] = ''
            for ii in range(BB_signal.shape[0]):
                if Moving_avg[ii] == 1 and BB_signal[ii] == 1 and\
                    MACD_signal[ii] == 1 and RSI_signal[ii] == 1:
                    OHLC.Position[ii] = 'BUY'
                elif Moving_avg[ii] == 0 and BB_signal[ii] == 0 and\
                    MACD_signal[ii] == 0 and RSI_signal[ii] == 1:
                    OHLC.Position[ii] = 'SELL'
                else:
                    OHLC.Position[ii] = 'HOLD'
            return OHLC
        #--MOVING AVERAGE vs BOLLINGER BAND vs MACD vs SUPER TREND --
        elif strategy == '99':
            Moving_avg = MA.signal
            BB_signal = Bollinger_Band.signal.values
            MACD_signal = MACD.signal.values
            SuperTrend_Signal = SuperTrend.signal.values
            OHLC['Position'] = ''
            for ii in range(BB_signal.shape[0]):
                if Moving_avg[ii] == 1 and BB_signal[ii] == 1 and\
                    MACD_signal[ii] == 1 and SuperTrend_Signal[ii] == 1:
                    OHLC.Position[ii] = 'BUY'
                elif Moving_avg[ii] == 0 and BB_signal[ii] == 0 and\
                    MACD_signal[ii] == 0 and SuperTrend_Signal[ii] == 1:
                    OHLC.Position[ii] = 'SELL'
                else:
                    OHLC.Position[ii] = 'HOLD'
            return OHLC
        #--MOVING AVERAGE vs BOLLINGER BAND vs MACD vs RSI vs SUPER TREND--
        elif strategy == '111':
            Moving_avg = MA.signal
            BB_signal = Bollinger_Band.signal.values
            MACD_signal = MACD.signal.values
            RSI_signal = RSI.signal.values
            SuperTrend_Signal = SuperTrend.signal.values
            OHLC['Position'] = ''
            for ii in range(BB_signal.shape[0]):
                if Moving_avg[ii] == 1 and BB_signal[ii] == 1 and\
                    MACD_signal[ii] == 1 and RSI_signal[ii] == 1 and\
                    SuperTrend_Signal[ii] == 1:
                    OHLC.Position[ii] = 'BUY'
                elif Moving_avg[ii] == 0 and BB_signal[ii] == 0 and\
                    MACD_signal[ii] == 0 and RSI_signal[ii] == 0 and\
                    SuperTrend_Signal[ii] == 1:
                    OHLC.Position[ii] = 'SELL'
                else:
                    OHLC.Position[ii] = 'HOLD'
            return OHLC
    
    def main(self, path, strategy, STOCK, DEVIATION = None, PERIOD = None, LOWER_BOUND = None,
             UPPER_BOUND = None, MIDLINE = None, FAST = None, SLOW = None, SIGNAL = None, TIMEFRAME = None,
             PERIOD_ALPHA = None, PERIOD_BETA = None):
        '''
        :param:
            :strategy: select a startegy to signal signal 
            INDICATOR SIGNALS
            ========================
            [x] MOVING AVERAGE
            [x] BOLLINGER BAND
            [X] MACD
            [X] RSI
            [X] SUPER TREND
            ========================
            STRATEGIES
            ========================
            [1] MA CROSS-OVER
            [2] BOLLINGER BAND
            [3] MACD
            [4] RSI
            [5] SUPER TREND
            [6] MA vs SUPER_TREND
            [7] MA vs MACD
            [8] MA vs RSI
            [9] MA vs BOLLINGER BAND
            X[11] BOLLINGER BAND vs MACD
            [22] BOLLINGER BAND vs RSI
            [33] BOLLINGER vs SUPERTREND
            X[44] RSI vs SUPER TREND
            [55] MOVING AVERAGE vs BOLLINGER BAND vs MACD
            [66] MOVING AVERAGE vs BOLLINGER BAND vs RSI
            [77] MOVING AVERAGE vs BOLLINGER BAND vs SUPER TREND
            [88] MOVING AVERAGE vs BOLLINGER BAND vs MACD vs RSI
            [99] MOVING AVERAGE vs BOLLINGER BAND vs MACD vs SUPER TREND
            [111] MOVING AVERAGE vs BOLLINGER BAND vs MACD vs RSI vs SUPER TREND
        :return type:
            signal saved to prediction table
        '''
        from os.path import join
        if not os.path.exists(path + '/PREDICTED/{}'.format(TIMEFRAME)):
          os.makedirs(path + '/PREDICTED/{}'.format(TIMEFRAME))
#        for ii in STOCKLIST:
        datapath = join(path, 'DATASETS/{}/'.format(STOCK))
        #-------get the data we need------------------
        df = loc.read_csv(join(datapath, STOCK + '_{}'.format(TIMEFRAME) + str('.csv')))
        stock_data = stock(df)
        if strategy == '1':
            MA_alphbeta = signalStrategy().MA_signal(stock_data, ema = True, period_alpha=PERIOD_ALPHA, period_beta=PERIOD_BETA)
            signal = Signal().tradingSignal(df, MA = MA_alphbeta, strategy = strategy)
        elif strategy == '2':
            df_BB = signalStrategy().bollinger_band_signal(df, PERIOD, deviation = DEVIATION)
            signal = Signal().tradingSignal(df, Bollinger_Band = df_BB, strategy = strategy)
        elif strategy == '3':
            df_MACD = signalStrategy().macd_crossOver(df, FAST, SLOW, SIGNAL)
            signal = Signal().tradingSignal(df, MACD = df_MACD, strategy = strategy)
        elif strategy == '4':
            df_RSI = signalStrategy().RSI_signal(df, PERIOD, lw_bound = LOWER_BOUND, up_bound = UPPER_BOUND)
            signal = Signal().tradingSignal(df, RSI = df_RSI, strategy = strategy)
        elif strategy == '5':
            df_STrend = signalStrategy().SuperTrend_signal(df, MULTIPLIER, PERIOD)
            signal = Signal().tradingSignal(df, SuperTrend = df_STrend, strategy = strategy)
        elif strategy == '6':
            MA_alphbeta = signalStrategy().MA_signal(stock_data, ema = True, period_alpha=PERIOD_ALPHA, period_beta=PERIOD_BETA)
            df_STrend = signalStrategy().SuperTrend_signal(df, MULTIPLIER, PERIOD)
            signal = Signal().tradingSignal(df, SuperTrend = df_STrend, MA = MA_alphbeta, strategy = strategy)
        elif strategy == '7':
            MA_alphbeta = signalStrategy().MA_signal(stock_data, ema = True, period_alpha=PERIOD_ALPHA, period_beta=PERIOD_BETA)
            df_MACD = signalStrategy().macd_crossOver(df, FAST, SLOW, SIGNAL)
            signal = Signal().tradingSignal(df, MACD = df_MACD, MA = MA_alphbeta, strategy = strategy)
        elif strategy == '8':
            MA_alphbeta = signalStrategy().MA_signal(stock_data, ema = True, period_alpha=PERIOD_ALPHA, period_beta=PERIOD_BETA)
            df_RSI = signalStrategy().RSI_signal(df, PERIOD, lw_bound = LOWER_BOUND, up_bound = UPPER_BOUND)
            signal = Signal().tradingSignal(df, RSI = df_RSI, MA = MA_alphbeta, strategy = strategy)
        elif strategy == '9':
            MA_alphbeta = signalStrategy().MA_signal(stock_data, ema = True, period_alpha=PERIOD_ALPHA, period_beta=PERIOD_BETA)
            df_BB = signalStrategy().bollinger_band_signal(df, PERIOD, deviation = DEVIATION)
            signal = Signal().tradingSignal(df, Bollinger_Band = df_BB, MA = MA_alphbeta, strategy = strategy)
        elif strategy == '11':
            df_BB = signalStrategy().bollinger_band_signal(df, PERIOD, deviation = DEVIATION)
            df_MACD = signalStrategy().macd_crossOver(df, FAST, SLOW, SIGNAL)
            signal = Signal().tradingSignal(df, Bollinger_Band= df_BB, MACD = df_MACD, strategy = strategy)
        elif strategy == '22':
            df_BB = signalStrategy().bollinger_band_signal(df, PERIOD, deviation = DEVIATION)
            df_RSI = signalStrategy().RSI_signal(df, PERIOD, lw_bound = LOWER_BOUND, up_bound = UPPER_BOUND)
            signal = Signal().tradingSignal(df, Bollinger_Band= df_BB, RSI = df_RSI, strategy = strategy)
        elif strategy == '33':
            df_BB = signalStrategy().bollinger_band_signal(df, PERIOD, deviation = DEVIATION)
            df_STrend = signalStrategy().SuperTrend_signal(df, MULTIPLIER, PERIOD)
            signal = Signal().tradingSignal(df, Bollinger_Band= df_BB, SuperTrend= df_RSI, strategy = strategy)
        elif strategy == '44':
            df_RSI = signalStrategy().RSI_signal(df, PERIOD, lw_bound = LOWER_BOUND, up_bound = UPPER_BOUND)
            df_STrend = signalStrategy().SuperTrend_signal(df, MULTIPLIER, PERIOD)
            signal = Signal().tradingSignal(df, RSI= df_RSI, SuperTrend= df_STrend, strategy = strategy)
        elif strategy == '55':
            MA_alphbeta = signalStrategy().MA_signal(stock_data, ema = True, period_alpha=PERIOD_ALPHA, period_beta=PERIOD_BETA)
            df_BB = signalStrategy().bollinger_band_signal(df, PERIOD, deviation = DEVIATION)
            df_MACD = signalStrategy().macd_crossOver(df, FAST, SLOW, SIGNAL)
            signal = Signal().tradingSignal(df, MA= MA_alphbeta, Bollinger_Band= df_BB, MACD=df_MACD, strategy = strategy)
        elif strategy == '66':
            MA_alphbeta = signalStrategy().MA_signal(stock_data, ema = True, period_alpha=PERIOD_ALPHA, period_beta=PERIOD_BETA)
            df_BB = signalStrategy().bollinger_band_signal(df, PERIOD, deviation = DEVIATION)
            df_RSI = signalStrategy().RSI_signal(df, PERIOD, lw_bound = LOWER_BOUND, up_bound = UPPER_BOUND)
            signal = Signal().tradingSignal(df, MA= MA_alphbeta, Bollinger_Band= df_BB, RSI=df_RSI, strategy = strategy)
        elif strategy == '77':
            MA_alphbeta =signalStrategy().MA_signal(stock_data, ema = True, period_alpha=PERIOD_ALPHA, period_beta=PERIOD_BETA)
            df_BB = signalStrategy().bollinger_band_signal(df, PERIOD, deviation = DEVIATION)
            df_STrend = signalStrategy().SuperTrend_signal(df, MULTIPLIER, PERIOD)
            signal = Signal().tradingSignal(df, MA= MA_alphbeta, Bollinger_Band= df_BB, SuperTrend=df_STrend, strategy = strategy)
        elif strategy == '88':
            MA_alphbeta = signalStrategy().MA_signal(stock_data, ema = True, period_alpha=PERIOD_ALPHA, period_beta=PERIOD_BETA)
            df_BB = signalStrategy().bollinger_band_signal(df, PERIOD, deviation = DEVIATION)
            df_MACD = signalStrategy().macd_crossOver(df, FAST, SLOW, SIGNAL)
            df_RSI = signalStrategy().RSI_signal(df, PERIOD, lw_bound = LOWER_BOUND, up_bound = UPPER_BOUND)
            signal = Signal().tradingSignal(df, MA= MA_alphbeta, Bollinger_Band= df_BB, MACD=df_MACD, RSI=df_RSI, strategy = strategy)
        elif strategy == '99':
            MA_alphbeta = signalStrategy().MA_signal(stock_data, ema = True, period_alpha=PERIOD_ALPHA, period_beta=PERIOD_BETA)
            df_BB = signalStrategy().bollinger_band_signal(df, PERIOD, deviation = DEVIATION)
            df_MACD = signalStrategy().macd_crossOver(df, FAST, SLOW, SIGNAL)
            df_STrend = signalStrategy().SuperTrend_signal(df, MULTIPLIER, PERIOD)
            signal = Signal().tradingSignal(df, MA= MA_alphbeta, Bollinger_Band= df_BB, MACD=df_MACD, SuperTrend=df_STrend, strategy = strategy)
        elif strategy == '111':
            MA_alphbeta = signalStrategy().MA_signal(stock_data, ema = True, period_alpha=PERIOD_ALPHA, period_beta=PERIOD_BETA)
            df_BB = signalStrategy().bollinger_band_signal(df, PERIOD, deviation = DEVIATION)
            df_MACD = signalStrategy().macd_crossOver(df, FAST, SLOW, SIGNAL)
            df_RSI = signalStrategy().RSI_signal(df, PERIOD, lw_bound = LOWER_BOUND, up_bound = UPPER_BOUND)
            df_STrend = signalStrategy().SuperTrend_signal(df, MULTIPLIER, PERIOD)
            signal = Signal().tradingSignal(df, MA= MA_alphbeta, Bollinger_Band= df_BB, MACD=df_MACD, RSI=df_RSI, SuperTrend=df_STrend, strategy = strategy)
        else:
            pass
    
        print('*'*40)
        print('Signal generation completed...')
        print('*'*40)
        print('Saving file')
        #---strategy selection-----
        loc.set_path(path+ '/PREDICTED/{}'.format(TIMEFRAME))
        signal.to_csv('{}'.format(STOCK)+ '.csv', mode='w')


class Run(object):
    def __init__(self, path, strategy, STOCKLIST, DEVIATION, PERIOD, LOWER_BOUND,\
                 UPPER_BOUND, MIDLINE, FAST, SLOW, SIGNAL, TIMEFRAME,\
                 PERIOD_ALPHA, PERIOD_BETA, timer):
        
        self.path = path
        self.strategy = strategy
        self.STOCKLIST = STOCKLIST
        self.DEVIATION = DEVIATION
        self.PERIOD = PERIOD
        self.LOWER_BOUND = LOWER_BOUND
        self.UPPER_BOUND = UPPER_BOUND
        self.MIDLINE = MIDLINE
        self.FAST = FAST
        self.SLOW = SLOW
        self.SIGNAL = SIGNAL
        self.TIMEFRAME = TIMEFRAME
        self.PERIOD_ALPHA = PERIOD_ALPHA
        self.PERIOD_BETA = PERIOD_BETA
        self.timer = timer
        try:
            if self.STOCKLIST is None:
                raise ValueError('Incorrect stock name\n Enter atleast one stock name or fx pair')
            else:
                thread = []
                for ii, stkList in enumerate(self.STOCKLIST):
                    thread.append(multiprocessing.Process(target = self.runMain, args = [stkList]))
                for trd in thread:
                    trd.daemon = True
                    trd.start()
                for st_trd in thread:
                    st_trd.join()
        except Exception:
            raise ValueError('Thread unable to start')
            
    def runSignal(self, stkname):
        return Signal().main(path = self.path, strategy = self.strategy, STOCK = stkname, DEVIATION = self.DEVIATION, PERIOD = self.PERIOD, LOWER_BOUND = self.LOWER_BOUND,\
              UPPER_BOUND = self.UPPER_BOUND, MIDLINE = self.MIDLINE, FAST = self.FAST, SLOW = self.SLOW, SIGNAL = self.SIGNAL, TIMEFRAME = self.TIMEFRAME,\
              PERIOD_ALPHA = self.PERIOD_ALPHA, PERIOD_BETA = self.PERIOD_BETA)
        
    def runMain(self, stkname):
        self.stkname = stkname
        while True:
            if not self.path:
                break
            elif not self.strategy:
                raise ValueError('Strategy not define')
            elif not self.DEVIATION:
                raise ValueError('DEVIATION required')
            elif not self.PERIOD:
                raise ValueError('PERIOD required')
            elif not self.LOWER_BOUND:
                raise ValueError('LOWER_BOUND required')
            elif not self.UPPER_BOUND:
                raise ValueError('UPPER_BOUND required')
            elif not self.FAST:
                raise ValueError('FAST required')
            elif not self.SLOW:
                raise ValueError('SLOW required')
            elif not self.SIGNAL:
                raise ValueError('SIGNAL required')
            elif not self.TIMEFRAME:
                raise ValueError('TIMEFRAME required')
            elif not self.PERIOD_ALPHA:
                raise ValueError('PERIOD_ALPHA required')
            elif not self.PERIOD_BETA:
                raise ValueError('PERIOD_BETA required')
            else:
                self.runSignal(self.stkname)
            print('program running in background')
            time.sleep(self.timer)
        
            
#%% main script 
if __name__ == '__main__':
  import multiprocessing
  import time
  #---------GLOBAL SETTINGS-------------------
  path = '/home/kenneth/Documents/GIT_PROJECTS/AI-Signal-Generator'
  STRATEGY = '111'
  DEVIATION = MULTIPLIER = 2
  PERIOD = 20
  #---------MA SETTINGS--------------
  PERIOD_ALPHA = 10
  PERIOD_BETA = 20
  #--------RSI_SETTINGS------------------------
  LOWER_BOUND = 30
  UPPER_BOUND = 70
  MIDLINE = 0
  FILLCOLOR = 'skyblue'
  #--------MACD SETTINGS-----------------------
  FAST = 12
  SLOW = 26
  SIGNAL = 9
  TIMEFRAME = 'H1'
  instrument = ['EUR_USD', 'GBP_USD', 'AUD_CAD', 'AUD_USD',
                'BTC_USD', 'EUR_CAD', 'EUR_GBP', 'EUR_NZD',
                'NZD_USD']
  
  Run(path = path, strategy = STRATEGY, STOCKLIST = instrument, DEVIATION = DEVIATION, PERIOD = PERIOD, LOWER_BOUND = LOWER_BOUND,\
         UPPER_BOUND = UPPER_BOUND, MIDLINE = MIDLINE, FAST = FAST, SLOW = SLOW, SIGNAL = SIGNAL, TIMEFRAME = TIMEFRAME,\
         PERIOD_ALPHA = PERIOD_ALPHA, PERIOD_BETA = PERIOD_BETA, timer = 1800)
  


    
    
    
    
    
    
