#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  27 16:30:21 2019

@author: kennedy
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
import datetime

class Path(object):
    def __init__(self, path):
        self.path = path
        self.loadPath()
        
    def loadPath(self):
      import os
      try:
        if os.path.exists(self.path['mainPath']):
          try:
            FOLDERS = ['/DATASETS', 
                       '/PREDICTED', 
                       '/IMAGES',
                       '/TICKERS',
                       '/MODEL',
                       '/SIGNALS']
            FOLDER_COUNT = 0
            for folders in FOLDERS:
              '''If folder is not created or created but deleted..Recreate/Create the folder.
              Check for all folders in the FOLDERS list'''
              if not os.path.exists(self.path['mainPath'] + FOLDERS[FOLDER_COUNT]):
                os.makedirs(self.path['mainPath'] + FOLDERS[FOLDER_COUNT])
                print('====== 100% Completed ==== : {}'.format(self.path['mainPath'] + FOLDERS[FOLDER_COUNT]))
                FOLDER_COUNT += 1
              elif os.path.exists(self.path['mainPath'] + FOLDERS[FOLDER_COUNT]):
                '''OR check if the file is already existing using a boolean..if true return'''
                print('File Already Existing : {}'.format(self.path['mainPath'] + FOLDERS[FOLDER_COUNT]))
                FOLDER_COUNT += 1
          except OSError as e:
              '''raise OSError('File Already Existing {}'.format(e))'''
              print('File Already existing: {}'.format(e))
        elif not os.path.exists(self.path['mainPath']):
            raise OSError('File self.path: {} does not exist\n\t\tPlease check the self.path again'.format(self.path['mainPath']))
        else:
            print('File Already Existing')
      except Exception as e:
          raise(e)
      finally:
          print('Process completed...Exiting')


class stockDownload:
    def __init__(self, path, instrument, start, end, client, timeframe):
        self.path = path
        self.instrument = instrument
        self.start = start
        self.end = end
        self.client = client
        self.timeframe = timeframe
        self.downloadStockData()
        
    def downloadStockData(self):
        '''
          :Arguments:
            :instruments:
              Name of the instrument we are trading
            :start: specify the start date of stcok to download
            :end: specify end date of the stock to download
            
          :Returntype:
            return the csv file of the downloaded stock in the
            specific folder.
        '''
        from oandapyV20.contrib.factories import InstrumentsCandlesFactory
        def covert_json(reqst, frame):
            for candle in reqst.get('candles'):
                ctime = candle.get('time')[0:19]
                try:
                    #--Only download closed candle
                    if not candle['complete']:
                        pass
                    else:
                        rec = '{time},{complete},{o},{h},{l},{c},{v}'.format(time = ctime,
                               complete = candle['complete'],
                               o = candle['mid']['o'],
                               h = candle['mid']['h'],
                               l = candle['mid']['l'],
                               c = candle['mid']['c'],
                               v = candle['volume'])
                except Exception as e:
                    raise(e)
                else:
                    frame.write(rec+'\n')
                
                
        #try except to both create folder and enter ticker
        try:
            #create folder for all instruments
            if not os.path.exists(self.path['mainPath'] + f'/DATASETS/{self.instrument}'):
                os.makedirs(self.path['mainPath'] + f'/DATASETS/{self.instrument}')
            #import the required timeframe
            with open(self.path['mainPath'] + '/DATASETS/{}/{}_{}.csv'.format(self.instrument, self.instrument, self.timeframe), 'w') as OUTPUT:
                params = {'from': self.start,
                          'to': self.end,
                          'granularity': self.timeframe,
                          }
                try:
                  for ii in InstrumentsCandlesFactory(instrument = self.instrument, params = params):
                      print("REQUEST: {} {} {}".format(ii, ii.__class__.__name__, ii.params))
                      self.client.request(ii)
                      covert_json(ii.response, OUTPUT)
                except:
                    print('{} not available using this API\n Please check your internet connection'.format(self.instrument))
                print('********************Done downloading******************\n{}_{}\n'.format(self.instrument, self.timeframe))
        except Exception as e:
            raise(e)
        finally:
            print('*'*40)
            print('Stock download completed')
            print('*'*40)

class Runcollector:
    def __init__(self, path, start, end, client, timeframe):
        self.path = path
        self.start = start
        self.end = end
        self.client = client
        self.timeframe = timeframe
        self.runnewMain()

    def loadData(self):
        import multiprocessing
        threads = []
        for instr in self.path['instruments'].split(','):
            threads.append(multiprocessing.Process(target = stockDownload, args = (self.path, instr, self.start,
                                                                                   self.end, self.client, self.timeframe)))
        for trd in threads:
            trd.daemon = True
            trd.start()
        for st_trd in threads:
            st_trd.join()
                
    def runnewMain(self):
        import time
        return self.loadData()
          
        
