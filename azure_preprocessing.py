
"""
Created on Thu Jun  6 11:07:24 2024

@author: repps
"""
from main import WindowClass, SectionWindow
import plaintextdictionary

import time
import os
import json
import numpy as np
import dill as pickle
from azure.ai.translation.text import TextTranslationClient, TranslatorCredential
from azure.ai.translation.text.models import InputTextItem

def savejson(entry, filepath):
    with open(filepath, 'w') as outfile:
        json.dump(entry, outfile)
        
def savepickle(entry, filepath):
    with open(filepath, 'wb') as outfile:
        pickle.dump(entry, outfile)
        
class language():
    def __init__(self):
        self.ui = WindowClass()
        self.processedfilepath = 'preprocessing//multilingual_dict.pkl'
        langkeys = ['en', 'zh-Hans', 'tlh-Latn', 'ar', 'bn', 'cs', 'da', 'de', 'el', 'es',
                    'fi', 'fil', 'fr', 'he', 'hi', 'hr', 'id', 'it', 'ja', 'ko',
                    'nb', 'ne', 'pa', 'pl', 'ps', 'pt', 'ro', 'ru', 'th', 'uk',
                    'ur', 'vi', 'yue', 'sv']
        self.translator = TextTranslationClient(credential = TranslatorCredential(
            "< azure key hidden >", "eastus2"))

        
        self.languages = {}
        alllanguages = self.translator.get_languages()
        for key, value in alllanguages.translation.items():
            self.languages[key] = value
        sort_languages = []
        for langkey in langkeys:
            sort_languages.append(self.languages[langkey].name)
        sort_ind = np.argsort(sort_languages)
        self.langkeys = []
        for ii in sort_ind:
            self.langkeys.append(langkeys[ii])
            
    def saveProcessedLanguageDict(self):
        self.buildBabelFishDict()
        self.saveBabelFishasPickle()
        
    def saveBabelFishasJSON(self):
        savejson(self.babelFishDict, self.processedfilepath)
        
    def saveBabelFishasPickle(self):
        savepickle(self.babelFishDict, self.processedfilepath)

    def buildBabelFishDict(self):
        self.ui.getInterfaceWidgetsText()
        self.getSectionTextList()
        self.getSceneContextMenuTextList()
        self.getNewBlockMenuTextList()
        self.getPlainTextConstantsList()
        
        self.initializeBabelFishDict()
        self.translateTextList()
        
        self.addBlockDict()

    def initializeBabelFishDict(self):
        self.babelFishDict = {}
        self.babelFishDict['languages'] = {}
        for langkey in self.langkeys:
            self.babelFishDict['languages'][langkey] = {}
            lang_en = self.languages[langkey].name
            self.babelFishDict['languages'][langkey]['Language en'] = lang_en
            lang_nat = self.languages[langkey].native_name
            self.babelFishDict['languages'][langkey]['Language nat'] = lang_nat
            self.babelFishDict['languages'][langkey]['Menu label'] = lang_nat + ' [' + lang_en + ']'
        
    def translateTextList(self):
        self.babelFishDict['ui'] = {}
        for langkey in self.langkeys:
            print(langkey)
            self.babelFishDict['ui'][langkey] = {}
            
            input_text_elements = [InputTextItem(text=itm) for itm in self.ui.allwidgetstext]
            response = self.translator.translate(
                content = input_text_elements,
                to = [langkey],
                from_parameter = 'en')
            textlist = [val.translations[0].text for val in response]
            self.babelFishDict['ui'][langkey]['widgets'] = textlist
            print(textlist)
            time.sleep(0.5)
            
            input_text_elements = [InputTextItem(text=itm) for itm in self.sectionTextList_en]
            response = self.translator.translate(
                content = input_text_elements,
                to = [langkey],
                from_parameter = 'en')
            textlist = [val.translations[0].text for val in response]
            self.babelFishDict['ui'][langkey]['section'] = textlist
            print(textlist)
            time.sleep(0.5)
            
            input_text_elements = [InputTextItem(text=itm) for itm in self.sceneContextMenuTextList_en]
            response = self.translator.translate(
                content = input_text_elements,
                to = [langkey],
                from_parameter = 'en')
            textlist = [val.translations[0].text for val in response]
            self.babelFishDict['ui'][langkey]['scene context'] = textlist
            print(textlist)
            time.sleep(0.5)
            
            input_text_elements = [InputTextItem(text=itm) for itm in self.newBlockMenuTextList_en]
            response = self.translator.translate(
                content = input_text_elements,
                to = [langkey],
                from_parameter = 'en')
            textlist = [val.translations[0].text for val in response]
            self.babelFishDict['ui'][langkey]['new block'] = textlist
            print(textlist)
            time.sleep(0.5)
            
            input_text_elements = [InputTextItem(text=itm) for itm in self.plainTextConstantsList_en]
            response = self.translator.translate(
                content = input_text_elements,
                to = [langkey],
                from_parameter = 'en')
            textlist = [val.translations[0].text for val in response]
            self.babelFishDict['ui'][langkey]['plain text const'] = textlist
            print(textlist)
            time.sleep(0.5)
            
    def getSectionTextList(self):
        self.sectionTextList_en = ['Section Name:',
                                   'Section Description:', 
                                   'Confirm', 
                                   'Cancel']
        
    def getSceneContextMenuTextList(self):
        self.sceneContextMenuTextList_en = ['Create Action Block',
                                            'Create Item Block',
                                            'Create Section Block',
                                            'Insert from File',
                                            'Insert from File as Section',
                                            'Add A-Type Connections',
                                            'Add B-Type Connections',
                                            'Add C-Type Connections',
                                            'Copy',
                                            'Paste',
                                            'Select All',
                                            'Delete']
        
    def getNewBlockMenuTextList(self):
        self.newBlockMenuTextList_en = ['New Action Block Entry',
                                        'New Item Block Entry',
                                        'Block Class:',
                                        'Block Sub-Class:',
                                        'Name:',
                                        'Linked Item:',
                                        'Link ID:',
                                        'Parameters',
                                        'Values',
                                        '+ Add Parameter',
                                        'Notes:',
                                        'Confirm',
                                        'Cancel',
                                        'The data in this block will be linked to the selected link ID.',
                                        'All other data in this block will be overwritten.\n',
                                        'Would you like to continue?',
                                        'Yes',
                                        'No',
                                        'Action',
                                        'Item']
        
    def getPlainTextConstantsList(self):
        self.plainTextConstantsList_en = ['Protocol Generation Error',
                                          'Experiment Name:',
                                          'Experiment Description:',
                                          'Base Information Transcription Error',
                                          'Additional Information',
                                          'Additional Information List Transcription Error',
                                          'Materials',
                                          'Materials List Transcription Error',
                                          'Equipment',
                                          'Equipment List Transcription Error',
                                          'Procedure',
                                          'Action Transcription Error',
                                          'Protocol List Transcription Error',
                                          'Error',
                                          'and']
        
    def addBlockDict(self):
        self.initializeBabelFishBlockDict()
        for langkey in self.langkeys:
            self.addLanguageBlockDict(langkey)
    
    def initializeBabelFishBlockDict(self):
        self.blockdict = plaintextdictionary.loadDictionary()
        self.initializeActionBabelFishDict()
        self.initializeItemBabelFishDict()
        self.initializeParamBabelFishDict()
    
    def initializeActionBabelFishDict(self):
        self.babelFishDict['Action'] = {}
        actDict = self.blockdict['Action'].copy()
        for typekey in actDict.keys():
            for namekey in actDict[typekey].keys():
                self.babelFishDict['Action'][namekey] = {}
                for langkey in self.langkeys:
                    self.babelFishDict['Action'][namekey][langkey] = {}
                
    def initializeItemBabelFishDict(self):
        self.babelFishDict['Item'] = {}
        itemDict = self.blockdict['Item'].copy()
        for typekey in itemDict.keys():
            for namekey in itemDict[typekey]:
                self.babelFishDict['Item'][namekey] = {}
                for langkey in self.langkeys:
                    self.babelFishDict['Item'][namekey][langkey] = {}
                    
    def initializeParamBabelFishDict(self):
        self.babelFishDict['Action Parameter'] = {}
        paramDict = self.blockdict['Action Parameter'].copy()
        for namekey in paramDict:
            self.babelFishDict['Action Parameter'][namekey] = {}
            for langkey in self.langkeys:
                self.babelFishDict['Action Parameter'][namekey][langkey] = {}
                
        self.babelFishDict['Item Parameter'] = {}
        paramDict = self.blockdict['Item Parameter'].copy()
        for namekey in paramDict:
            self.babelFishDict['Item Parameter'][namekey] = {}
            for langkey in self.langkeys:
                self.babelFishDict['Item Parameter'][namekey][langkey] = {}
    
    def addLanguageBlockDict(self, langkey):
        self.addActionLanguageBlockDict(langkey)
        self.addItemLanguageBlockDict(langkey)
        self.addParamLanguageBlockDict(langkey)
        
    def addActionLanguageBlockDict(self, langkey):
        actDict = self.blockdict['Action'].copy()
        for typeKey in actDict.keys():
            input_text_elements = [InputTextItem(text=namekey) for namekey in actDict[typeKey].keys()]
            response = self.translator.translate(
                content = input_text_elements,
                to = [langkey],
                from_parameter = 'en')
            time.sleep(1)
            textlist = [val.translations[0].text for val in response]
            for ii, namekey in enumerate(actDict[typeKey].keys()):
                self.babelFishDict['Action'][namekey][langkey]['Name'] = textlist[ii]
                self.babelFishDict['Action'][namekey][langkey]['Func'] = {}
            print(textlist)
            
            input_text_elements = []
            keypairs = []
            for nameKey in actDict[typeKey].keys():
                for actKey in actDict[typeKey][nameKey].keys():
                    keypairs.append([nameKey, actKey])
                    funcoutstr = actDict[typeKey][nameKey][actKey]('{x}','{y}','{z}')
                    input_text_elements.append(InputTextItem(text=funcoutstr))
            
            if langkey != 'tlh-Latn':
                response = self.translator.translate(
                    content = input_text_elements,
                    to = [langkey],
                    from_parameter = 'en')
            else:
                response = self.translator.translate(
                    content = input_text_elements,
                    to = ['en'],
                    from_parameter = 'en')
            time.sleep(1)
            textlist = [val.translations[0].text for val in response]
            print(textlist)
            for ii, keypair in enumerate(keypairs):
                func = eval('lambda x, y, z: f"' + textlist[ii] + '"')
                self.babelFishDict['Action'][keypair[0]][langkey]['Func'][keypair[1]] = func
            print(textlist)

    def addItemLanguageBlockDict(self, langkey):
        itemDict = self.blockdict['Item'].copy()
        for typeKey in itemDict.keys():
            input_text_elements = [InputTextItem(text = namekey) for namekey in itemDict[typeKey]]
            response = self.translator.translate(
                content = input_text_elements,
                to = [langkey],
                from_parameter = 'en')
            textlist = [val.translations[0].text for val in response]
            print(textlist)
            for ii, namekey in enumerate(itemDict[typeKey]):
                self.babelFishDict['Item'][namekey][langkey]['Name'] = textlist[ii]
            time.sleep(3)
                
    def addParamLanguageBlockDict(self, langkey):
        paramDict = self.blockdict['Action Parameter'].copy()
        
        input_text_elements = [InputTextItem(text = namekey) for namekey in paramDict]
        response = self.translator.translate(
            content = input_text_elements,
            to = [langkey],
            from_parameter = 'en')
        textlist = [val.translations[0].text for val in response]
        
        for ii, namekey in enumerate(paramDict):
            self.babelFishDict['Action Parameter'][namekey][langkey]['Name'] = textlist[ii]
        print(textlist)
        time.sleep(3)
            
        paramDict = self.blockdict['Item Parameter'].copy()
        
        input_text_elements = [InputTextItem(text = namekey) for namekey in paramDict]
        response = self.translator.translate(
            content = input_text_elements,
            to = [langkey],
            from_parameter = 'en')
        textlist = [val.translations[0].text for val in response]
        
        for ii, namekey in enumerate(paramDict):
            self.babelFishDict['Item Parameter'][namekey][langkey]['Name'] = textlist[ii]
        print(textlist)
        time.sleep(3)


language().saveProcessedLanguageDict()
