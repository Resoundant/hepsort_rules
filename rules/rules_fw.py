from pydicom import Dataset

PRIVATE_TAGS={
    'GESequence':0x0019109c,
}


FW_OPT_LABELS = [
    'r2star',
    'fat',
]

FW_REQ_LABELS = [
    'pdff',
    'water',
]

FW_LABELS_TO_ALC = {
    'pdff'   : 'fw.ffrac',
    'water'  : 'fw.water',
    'r2star' : 'fw.r2star',
    'fat'    : 'fw.fat',

}

FW_TIME_RANGE = 5.0

def private_value_equals(data:Dataset, tag, value) -> bool:
    data_value = data.get(tag)
    if data_value == None:
        return False
    return data_value.value == value

def private_value_contains(data:Dataset, tag, value) -> bool:
    data_value = data.get(tag)
    if data_value == None:
        return False
    return value in data_value.value

# def substring_in_list(data, tag, value) -> bool:
#   todo: return false if data[tag] does is not a list
#     lambda data: any('FAT_FRAC' in x for x in data.get('ImageType',[]))

def append_dataset(data:Dataset, key:str, value:str):
    if data.get(key, None) == None:
        setattr(data, key, [value])
        return
    existing_value = data.get(key)
    if type(existing_value) != list:
        existing_value = [existing_value]
    existing_value.append(value)
    setattr(data, key, existing_value)
    return


RULES_GE_IDEAL=[
{   'name': 'ge_idealiq_pdff',
    'rules': [
        lambda data: private_value_contains(data,PRIVATE_TAGS['GESequence'],'IDEAL'),
        lambda data: 'FAT_FRACTION' in data.get('ImageType',''),
    ],
    'criteria': all,
    'action':lambda data: append_dataset(data, "label", "pdff"),
},
{   'name': 'ge_idealiq_fat',
    'rules': [
        lambda data: private_value_contains(data,PRIVATE_TAGS['GESequence'],'IDEAL'),
        lambda data: 'FAT' in data.get('ImageType',''),
    ],
    'criteria': all,
    'action':lambda data: append_dataset(data, "label", "fat"),
},
{   'name':'ge_idealiq_water',
    'rules': [
        lambda data: private_value_contains(data,PRIVATE_TAGS['GESequence'],'IDEAL'),
        lambda data: 'WATER' in data.get('ImageType',''),
    ],
    'criteria': all,
    'action':lambda data: append_dataset(data, "label", "water"),
},  
{   'name':'ge_idealiq_r2star',
    'rules': [
        lambda data: private_value_contains(data,PRIVATE_TAGS['GESequence'],'IDEAL'),
        lambda data: 'R2_STAR_MAP' in data.get('ImageType',''),
    ],
    'criteria': all,
    'action':lambda data: append_dataset(data, "label", "r2star"),
},
]

RULES_SIEMENS_QDIXON=[
{   'name': 'siemens_qdixon_pdff',
    'rules': [
        lambda data: 'FAT_FRAC'     in data.get('ImageType',''),
        lambda data: 'FAT_FRACTION' in data.get('ImageType',''),
    ],
    'criteria': any,
    'action':lambda data: append_dataset(data, "label", "pdff"),
},
{   'name':'siemens_qdixon_fat',
    'rules': [
        lambda data: 'FAT' in data.get('ImageType',''),
    ],
    'criteria': all,
    'action':lambda data: append_dataset(data, "label", "fat"),
},
{   'name':'siemens_qdixon_water',
    'rules': [
        #lambda data: 'fl3d6' in data.get('SequenceName',''),
        lambda data: 'WATER' in data.get('ImageType',''),
    ],
    'criteria': all,
    'action':lambda data: append_dataset(data, "label", "water"),
},
{   'name':'siemens_qdixon_r2star',
    'rules': [
        #lambda data: 'fl3d6' in data.get('SequenceName',''),
        lambda data: 'R2_STAR_MAP' in data.get('ImageType',''),
    ],
    'criteria': all,
    'action':lambda data: append_dataset(data, "label", "r2star"),
},
]

RULES_PHILIPS_MDIXONDQUANT=[
{   'name':'philips_mdixon_quant_pdff',
    'rules': [
        lambda data: 'FF' in data.get('ImageType',''),
    ],
    'criteria': all,
    'action':lambda data: append_dataset(data, "label", "pdff"),
},
{   'name':'philips_mdixon_quant_fat',
    'rules': [
        lambda data: 'F' in data.get('ImageType',''),
    ],
    'criteria': all,
    'action':lambda data: append_dataset(data, "label", "fat"),
},
{   'name':'philips_mdixon_quant_water',
    'rules': [
        lambda data: 'W' in data.get('ImageType',''),
    ],
    'criteria': all,
    'action':lambda data: append_dataset(data, "label", "water"),
},
{   'name':'philips_mdixon_quant_r2star',
    'rules': [
        lambda data: 'R2_STAR' in data.get('ImageType',''),
    ],
    'criteria': all,
    'action':lambda data: append_dataset(data, "label", "r2star"),
},
]

FW_RULES = [] \
    + RULES_SIEMENS_QDIXON \
    + RULES_GE_IDEAL \
    + RULES_PHILIPS_MDIXONDQUANT
    
