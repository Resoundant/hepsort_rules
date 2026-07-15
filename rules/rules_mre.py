from pydicom import Dataset

PRIVATE_TAGS={
    'GESequence':0x0019109c,
    'GEpolarizations_epi': 0x0019107e,
    'GEpolarizations_gre': 0x001910f2,
}

MRE_REQ_LABELS = [
    'mre_mag',
    'mre_phs',
]

MRE_LABELS_TO_ALC = {
    'mre_mag': 'mre.mag',
    'mre_phs': 'mre.phs',
}



MRE_TIME_RANGE = 5.0

# # this summarizes the labels that rules can apply that will be filtered 
# MRE_LABELS = [
#     'mre_mag',
#     'mre_phs',
#     'mre_ge',
#     '3d_mre_mag',
#     '3d_mre_phs',
#     '3d_mre_stiff',
# ]

# LABELS_MAYO_GE = [
#     'mre_iqepi',
#     'mre_iqgre',
# ]

# data tagged as mre_mag and mre_phs will try to be matched together.
# data tagged as mre_ge will go through a secondary step to split in half, first half if phs, second half is mag
# data tagged as mre_iqgre will go through a secondary step to 4 idk + 4 mag + 8 phs


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

def get_private_float_or_zero(data:Dataset, tag) -> float:
    data_value = data.get(tag, None)
    if data_value == None:
        return 0.0
    return float(data_value)

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
    

RULES_CANON_MRE=[
# {   'name':'canon_seepi_mre_mag',
#     'rules':func_check_dcm_tags([('Magnitude','in',TAGS['ImageComments'])]),
#     'action':lambda data: setattr(data, "label", "mre_mag")
# },
# {   'name':'canon_seepi_mre_stiff',
#     'rules':func_check_dcm_tags([('Stiffness','in',TAGS['ImageComments'])]),
#     'action':lambda data: setattr(data, "label", "mre_stiff")
# },
# {   'name':'canon_seepi_mre_phs',
#     'rules':func_check_dcm_tags([('PhaseDiff','in',TAGS['ImageComments'])]),
#     'action':lambda data: setattr(data, "label", "mre_phs")
# },

]


RULES_PHILIPS_MRE = [
{   
    'name':'philips_seepi_mre_mag',
    'rules': [
        lambda data: 'ORIGINAL' in data.get('ImageType',''),
        lambda data: 'M' in data.get('ImageType',''),
        lambda data: 'M_SE' in data.get('ImageType',''),
        lambda data: data.get('NumberOfTemporalPositions',0) <= 1, # distinguish from 3D
    ],
    'criteria': all,
    'action': lambda data: [
        append_dataset(data, "label", "mre_mag"),
        setattr(data, "data_source", "seepi_mre"),
    ]
},
{   'name':'philips_gre_mre_mag',
    'rules': [
        lambda data: 'ORIGINAL' in data.get('ImageType',''),
        lambda data: 'M' in data.get('ImageType',''),
        lambda data: 'FFE' in data.get('ImageType',''),
        lambda data: data.get('NumberOfTemporalPositions',0) <= 1, # distinguish from 3D
    ],
    'criteria': all,
    'action': lambda data: [
        append_dataset(data, "label", "mre_mag"),
        setattr(data, "data_source", "gre_mre"),
    ]
},
{   'name':'philips_mre_phs', # applies to gre and epi
    'rules': [
        lambda data: 'ORIGINAL' in data.get('ImageType',''),
        lambda data: 'P' in data.get('ImageType',''),
        lambda data: 'MRE' in data.get('ImageType',''),
        lambda data: data.get('NumberOfTemporalPositions',0) <= 1, # distinguish from 3D
    ],
    'criteria': all,
    'action': lambda data: [
        append_dataset(data, "label", "mre_phs"),
        # setattr(data, "data_source", "seepi_mre"), #phs does not differentiate EPI or GRE
    ]
},
]


RULES_SIEMENS_MRE=[
{   'name':'siemens_gre_mre_mag',
    'rules': [
        lambda data: 'PRIMARY' in data.get('ImageType',''),
        lambda data: 'M' in data.get('ImageType',''),
        lambda data: 'greMR' in data.get('SequenceName','')
    ],
    'criteria': all,
    'action': lambda data: [
        append_dataset(data, "label", "mre_mag"),
        setattr(data, "data_source", "gre_mre"),
    ]
},
{   'name':'siemens_gre_mre_phs',
    'rules': [
        lambda data: 'PRIMARY' in data.get('ImageType',''),
        lambda data: 'P' in data.get('ImageType',''),
        lambda data: 'WV' not in data.get('ImageType',''),
        lambda data: 'greMR' in data.get('SequenceName','')
    ],
    'criteria': all,
    'action': lambda data: [
        append_dataset(data, "label", "mre_phs"),
        setattr(data, "data_source", "gre_mre"),
    ]
},
{   'name':'siemens_seepi_mre_mag',
    'rules': [
        lambda data: 'PRIMARY' in data.get('ImageType',''),
        lambda data: 'M' in data.get('ImageType',''),
        lambda data: ('epiMR' in data.get('SequenceName',''))
                or   ('epseM' in data.get('SequenceName','') and 'WIP_e' not in data.get('SequenceName','')) 
    ],
    'criteria': all,
    'action': lambda data: [
        append_dataset(data, "label", "mre_mag"),
        setattr(data, "data_source", "seepi_mre"),
    ]
},
{   'name':'siemens_epi_mre_phs',
    'rules': [
        lambda data: 'PRIMARY' in data.get('ImageType',''),
        lambda data: 'P' in data.get('ImageType',''),
        lambda data: 'WV' not in data.get('ImageType',''),
        lambda data: ('epiMR' in data.get('SequenceName',''))
                or   ('epseM' in data.get('SequenceName','') and 'WIP_e' not in data.get('SequenceName',''))
    ],
    'criteria': all,
    'action': [
        lambda data: append_dataset(data, "label", "mre_phs"),
        lambda data: setattr(data, "data_source", "seepi_mre"),
    ]
},
{   'name':'siemens_seepi_mre_mag_xa61',
    'rules': [
        lambda data: 'ELASTO' in data.get('ImageType',''),
        lambda data: 'MAGNITUDE' in data.get('ComplexImageComponent',''),
    ],
    'criteria': all,
    'action': lambda data: [
        append_dataset(data, "label", "mre_mag"),
        setattr(data, "data_source", "seepi_mre"),
    ]
},
{   'name':'siemens_epi_mre_phs_xa61',
    'rules': [
        lambda data: 'ELASTO' in data.get('ImageType',''),
        lambda data: 'PHASE' in data.get('ComplexImageComponent',''),
    ],
    'criteria': all,
    'action': [
        lambda data: append_dataset(data, "label", "mre_phs"),
        lambda data: setattr(data, "data_source", "seepi_mre"),
    ]
},
{   'name':'siemens_epi2dwip_mre_mag',
    'rules': [
        lambda data: 'PRIMARY' in data.get('ImageType',''),
        lambda data: 'M' in data.get('ImageType',''),
        lambda data: 'WIP_epseMRE' in data.get('SequenceName','')
    ],
    'criteria': all,
    'action': lambda data: [
        append_dataset(data, "label", "mre_mag"),
        setattr(data, "data_source", "seepi_mre"),
    ]
},
{   'name':'siemens_epi2dwip_mre_phs',
    'rules': [
        lambda data: 'PRIMARY' in data.get('ImageType',''),
        lambda data: 'P' in data.get('ImageType',''),
        lambda data: 'WV' not in data.get('ImageType',''),
        lambda data: ('WIP_epseMRE' in data.get('SequenceName','') or ('WIP_e_' in data.get('SequenceName','')))
    ],
    'criteria': all,
    'action':lambda data: [
        append_dataset(data, "label", "mre_phs"),
        setattr(data, "data_source", "seepi_mre"),
    ]
},
]


RULES_GE_MRE=[
### standard 2D MRE ###
{   'name':'ge_mre_mrtouch',
    'rules': [
        lambda data: private_value_equals(data,PRIVATE_TAGS['GESequence'],'MR-Touch'),
        lambda data: data.get('PhotometricInterpretation', '') != 'RGB',
        lambda data: 'DERIVED' not in data.get('ImageType',''), # on-scanner wave and elasto data
    ],
    'criteria': all,
    'action':lambda data: [
        append_dataset(data, "label", "mre_ge"),
        #setattr(data, "data_source", "seepi_mre"), # need to do this later
    ]
},
]

RULES_MAYO_GE = [
{   'name':'mayo_ge_fgre_mre',
    'rules': [
        lambda data: private_value_equals(data,PRIVATE_TAGS['GESequence'],'fgremre'),
        lambda data: data.get('PhotometricInterpretation', '') != 'RGB',
        lambda data: 'SECONDARY' not in data.get('ImageType',''), # on-scanner wave data
    ],
    'criteria': all,
    'action':lambda data: [
        append_dataset(data, "label", "mre_ge"),
        setattr(data, "data_source", "gre_mre"), 
    ]
},
# this is on-scanner M/P from Kevin's IQ inputs (eg series 5=IQ, 501=M/P)
{   'name':'mayo_ge_epi_mre',
    'rules': [
        lambda data: private_value_equals(data,PRIVATE_TAGS['GESequence'],'epimre'),
        lambda data: not data.get('SeriesDescription', '').startswith(('PE', 'FE', 'SS', 'Stiffness', 'RGB', 'Storage', 'Loss', 'Divergence')),
        lambda data: data.get('PhotometricInterpretation', '') != 'RGB',
        lambda data: 'PROCESSED' in data.get('ImageType',''), # on-scanner M/P data
        lambda data: str(data.get('SeriesNumber',0)).endswith("1"), # on-scanner M/P data will end in 1, wave will not
    ],
    'criteria': all,
    'action':lambda data: [
        append_dataset(data, "label", "mre_ge"),
        setattr(data, "data_source", "seepi_mre"),
    ]
},
# 'raw' IQ data from kevin glaser EPI MRE, GE sequence name epimre
# could be 2D or 3D, both are named epimre.
# on-scanner IQ is ORIGINAL/PRIMARY/OTHER
# on-scanner MP is DERIVED/SECONDARY/PROCESSED (which is incorrect, but here we are), along with the wave and other contrasts
{   'name':'mayo_ge_epi_mre_iq',
    'rules': [
        lambda data: private_value_equals(data,PRIVATE_TAGS['GESequence'],'epimre'),
        lambda data: not data.get('SeriesDescription', '').startswith(('PE', 'FE', 'SS', 'Stiffness', 'RGB', 'Storage', 'Loss', 'Divergence')),
        lambda data: data.get('PhotometricInterpretation', '') != 'RGB',
        lambda data: 'ORIGINAL'  in data.get('ImageType',''), # on-scanner IQ data
        lambda data: 'PRIMARY'   in data.get('ImageType',''), # on-scanner IQ data
    ],
    'criteria': all,
    'action':lambda data: [
        append_dataset(data, "label", "mre_iqepi"),
        setattr(data, "data_source", "seepi_mre"), 
        setattr(data, "digest_type", "mmdi3v")
    ]
},

# this is to try to flag on-scanner recon contrasts
{   'name':'mayo_ge_epi_mre_onscanner',
    'rules': [
        lambda data: private_value_equals(data,PRIVATE_TAGS['GESequence'],'epimre'),
        #lambda data: data.get('SeriesDescription', '').startswith(('PE', 'FE', 'SS', 'Stiffness', 'RGB', 'Storage', 'Loss', 'Divergence')),
        lambda data: data.get('PhotometricInterpretation', '') != 'RGB',
    ],
    'criteria': all,
    'action':lambda data: [
        append_dataset(data, "label", "mre_ge_other"),
        setattr(data, "data_source", "seepi_mre"), 
    ]
},
### Roger's IQ MRE (16 images, 4 idk, 4 mag, 8 phase)
{   'name':'mayo_ge_iqgre_mre',
    'rules': [
        lambda data: private_value_equals(data,PRIVATE_TAGS['GESequence'],'iqmre2d'),
        lambda data: data.get('PhotometricInterpretation', '') != 'RGB',
        lambda data: 'SECONDARY' not in data.get('ImageType',''), # on-scanner wave data
    ],
    'criteria': all,
    'action':lambda data: [
        append_dataset(data, "label", "mre_iqgre"),
        setattr(data, "data_source", "Mayo_IQGRE"), # iqgre_mre #GE Mayo IQGRE
    ]
},
### Mayo Iron-overload MRE variants (16 images, 4 idk, 4 mag, 8 phase)
{   'name':'mayo_ge_epi_mre_iron',
    'rules': [
        lambda data: private_value_contains(data,PRIVATE_TAGS['GESequence'],'epimre_iron'),
        # lambda data: 'DERIVED' not in data.get('ImageType',''), # on-scanner wave and elasto data
    ],
    'criteria': all,
    'action':lambda data: [
        append_dataset(data, "label", "mayo_iron"),
        setattr(data, "data_source", "GE Mayo SEEPI Iron"), 
    ]
},
{   'name':'mayo_ge_se_iron_mre',
    'rules': [
        lambda data: private_value_contains(data,PRIVATE_TAGS['GESequence'],'se_iron_mre'),
        # lambda data: 'DERIVED' not in data.get('ImageType',''), # on-scanner wave and elasto data
    ],
    'criteria': all,
    'action':lambda data: [
        append_dataset(data, "label", "mayo_iron"),
        setattr(data, "data_source", "GE Mayo SE Iron"), 
    ]
},
]

# GE rules for 3VMRE (3DMRE) IQ data
RULES_3VMRE_WIP = [
# 3V EPI stored polarizations in 0019,107e (VR = SS, signed short (16 bit))
{
    'name':'ge_3vmre_iq',
    'rules': [
        lambda data: private_value_equals(data,PRIVATE_TAGS['GESequence'],'epimre'),
        lambda data: data.get('NumberOfTemporalPositions',0) > 1,
        # lambda data: get_private_float_or_zero(data,PRIVATE_TAGS['GEpolarizations_epi']) > 1,

    ],
    'criteria': all,
    'action':lambda data: [
        setattr(data, "label", "3v_iq"),
        setattr(data, "data_source", "3vmmdi"),
        setattr(data, "digest_type", "mmdi3v")
    ]
},
# 3V GRE stored polarizations in 0019,10f2  (VR = SS)
# {
#     'name':'ge_3vmre_gre',
#     'rules': [
#         lambda data: compare_private_value(data,PRIVATE_TAGS['GESequence'],'gremre'), # TODO IDK this pulse seq name
#         lambda data: data.get('NumberOfTemporalPositions',0) > 1,
#         lambda data: get_private_float_or_zero(data,PRIVATE_TAGS['GEpolarizations_gre']) > 1,

#     ],
#     'criteria': all,
#     'action':lambda data: [
#         setattr(data, "label", "3v_iq"),
#         setattr(data, "data_source", "3vmmdi"),
#     ]
# },
{
    'name':'philips_3vmre_mag',
    'rules': [
        lambda data: 'ORIGINAL' in data.get('ImageType',''),
        lambda data: 'M' in data.get('ImageType',''),
        lambda data: 'SE' in data.get('ImageType',''),
        lambda data: data.get('NumberOfTemporalPositions',0) > 1,
    ],
    'criteria': all,
    'action': lambda data: [
        append_dataset(data, "label", "mre_mag"),
        setattr(data, "data_source", "3vmmdi"),
        setattr(data, "digest_type", "mmdi3v")
    ]
},
{
    'name':'philips_3vmre_phs', # applies to gre and epi
    'rules': [
        lambda data: 'ORIGINAL' in data.get('ImageType',''),
        lambda data: 'P' in data.get('ImageType',''),
        lambda data: 'MRE' in data.get('ImageType',''),
        lambda data: data.get('NumberOfTemporalPositions',0) > 1,
    ],
    'criteria': all,
    'action': lambda data: [
        append_dataset(data, "label", "mre_phs"),
        setattr(data, "data_source", "3vmmdi"), 
        setattr(data, "digest_type", "mmdi3v")
    ]
},
{
    'name':'siemens_3vmre_wip924_mag', # applies to gre and epi
    'rules': [
        lambda data: 'M' in data.get('ImageType',''),
        lambda data: 'WIP_epseMRE' in data.get('SequenceName','')
    ],
    'criteria': all,
    'action': lambda data: [
        append_dataset(data, "label", "mre_phs"),
        setattr(data, "data_source", "3vmmdi"), 
        setattr(data, "digest_type", "mmdi3v")
    ]
},
{
    'name':'siemens_3vmre_wip924_phs', # applies to gre and epi
    'rules': [
        lambda data: 'P' in data.get('ImageType',''),
        lambda data: 'WIP_epseMRE' in data.get('SequenceName','')
    ],
    'criteria': all,
    'action': lambda data: [
        append_dataset(data, "label", "mre_phs"),
        setattr(data, "data_source", "3vmmdi"), 
        setattr(data, "digest_type", "mmdi3v")
    ]
},
]


MRE_REQ_LABELS_3D = [
    '3dmre_mag_rms',
    '3dmre_phs_z',
    '3dmre_stiff',
    '3dmre_conf',
]

MRE3D_LABELS_TO_ALC = {
    '3dmre_mag_rms': 'mre.mag',
    '3dmre_phs_z': 'mre.phs',
    '3dmre_stiff': 'mre.stiff',
    '3dmre_conf': 'mre.conf',
}

RULES_3DMMDI =[
{   'name':'3vmre_mag',
    'rules': [
        lambda data: 'MAGRMS' in data.get('ImageType',''),
        # lambda data: 'DERIVED' in data.get('ImageType',''),
        lambda data: 'MMDI3D' in data.get('ImageType',''),
    ],
    'criteria': all,
    'action':lambda data: [
        append_dataset(data, "label", "3dmre_mag_rms"),
        setattr(data, "data_source", "MMDI 3D"),
    ]
},
{   'name':'3vmre_phs_z',
    'rules': [
        lambda data: 'PHSDIFFZ' in data.get('ImageType',''),
        # lambda data: 'DERIVED' in data.get('ImageType',''),
        lambda data: 'MMDI3D' in data.get('ImageType',''),
    ],
    'criteria': all,
    'action':lambda data: [
        append_dataset(data, "label", "3dmre_phs_z"),
        setattr(data, "data_source", "MMDI 3D"),
    ]
},
{   'name':'3vmre_stiff',
    'rules': [
        lambda data: 'STIFFNESS' in data.get('ImageType',''),
        # lambda data: 'DERIVED' in data.get('ImageType',''),
        lambda data: 'MMDI3D' in data.get('ImageType',''),
    ],
    'criteria': all,
    'action':lambda data: [
        append_dataset(data, "label", "3dmre_stiff"),
        setattr(data, "data_source", "MMDI 3D"),
    ]
},
{   'name':'3vmre_conf',
    'rules': [
        lambda data: 'CONFIDENCE' in data.get('ImageType',''),
        # lambda data: 'DERIVED' in data.get('ImageType',''),
        lambda data: 'MMDI3D' in data.get('ImageType',''),
    ],
    'criteria': all,
    'action':lambda data: [
        append_dataset(data, "label", "3dmre_conf"),
        setattr(data, "data_source", "MMDI 3D"),
    ]
},
]

MRE_RULES = [] \
    + RULES_CANON_MRE \
    + RULES_PHILIPS_MRE \
    + RULES_SIEMENS_MRE \
    + RULES_GE_MRE \
    + RULES_MAYO_GE \
    + RULES_3VMRE_WIP \
    + RULES_3DMMDI


