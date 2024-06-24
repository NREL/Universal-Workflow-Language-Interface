# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 18:54:22 2023

@author: repps
"""
import itemdictionary as itemdict
import actiondictionary as actiondict

def loadDictionary():
    dictionary = {
        'Action': actiondict.getActionList('Action'),
        'Item': {
            'Container': itemdict.getItemList('Container'),
            'Source': itemdict.getItemList('Source'),
            'Tool': itemdict.getItemList('Tool'),
            'Abstract': itemdict.getItemList('Abstract')
        },
        'Action Parameter': actiondict.getActionList('Action_Params'),
        'Item Parameter': itemdict.getItemList('Container_Tool_Source_Params')
    }

    return dictionary