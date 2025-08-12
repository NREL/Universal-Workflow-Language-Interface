
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
from openai import OpenAI
from typing import List, Dict, Any

def savejson(entry, filepath):
    with open(filepath, 'w') as outfile:
        json.dump(entry, outfile)
        
def savepickle(entry, filepath):
    with open(filepath, 'wb') as outfile:
        pickle.dump(entry, outfile)
        
class language():
    def __init__(self):
        self.processedfilepath = 'preprocessing//multilingual_dict.pkl'
        # langkeys = ['zh-cn', 'es', 'en', 'hi', 'pt', 'bn', 'ru', 'ja', 'vi', 'tr', 'mr', 'te', 'ko', 'fr', 'ta', 'ar', 'de', 'ur', 'jw', 'pa', 'it', 'gu', 'fa']
        # langkeys = ['zh-Hans', 'en',]
        langkeys = ['en', 'zh-Hans', 'tlh-Latn', 'ar', 'bn', 'cs', 'da', 'de', 'el', 'es',
                    'fi', 'fil', 'fr', 'he', 'hi', 'hr', 'id', 'it', 'ja', 'ko',
                    'nb', 'ne', 'pa', 'pl', 'ps', 'pt', 'ro', 'ru', 'th', 'uk',
                    'ur', 'vi', 'yue', 'sv']
        
        # Initialize OpenAI client
        # Load OpenAI API key from a fixed file path text file that only contains the key
        api_key_path = "C:/Users/repps/OneDrive - NREL/Desktop/openai_key.txt"
        with open(api_key_path, "r") as key_file:
            api_key = key_file.read().strip()
        
        self.client = OpenAI(api_key=api_key)
        
        # Language mapping for OpenAI (using ISO 639-1 codes)
        self.language_mapping = {
            'en': 'English',
            'zh-Hans': 'Chinese (Simplified)',
            'tlh-Latn': 'Klingon (Latin)',
            'ar': 'Arabic',
            'bn': 'Bengali',
            'cs': 'Czech',
            'da': 'Danish',
            'de': 'German',
            'el': 'Greek',
            'es': 'Spanish',
            'fi': 'Finnish',
            'fil': 'Filipino',
            'fr': 'French',
            'he': 'Hebrew',
            'hi': 'Hindi',
            'hr': 'Croatian',
            'id': 'Indonesian',
            'it': 'Italian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'nb': 'Norwegian Bokmål',
            'ne': 'Nepali',
            'pa': 'Punjabi',
            'pl': 'Polish',
            'ps': 'Pashto',
            'pt': 'Portuguese',
            'ro': 'Romanian',
            'ru': 'Russian',
            'th': 'Thai',
            'uk': 'Ukrainian',
            'ur': 'Urdu',
            'vi': 'Vietnamese',
            'yue': 'Cantonese',
            'sv': 'Swedish'
        }
        
        self.languages = {}
        for key in langkeys:
            self.languages[key] = type('Language', (), {
                'name': self.language_mapping.get(key, key),
                'native_name': self.language_mapping.get(key, key)
            })()
        
        sort_languages = []
        for langkey in langkeys:
            sort_languages.append(self.languages[langkey].name)
        sort_ind = np.argsort(sort_languages)
        self.langkeys = []
        for ii in sort_ind:
            self.langkeys.append(langkeys[ii])
    
    def translate_texts_with_openai(self, texts: List[str], target_language: str) -> List[str]:
        """
        Translate a list of texts using OpenAI's GPT-4o-mini model.
        If the list has more than 20 items, process it in chunks.
        
        Args:
            texts: List of English texts to translate
            target_language: Target language code (e.g., 'es', 'fr', 'de')
            
        Returns:
            List of translated texts
        """
        if not texts:
            return []
        
        # If list has more than 20 items, process in chunks
        if len(texts) > 20:
            print(f"Processing {len(texts)} items in chunks of 20...")
            all_translated = []
            chunk_size = 20
            
            for i in range(0, len(texts), chunk_size):
                chunk = texts[i:i + chunk_size]
                print(f"Processing chunk {i//chunk_size + 1}/{(len(texts) + chunk_size - 1)//chunk_size} ({len(chunk)} items)")
                translated_chunk = self._translate_chunk(chunk, target_language, i)
                all_translated.extend(translated_chunk)
                time.sleep(1)  # Rate limiting between chunks
            
            return all_translated
        else:
            return self._translate_chunk(texts, target_language, 0)
    
    def _translate_chunk(self, texts: List[str], target_language: str, start_index: int) -> List[str]:
        """
        Translate a chunk of texts (up to 20 items) using OpenAI's GPT-4o-mini model.
        
        Args:
            texts: List of English texts to translate (max 20 items)
            target_language: Target language code
            start_index: Starting index for numbering in the prompt
            
        Returns:
            List of translated texts
        """
        target_lang_name = self.language_mapping.get(target_language, target_language)
        
        # Create a single prompt for all texts in the chunk
        text_list = '\n'.join([f"{i+1}. {text}" for i, text in enumerate(texts)])
        
        prompt = f"""Translate the following {len(texts)} English texts to {target_lang_name}. 
Return ONLY the translated texts in the same order, one per line, WITHOUT any numbers, bullet points, or formatting.

IMPORTANT REQUIREMENTS:
1. Return exactly {len(texts)} translated texts
2. Each translation should be on its own line
3. Maintain the exact same order as the input
4. Do not include any numbers, bullets, or extra formatting
5. Ensure the output list has equal length to the input list

{text_list}

IMPORTANT: Return only the translated text, no numbers, no bullets, no extra formatting. The output must contain exactly {len(texts)} lines."""
        
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4.1-nano",
                    messages=[
                        {"role": "system", "content": "You are a professional translator. Translate accurately and maintain the original meaning and context. You must return exactly the same number of translations as input texts."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                )
                
                # Parse the response
                translated_text = response.choices[0].message.content.strip()
                translated_lines = [line.strip() for line in translated_text.split('\n') if line.strip()]
                
                # Clean up any remaining numbers or formatting
                cleaned_lines = []
                for line in translated_lines:
                    # Remove leading numbers, periods, and whitespace (e.g., "1. ", "2. ", etc.)
                    cleaned_line = line.strip()
                    # Remove patterns like "1. ", "2. ", "1)", "2)", etc.
                    import re
                    cleaned_line = re.sub(r'^\d+[\.\)]\s*', '', cleaned_line)
                    cleaned_lines.append(cleaned_line)
                
                translated_lines = cleaned_lines
                
                # Check if we have the same number of translations as input texts
                if len(translated_lines) == len(texts):
                    return translated_lines
                else:
                    print(f"Attempt {attempt + 1}/{max_attempts}: Expected {len(texts)} translations, got {len(translated_lines)}")
                    if attempt < max_attempts - 1:
                        print(f"Retrying translation...")
                        continue
                    else:
                        print(f"Final attempt failed. Padding/truncating to match expected length.")
                        # Pad with original text if we have fewer translations
                        while len(translated_lines) < len(texts):
                            translated_lines.append(texts[len(translated_lines)])
                        # Truncate if we have more translations
                        translated_lines = translated_lines[:len(texts)]
                        return translated_lines
                
            except Exception as e:
                print(f"Attempt {attempt + 1}/{max_attempts}: Error translating to {target_language}: {e}")
                if attempt < max_attempts - 1:
                    print(f"Retrying translation...")
                    continue
                else:
                    print(f"All attempts failed. Returning original texts as fallback.")
                    # Return original texts as fallback
                    return texts.copy()
            
    def saveProcessedLanguageDict(self):
        self.buildBabelFishDict()
        self.saveBabelFishasPickle()
        
    def saveBabelFishasJSON(self):
        savejson(self.babelFishDict, self.processedfilepath)
        
    def saveBabelFishasPickle(self):
        savepickle(self.babelFishDict, self.processedfilepath)

    def buildBabelFishDict(self):
        # Get all hardcoded interface labels
        self.interfaceLabels = [
            # Menu titles
            'File', 'Edit', 'Insert', 'View', 'Batch', 'Help', 'Language',
            'Table View', 'Feedback',
            
            # File menu actions
            'New', 'Open', 'Save', 'Save As', 'Save All', 'Test Button',
            
            # Edit menu actions
            'Copy', 'Paste', 'Select All', 'Delete',
            
            # Insert menu actions
            'Create Action Block', 'Create Item Block', 'Create Section Block',
            'Insert from File', 'Insert from File as Section',
            'Add A-Type Connections', 'Add B-Type Connections', 'Add C-Type Connections',
            
            # View menu actions
            'Show all cells', 'Show empty cells', 'Show unique cells',
            
            # Design menu actions
            'Design Experiment Set', 'Build Table Map', 'Import Table',
            
            # Help menu actions
            'Tutorial', 'Controls',
            
            # Tab names (these will be dynamic)
            'Workflows', 'Table', 'Protocol', 'Raw',
            
            # Additional labels found in the interface
            'Entry Name: ', 'File Path: ', 'Experiment Description:',
            
            # Additional hardcoded strings found in the code
            'Delete Column', 'Import and Save UWLs', 'Cancel', '?',
            'Invalid Table Format', 'The selected Excel file does not contain a \'Parameters\' column. Please ensure the table is formatted correctly and try again.',
            'The selected Excel file does not contain the required hidden columns (\'hidden_rootuwl\', \'hidden_keymap\'). Please ensure the table was generated by the UWLi export tool and try again.',
            'Invalid UWL', 'The root UWL could not be loaded from the table file. Please ensure the file was generated by the UWLi export tool and try again.',
            'Interface Controls',
            
            # Popup window texts - SectionWindow
            'New Section Info', '(Untitled)',
            
            # Popup window texts - NewSectionWindow
            'New Section Info',
            
            # Popup window texts - NewBlockWindow
            'New Action Block Entry', 'New Item Block Entry',
            
            # Popup window texts - ExperimentDesignWindow
            'Design Method:', 'Random', 'Grid', 'Latin Hypercube', 'Minimax',
            'Root UWL:', '** Select File to View Parameters **', 'Browse',
            'Root File Name:', 'Experiment_#', 'Number of New Experiments:',
            'Open File', 'UWL Entry (*.uwl *.json);;UWL Template (*.uwlt)',
            '+ Add Parameter', 'Parameter', 'Data Type', 'Scale', 'Units', 'Min Bound', 'Max Bound',
            'Discrete Levels', 'Levels', 'Categories', '+ Add Category', 'Delete Row',
            'Confirm', 'Cancel', 'Numerical-Continuous', 'Linear', 'Logarithmic',
            'Parameter:', 'Data Type:', 'Scale:', 'Units (optional):', 'Min Bound:', 'Max Bound:',
            'Numerical-Integer', 'Numerical-Discrete', 'Categorical', 'Log',
            'Container', 'Source', 'Tool', 'Abstract', 'Add', 'Remove', 'Modify',
            
            # Popup window texts - BuildTableMapWindow
            'Excel Table Export Tool', 'Root UWL:', '** Select File to View Parameters **', 'Browse',
            'Parameters to Export:', 'Include Headers', 'Export to Excel',
            'Help', 'Cancel', 'Open File', 'UWL Entry (*.uwl *.json);;UWL Template (*.uwlt)',
            'This tool exports workflow parameters to an Excel table for batch editing.',
            'The exported table contains hidden columns with the root UWL and parameter mapping.',
            'After editing the table, use the Import Table tool to create new UWLs.',
            'Generate Table', 'Save Formatted Table', 'No file selected', 'Please select a root UWL file.',
            
            # Popup window texts - TableMapImportWindow
            'Excel Table Import Tool', 'Browse Table File', 'Select a table file to view.',
            'Select Excel File', 'Excel Files (*.xlsx)', 'Invalid Table Format',
            'The selected Excel file could not be read. Please ensure the table is formatted correctly and try again.',
            'Edit Column Label', 'Enter new label for column \'{old_label}\':',
            'Import and Save UWLs', 'Cancel', 'Help',
            'No File Selected', 'Please select a table file to import experiments.',
            'This window is used to import a batch of UWLs that are formatted in excel. Use the Build Table Map tool to create an excel file that can be manually edited to adjust parameter values. The file contains two hidden columns containing the root UWL and a map for each parameter to that root UWL. Files that were not originally created using the build tool will most likely fail to import here.',
            '\'Import and Save UWLs\' will prompt you for a directory path and save your imported UWLs in a time stamped folder with the column headers corresponding to the file names.',
            

            
            # Error messages
            'Error', 'The selected file path is already open. Select a different path or close the open tab before proceeding.',
            'Save All Complete', 'Successfully saved {savedCount} file(s)', 'Save All Failed', 'Failed to save {errorCount} file(s).',
            'Save Error', 'Failed to save tab {tabIndex}: {error}', 'Failed to save tab', 'Failed to save', 'file(s)',
            
            # File dialog texts
            'Save File', 'UWL Entry (*.uwl);;UWL Template (*.uwlt)',
            'Save File for Tab {tabIndex}',
            'Save to Excel', 'Excel Files (*.xlsx);;All Files (*)', 'Select Directory',
            
            # Navigation button texts
            'Zoom In', 'Zoom Out', 'Zoom Fit', 'Pan Up', 'Pan Down', 'Pan Left', 'Pan Right',
            
            # Tutorial window texts
            'Tutorial', 'Quick Start', ' < ', ' > ',
            
            # Controls window texts
            'Workflow View Navigation', 'Pan Up - < Up Arrow > or < Scroll Down .', 'Pan Down - < Down Arrow > or < Scroll Up >',
            'Pan Left - < Left Arrow > or < Alt + Scroll Down >', 'Pan Right - < Right Arrow > or < Alt + Scroll Up >',
            'Faster Pan - < Shift + Command >', 'Zoom In - < Ctrl + Scroll Down >', 'Zoom Out - < Ctrl + Scroll Up >',
            'File Management', 'New File - File >> New or < Ctrl + N >', 'Open File - File >> Open or < Ctrl + O >',
            'Save File - File >> Save or < Ctrl + S >', 'Save File as - File >> Save as or < Ctrl + Shift + S >',
            'Block Placing', 'Place Action Block - Right click and select or < Shift + D >',
            'Place Item Block - Right click and select or < Shift + F >', 'Place Section Block - Right click and select or < Shift + G >',
            'Insert Blocks from File - Right click and select or < Ctrl + I >',
            'Insert Blocks from File as Section - Right click and select or < Ctrl + Shift + I >',
            'Block Connection (For all highlighted blocks)', 'Add A-Type Connections - Right click and select or < Shift + 1 >',
            'Add B-Type Connections - Right click and select or < Shift + 2 >', 'Add C-Type Connections - Right click and select or < Shift + 3 >',
            'Workflow Editing', 'Copy - Edit >> Copy, Right click and select, or < Ctrl + C >',
            'Paste - Edit >> Paste, Right click and select, or < Ctrl + V >',
            'Select All - Edit >> Copy, Right click and select, or < Ctrl + A >',
            'Delete - Edit >> Delete, Right click and select, or < Delete >',
            'Move Blocks - Click and drag', 'Highlight Blocks - Click and drag box or < Ctrl + Click >'
        ]
        
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
            print(f"Translating to {langkey}...")
            self.babelFishDict['ui'][langkey] = {}
            
            # Translate interface widgets
            textlist = self.translate_texts_with_openai(self.interfaceLabels, langkey)
            # Create dictionary with English keys
            self.babelFishDict['ui'][langkey]['widgets'] = {}
            for i, text in enumerate(textlist):
                if i < len(self.interfaceLabels):
                    self.babelFishDict['ui'][langkey]['widgets'][self.interfaceLabels[i]] = text
            print(f"Widgets translated: {textlist}")
            time.sleep(1)  # Rate limiting
            
            # Translate section texts
            textlist = self.translate_texts_with_openai(self.sectionTextList_en, langkey)
            # Create dictionary with English keys
            self.babelFishDict['ui'][langkey]['section'] = {}
            for i, text in enumerate(textlist):
                if i < len(self.sectionTextList_en):
                    self.babelFishDict['ui'][langkey]['section'][self.sectionTextList_en[i]] = text
            print(f"Section texts translated: {textlist}")
            time.sleep(1)
            
            # Translate scene context menu
            textlist = self.translate_texts_with_openai(self.sceneContextMenuTextList_en, langkey)
            # Create dictionary with English keys
            self.babelFishDict['ui'][langkey]['scene context'] = {}
            for i, text in enumerate(textlist):
                if i < len(self.sceneContextMenuTextList_en):
                    self.babelFishDict['ui'][langkey]['scene context'][self.sceneContextMenuTextList_en[i]] = text
            print(f"Scene context menu translated: {textlist}")
            time.sleep(1)
            
            # Translate new block menu
            textlist = self.translate_texts_with_openai(self.newBlockMenuTextList_en, langkey)
            # Create dictionary with English keys
            self.babelFishDict['ui'][langkey]['new block'] = {}
            for i, text in enumerate(textlist):
                if i < len(self.newBlockMenuTextList_en):
                    self.babelFishDict['ui'][langkey]['new block'][self.newBlockMenuTextList_en[i]] = text
            print(f"New block menu translated: {textlist}")
            time.sleep(1)
            
            # Translate plain text constants
            textlist = self.translate_texts_with_openai(self.plainTextConstantsList_en, langkey)
            # Create dictionary with English keys
            self.babelFishDict['ui'][langkey]['plain text const'] = {}
            for i, text in enumerate(textlist):
                if i < len(self.plainTextConstantsList_en):
                    self.babelFishDict['ui'][langkey]['plain text const'][self.plainTextConstantsList_en[i]] = text
            print(f"Plain text constants translated: {textlist}")
            time.sleep(1)
            
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
            # Translate action names
            action_names = list(actDict[typeKey].keys())
            textlist = self.translate_texts_with_openai(action_names, langkey)
            time.sleep(1)
            
            for ii, namekey in enumerate(action_names):
                self.babelFishDict['Action'][namekey][langkey]['Name'] = textlist[ii]
                self.babelFishDict['Action'][namekey][langkey]['Func'] = {}
            print(f"Action names translated: {textlist}")
            
            # Translate function outputs
            input_text_elements = []
            keypairs = []
            for nameKey in actDict[typeKey].keys():
                for actKey in actDict[typeKey][nameKey].keys():
                    keypairs.append([nameKey, actKey])
                    funcoutstr = actDict[typeKey][nameKey][actKey]('{x}','{y}','{z}')
                    input_text_elements.append(funcoutstr)
            
            if langkey != 'tlh-Latn':
                textlist = self.translate_texts_with_openai(input_text_elements, langkey)
            else:
                textlist = self.translate_texts_with_openai(input_text_elements, 'en')
            time.sleep(1)
            
            print(f"Function outputs translated: {textlist}")
            for ii, keypair in enumerate(keypairs):
                func = eval('lambda x, y, z: f"' + textlist[ii] + '"')
                self.babelFishDict['Action'][keypair[0]][langkey]['Func'][keypair[1]] = func

    def addItemLanguageBlockDict(self, langkey):
        itemDict = self.blockdict['Item'].copy()
        for typeKey in itemDict.keys():
            item_names = list(itemDict[typeKey])
            textlist = self.translate_texts_with_openai(item_names, langkey)
            print(f"Item names translated: {textlist}")
            for ii, namekey in enumerate(item_names):
                self.babelFishDict['Item'][namekey][langkey]['Name'] = textlist[ii]
            time.sleep(3)
                
    def addParamLanguageBlockDict(self, langkey):
        paramDict = self.blockdict['Action Parameter'].copy()
        
        # paramDict is a list, not a dictionary
        param_names = list(paramDict)
        textlist = self.translate_texts_with_openai(param_names, langkey)
        
        for ii, namekey in enumerate(param_names):
            self.babelFishDict['Action Parameter'][namekey][langkey]['Name'] = textlist[ii]
        print(f"Action parameter names translated: {textlist}")
        time.sleep(3)
            
        paramDict = self.blockdict['Item Parameter'].copy()
        
        # paramDict is a list, not a dictionary
        param_names = list(paramDict)
        textlist = self.translate_texts_with_openai(param_names, langkey)
        
        for ii, namekey in enumerate(param_names):
            self.babelFishDict['Item Parameter'][namekey][langkey]['Name'] = textlist[ii]
        print(f"Item parameter names translated: {textlist}")
        time.sleep(3)


language().saveProcessedLanguageDict()
