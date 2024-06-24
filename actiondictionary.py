# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 08:01:09 2024

@author: repps
"""

def loadActionDictionary():
    dictionary = {
        'Action': {
            # Actions - Add
            'Add': {
                'Add': {
                    '00': lambda a, b, c: f'Add {b} to {a}',
                    '01': lambda a, b, c: f'Add {b} to {a} using {c}'
                },
                'Drop cast': {
                    '00': lambda a, b, c: f'Drop cast {b} onto {a}',
                    '01': lambda a, b, c: f'Drop cast {b} onto {a} using {c}'
                },
                'Hold': {
                    '00': lambda a, b, c: f'Hold {b} with {a}',
                    '01': lambda a, b, c: f'Hold {b} with {a} using {c}'
                },
                'Fill': {
                    '00': lambda a, b, c: f'Fill {a} with {b}',
                    '01': lambda a, b, c: f'Fill {a} with {b} using {c}'
                },
                'Combine': {
                    '00': lambda a, b, c: f'Combine {a} with {b}',
                    '01': lambda a, b, c: f'Combine {a} with {b} using {c}'
                },
                'Transfer': {
                    '00': lambda a, b, c: f'Transfer {b} to {a}',
                    '01': lambda a, b, c: f'Transfer {b} to {a} using {c}'
                },
                'Load': {
                    '00': lambda a, b, c: f'Load {b} into {a}',
                    '01': lambda a, b, c: f'Load {b} into {a} using {c}'
                },
                'Cover': {
                    '00': lambda a, b, c: f'Cover {a} with {b}',
                    '01': lambda a, b, c: f'Cover {a} with {b} using {c}'
                },
                'Place': {
                    '00': lambda a, b, c: f'Place {b} onto {a}',
                    '01': lambda a, b, c: f'Place {b} onto {a} using {c}'
                },
                'Deposit': {
                    '00': lambda a, b, c: f'Deposit {b} onto {a}',
                    '01': lambda a, b, c: f'Deposit {b} onto {a} using {c}'
                },
                'Insert': {
                    '00': lambda a, b, c: f'Insert {b} into {a}',
                    '01': lambda a, b, c: f'Insert {b} into {a} using {c}'
                },
                'Pour': {
                    '00': lambda a, b, c: f'Pour {b} into {a}',
                    '01': lambda a, b, c: f'Pour {b} into {a} using {c}'
                },
                'Connect': {
                    '00': lambda a, b, c: f'Connect {b} to {a}',
                    '01': lambda a, b, c: f'Connect {b} to {a} using {c}'
                },
                'Secure': {
                    '00': lambda a, b, c: f'Secure {b} to {a}',
                    '01': lambda a, b, c: f'Secure {b} to {a} using {c}'
                }
            },

            # Actions - Remove
            'Remove': {
                'Remove': {
                    '00': lambda a, b, c: f'Remove {b} from {a}',
                    '01': lambda a, b, c: f'Remove {b} from {a} using {c}'
                },
                'Separate': {
                    '00': lambda a, b, c: f'Separate {b} from {a}',
                    '01': lambda a, b, c: f'Separate {b} from {a} using {c}'
                },
                'Aliquot': {
                    '00': lambda a, b, c: f'Aliquot {b} from {a}',
                    '01': lambda a, b, c: f'Aliquot {b} from {a} using {c}'
                },
                'Unload': {
                    '00': lambda a, b, c: f'Unload {b} from {a}',
                    '01': lambda a, b, c: f'Unload {b} from {a} using {c}'
                },
                'Withdraw': {
                    '00': lambda a, b, c: f'Withdraw {b} from {a}',
                    '01': lambda a, b, c: f'Withdraw {b} from {a} using {c}'
                },
                'Collect': {
                    '00': lambda a, b, c: f'Collect {b} from {a}',
                    '01': lambda a, b, c: f'Collect {b} from {a} using {c}'
                }
            },

            # Actions - Modify
            'Modify': {
                'Modify': {
                    '00': lambda a, b, c: f'Modify {a}',
                    '01': lambda a, b, c: f'Modify {a} with {b}',
                    '02': lambda a, b, c: f'Modify {a} with {b} using {c}',
                    '03': lambda a, b, c: f'Modify {a} using {c}'
                },
                'Measure': {
                    '00': lambda a, b, c: f'Measure {a}',
                    '01': lambda a, b, c: f'Measure {a} in {b}',
                    '02': lambda a, b, c: f'Measure {a} in {b} using {c}',
                    '03': lambda a, b, c: f'Measure {a} using {c}'
                },
                'Vortex': {
                    '00': lambda a, b, c: f'Vortex {a}',
                    '01': lambda a, b, c: f'Vortex {a} in {b}',
                    '02': lambda a, b, c: f'Vortex {a} in {b} using {c}',
                    '03': lambda a, b, c: f'Vortex {a} using {c}'
                },
                'Seal': {
                    '00': lambda a, b, c: f'Seal {a}',
                    '01': lambda a, b, c: f'Seal {a} with {b}',
                    '02': lambda a, b, c: f'Seal {a} with {b} using {c}',
                    '03': lambda a, b, c: f'Seal {a} using {c}'
                },
                'Sonicate': {
                    '00': lambda a, b, c: f'Sonicate {a}',
                    '01': lambda a, b, c: f'Sonicate {a} in {b}',
                    '02': lambda a, b, c: f'Sonicate {a} in {b} using {c}',
                    '03': lambda a, b, c: f'Sonicate {a} using {c}'
                },
                'Treat': {
                    '00': lambda a, b, c: f'Treat {a}',
                    '01': lambda a, b, c: f'Treat {a} with {b}',
                    '02': lambda a, b, c: f'Treat {a} with {b} using {c}',
                    '03': lambda a, b, c: f'Treat {a} using {c}'
                },
                'Clean': {
                    '00': lambda a, b, c: f'Clean {a}',
                    '01': lambda a, b, c: f'Clean {a} with {b}',
                    '02': lambda a, b, c: f'Clean {a} with {b} using {c}',
                    '03': lambda a, b, c: f'Clean {a} using {c}'
                },
                'Blow': {
                    '00': lambda a, b, c: f'Blow {a}',
                    '01': lambda a, b, c: f'Blow {a} with {b}',
                    '02': lambda a, b, c: f'Blow {a} with {b} using {c}',
                    '03': lambda a, b, c: f'Blow {a} using {c}'
                },
                'Rinse': {
                    '00': lambda a, b, c: f'Rinse {a}',
                    '01': lambda a, b, c: f'Rinse {a} with {b}',
                    '02': lambda a, b, c: f'Rinse {a} with {b} using {c}',
                    '03': lambda a, b, c: f'Rinse {a} using {c}'
                },
                'Cool': {
                    '00': lambda a, b, c: f'Cool {a}',
                    '01': lambda a, b, c: f'Cool {a} with {b}',
                    '02': lambda a, b, c: f'Cool {a} with {b} using {c}',
                    '03': lambda a, b, c: f'Cool {a} using {c}'
                },
                'Heat': {
                    '00': lambda a, b, c: f'Heat {a}',
                    '01': lambda a, b, c: f'Heat {a} with {b}',
                    '02': lambda a, b, c: f'Heat {a} with {b} using {c}',
                    '03': lambda a, b, c: f'Heat {a} using {c}'
                },
                'Preheat': {
                    '00': lambda a, b, c: f'Preheat {a}',
                    '01': lambda a, b, c: f'Preheat {a} with {b}',
                    '02': lambda a, b, c: f'Preheat {a} with {b} using {c}',
                    '03': lambda a, b, c: f'Preheat {a} using {c}'
                },
                'Run': {
                    '00': lambda a, b, c: f'Run {a}',
                    '01': lambda a, b, c: f'Run {a} on {b}',
                    '02': lambda a, b, c: f'Run {a} on {b} using {c}',
                    '03': lambda a, b, c: f'Run {a} using {c}'
                },
                'Stir': {
                    '00': lambda a, b, c: f'Stir {a}',
                    '01': lambda a, b, c: f'Stir {a} with {b}',
                    '02': lambda a, b, c: f'Stir {a} with {b} using {c}',
                    '03': lambda a, b, c: f'Stir {a} using {c}'
                },
                'Purge': {
                    '00': lambda a, b, c: f'Purge {a}',
                    '01': lambda a, b, c: f'Purge {a} with {b}',
                    '02': lambda a, b, c: f'Purge {a} with {b} using {c}',
                    '03': lambda a, b, c: f'Purge {a} using {c}'
                },
                'Set': {
                    '00': lambda a, b, c: f'Set {a}',
                    '01': lambda a, b, c: f'Set {a} with {b}',
                    '02': lambda a, b, c: f'Set {a} with {b} using {c}',
                    '03': lambda a, b, c: f'Set {a} using {c}'
                },
                'Start': {
                    '00': lambda a, b, c: f'Start {a}',
                    '01': lambda a, b, c: f'Start {a} with {b}',
                    '02': lambda a, b, c: f'Start {a} with {b} using {c}',
                    '03': lambda a, b, c: f'Start {a} using {c}'
                },
                'Stop': {
                    '00': lambda a, b, c: f'Stop {a}',
                    '01': lambda a, b, c: f'Stop {a} with {b}',
                    '02': lambda a, b, c: f'Stop {a} with {b} using {c}',
                    '03': lambda a, b, c: f'Stop {a} using {c}'
                },
                'Anneal': {
                    '00': lambda a, b, c: f'Anneal {a}',
                    '01': lambda a, b, c: f'Anneal {a} with {b}',
                    '02': lambda a, b, c: f'Anneal {a} with {b} using {c}',
                    '03': lambda a, b, c: f'Anneal {a} using {c}'
                },
                'Position': {
                    '00': lambda a, b, c: f'Position {a}',
                    '01': lambda a, b, c: f'Position {a} onto {b}',
                    '02': lambda a, b, c: f'Position {a} onto {b} using {c}',
                    '03': lambda a, b, c: f'Position {a} using {c}'
                },
                'Drag': {
                    '00': lambda a, b, c: f'Drag {a}',
                    '01': lambda a, b, c: f'Drag {a} across {b}',
                    '02': lambda a, b, c: f'Drag {a} across {b} using {c}',
                    '03': lambda a, b, c: f'Drag {a} using {c}'
                },
                'Scribe': {
                    '00': lambda a, b, c: f'Scribe {a}',
                    '01': lambda a, b, c: f'Scribe {a} onto {b}',
                    '02': lambda a, b, c: f'Scribe {a} onto {b} using {c}',
                    '03': lambda a, b, c: f'Scribe {a} using {c}'
                },
                'Swirl': {
                    '00': lambda a, b, c: f'Swirl {a}',
                    '01': lambda a, b, c: f'Swirl {a} with {b}',
                    '02': lambda a, b, c: f'Swirl {a} with {b} using {c}',
                    '03': lambda a, b, c: f'Swirl {a} using {c}'
                },
                'Wait': {
                    '00': lambda a, b, c: f'Wait {a}',
                    '01': lambda a, b, c: f'Wait {a} with {b}',
                    '02': lambda a, b, c: f'Wait {a} with {b} using {c}',
                    '03': lambda a, b, c: f'Wait {a} using {c}',
                    'S': lambda a, b, c: f'Wait'
                },
                'Cut': {
                    '00': lambda a, b, c: f'Cut {a}',
                    '01': lambda a, b, c: f'Cut {a} with {b}',
                    '02': lambda a, b, c: f'Cut {a} with {b} using {c}',
                    '03': lambda a, b, c: f'Cut {a} using {c}'
                },
                'Filter': {
                    '00': lambda a, b, c: f'Filter {a}',
                    '01': lambda a, b, c: f'Filter {a} with {b}',
                    '02': lambda a, b, c: f'Filter {a} with {b} using {c}',
                    '03': lambda a, b, c: f'Filter {a} using {c}'
                },
                'Pressurize': {
                    '00': lambda a, b, c: f'Pressurize {a}',
                    '01': lambda a, b, c: f'Pressurize {a} with {b}',
                    '02': lambda a, b, c: f'Pressurize {a} with {b} using {c}',
                    '03': lambda a, b, c: f'Pressurize {a} using {c}'
                },
                'Concentrate': {
                    '00': lambda a, b, c: f'Concentrate {a}',
                    '01': lambda a, b, c: f'Concentrate {a} with {b}',
                    '02': lambda a, b, c: f'Concentrate {a} with {b} using {c}',
                    '03': lambda a, b, c: f'Concentrate {a} using {c}'
                },
                'Centrifuge': {
                    '00': lambda a, b, c: f'Centrifuge {a}',
                    '01': lambda a, b, c: f'Centrifuge {a} with {b}',
                    '02': lambda a, b, c: f'Centrifuge {a} with {b} using {c}',
                    '03': lambda a, b, c: f'Centrifuge {a} using {c}'
                }
            }
        },
        'Action_Params': {
            "Heat": [
                "Temperature",
                "Setpoint temperature",
                "Target temperature"
                "Heating rate",
                "Cooling rate",
                "Heat flux"
                ],
            "Pressure": [
                "Pressure",
                "Initial pressure",
                "Final pressure",
                "Pressure ramp rate",
                "Pressure stability",
                "Pressure control",
                "Pressure release rate",
                "Compression ratio",
                "Maximum pressure",
                "Minimum pressure",
                "Pressure gradient",
                "Gas pressure",
                "Hydraulic pressure",
                "Vapor pressure",
                "Partial pressure",
                "Back pressure",
                "Internal pressure",
                "External pressure",
                "Pressure drop",
                "Pressure buildup"
                ],
            "Quantity": [
                "Mass",
                "Volume",
                "Flow rate",
                "Addition rate",
                "Drip rate"
                ],
            "Purification": [
                "Selectivity",
                "Resolution",
                "Retention time",
                "Separation efficiency",
                "Column efficiency",
                "Elution volume",
                "Eluent composition",
                "Mobile phase flow rate",
                "Stationary phase composition",
                "Partition coefficient",
                "Plate number",
                "Plate height",
                "Extraction efficiency",
                "Isolation purity",
                "Cut size",
                "Split ratio",
                "Extraction yield",
                "Distribution coefficient",
                "Phase ratio"
                ],
            "Distillation": [
                "Boiling point",
                "Condensation temperature",
                "Reflux ratio",
                "Number of theoretical plates",
                "Distillate purity",
                "Bottoms purity",
                "Heating temperature",
                "Cooling temperature",
                "Pressure",
                "Feed composition",
                "Holdup time",
                "Vapor velocity",
                "Liquid residence time",
                "Column diameter",
                "Column height",
                "Reboiler duty",
                "Condenser duty",
                "Composition profile",
                "Heat transfer coefficient"
                ],
            "MembraneSeparation": [
                "Permeability",
                "Selectivity",
                "Flux",
                "Rejection rate",
                "Operating pressure",
                "Feed concentration",
                "Feed flow rate",
                "Retentate concentration",
                "Permeate concentration",
                "Cross-flow velocity",
                "Membrane fouling rate",
                "Membrane cleaning frequency",
                "Membrane lifetime"
                ]
            }
        }
    return dictionary

def getActionList(listType):
    dictionary = loadActionDictionary()
    listdict = dictionary[listType].copy()
    
    if listType == 'Action':
        return listdict
    else:
        nameList = []
        for key in listdict.keys():
            for name in listdict[key]:
                if name not in nameList:
                    nameList.append(name)
        nameList.sort()
        return nameList
