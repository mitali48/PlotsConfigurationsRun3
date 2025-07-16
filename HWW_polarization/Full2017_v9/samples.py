import os
import inspect
from mkShapesRDF.lib.search_files import SearchFiles

searchFiles = SearchFiles()
redirector = ""

################################################                                                                                                                                                                                                                             
################# SKIMS ########################                                                                                                                                                                                                                             
################################################                                                                                                                                                                                                                             

mcProduction = 'Summer20UL17_106x_nAODv9_Full2017v9'
dataReco = 'Run2017_UL2017_nAODv9_Full2017v9'
fakeReco = dataReco
mcSteps = 'MCl1loose2017v9__MCCorr2017v9NoJERInHorn__l2tightOR2017v9'
fakeSteps = 'DATAl1loose2017v9__l2loose__fakeW'
dataSteps = 'DATAl1loose2017v9__l2loose__l2tightOR2017v9'
embedReco    = 'Embedding2017_UL2017_nAODv9_Full2017v9'
embedSteps   = 'DATAl1loose2017v9__l2loose__l2tightOR2017v9__Embedding'

samples = {}


##############################################
###### Tree base directory for the site ######
##############################################

treeBaseDir = '/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano'
limitFiles = -1

def makeMCDirectory(var=''):
    return os.path.join(treeBaseDir, mcProduction, mcSteps.format(var=''))


mcDirectory = makeMCDirectory()
fakeDirectory = os.path.join(treeBaseDir, dataReco, fakeSteps)
dataDirectory = os.path.join(treeBaseDir, dataReco, dataSteps)
embedDirectory = os.path.join(treeBaseDir, embedReco, embedSteps)

def nanoGetSampleFiles(path, name):
    _files = searchFiles.searchFiles(path, name, redirector=redirector)
    if limitFiles != -1 and len(_files) > limitFiles:
        return [(name, _files[:limitFiles])]
    else:
        return [(name, _files)]


def CombineBaseW(samples, proc, samplelist):
    _filtFiles = list(filter(lambda k: k[0] in samplelist, samples[proc]["name"]))
    _files = list(map(lambda k: k[1], _filtFiles))
    _l = list(map(lambda k: len(k), _files))
    leastFiles = _files[_l.index(min(_l))]
    dfSmall = ROOT.RDataFrame("Runs", leastFiles)
    s = dfSmall.Sum("genEventSumw").GetValue()
    f = ROOT.TFile(leastFiles[0])
    t = f.Get("Events")
    t.GetEntry(1)
    xs = t.baseW * s

    __files = []
    for f in _files:
        __files += f
    df = ROOT.RDataFrame("Runs", __files)
    s = df.Sum("genEventSumw").GetValue()
    newbaseW = str(xs / s)
    weight = newbaseW + "/baseW"

    for iSample in samplelist:
        addSampleWeight(samples, proc, iSample, weight)


def addSampleWeight(samples, sampleName, sampleNameType, weight):
    obj = list(filter(lambda k: k[0] == sampleNameType, samples[sampleName]["name"]))[0]
    samples[sampleName]["name"] = list(
        filter(lambda k: k[0] != sampleNameType, samples[sampleName]["name"])
    )
    if len(obj) > 2:
        samples[sampleName]["name"].append(
            (obj[0], obj[1], obj[2] + "*(" + weight + ")")
        )
    else:
        samples[sampleName]["name"].append((obj[0], obj[1], "(" + weight + ")"))




################################################
############ DATA DECLARATION ##################
################################################

DataRun = [
    ['B','Run2017B-UL2017-v1'],
    ['C','Run2017C-UL2017-v1'],
    ['D','Run2017D-UL2017-v1'],
    ['E','Run2017E-UL2017-v1'],
    ['F','Run2017F-UL2017-v1'],
]

DataSets = ['MuonEG','SingleMuon','SingleElectron','DoubleMuon', 'DoubleEG']

DataTrig = {
    'MuonEG'         : ' Trigger_ElMu' ,
    'SingleMuon'     : '!Trigger_ElMu && Trigger_sngMu' ,
    'SingleElectron' : '!Trigger_ElMu && !Trigger_sngMu && Trigger_sngEl',
    'DoubleMuon'     : '!Trigger_ElMu && !Trigger_sngMu && !Trigger_sngEl && Trigger_dblMu',
    'DoubleEG'       : '!Trigger_ElMu && !Trigger_sngMu && !Trigger_sngEl && !Trigger_dblMu && Trigger_dblEl'
}


#########################################
############ MC COMMON ##################
#########################################

# SFweight does not include btag weights
mcCommonWeight = 'XSWeight*SFweight*METFilter_MC'
mcCommonWeightMatched = 'XSWeight*SFweight*PromptGenLepMatch2l*METFilter_MC'

###########################################
#############  BACKGROUNDS  ###############
###########################################


###### DY #######                                                                                                                                                                                                                                                            
useEmbeddedDY = True
useDYtt = True
runDYveto = True

embed_tautauveto = '' #Setup
if useEmbeddedDY:
    embed_tautauveto = '*embed_tautauveto'


files=[]
if useEmbeddedDY:
    samples['Dyemb'] = {
        'name': [],
        'weight': 'METFilter_DATA*LepWPCut*embedtotal',
        'weights': [],
        'isData': ['all'],
        'FilesPerJob': 2
    }

    for run_, sd in DataRun:
        files = nanoGetSampleFiles(embedDirectory, 'DYToTT_MuEle_Embedded_Run2017' + run_)
        samples['Dyemb']['name'].extend(files)
        addSampleWeight(samples, 'Dyemb', 'DYToTT_MuEle_Embedded_Run2017' + run_, '(Trigger_ElMu  || Trigger_dblMu || Trigger_sngMu || Trigger_sngEl || Trigger_dblEl)')

    if runDYveto:
        # Vetoed MC: Needed for uncertainty
        files = nanoGetSampleFiles(mcDirectory, 'TTTo2L2Nu') + \
            nanoGetSampleFiles(mcDirectory, 'ST_s-channel') + \
            nanoGetSampleFiles(mcDirectory, 'ST_t-channel_top') + \
            nanoGetSampleFiles(mcDirectory, 'ST_t-channel_antitop') + \
            nanoGetSampleFiles(mcDirectory, 'ST_tW_antitop') + \
            nanoGetSampleFiles(mcDirectory, 'ST_tW_top') + \
            nanoGetSampleFiles(mcDirectory, 'WWJTo2L2Nu_minnlo') + \
            nanoGetSampleFiles(mcDirectory, 'WpWmJJ_EWK_noTop') + \
            nanoGetSampleFiles(mcDirectory, 'GluGluToWWToENEN') + \
            nanoGetSampleFiles(mcDirectory, 'GluGluToWWToENMN') + \
            nanoGetSampleFiles(mcDirectory, 'GluGluToWWToENTN') + \
            nanoGetSampleFiles(mcDirectory, 'GluGluToWWToMNEN') + \
            nanoGetSampleFiles(mcDirectory, 'GluGluToWWToMNMN') + \
            nanoGetSampleFiles(mcDirectory, 'GluGluToWWToMNTN') + \
            nanoGetSampleFiles(mcDirectory, 'GluGluToWWToTNEN') + \
            nanoGetSampleFiles(mcDirectory, 'GluGluToWWToTNMN') + \
            nanoGetSampleFiles(mcDirectory, 'GluGluToWWToTNTN') + \
            nanoGetSampleFiles(mcDirectory, 'ZZTo4L') + \
            nanoGetSampleFiles(mcDirectory, 'WZTo3LNu_mllmin0p1') + \
            nanoGetSampleFiles(mcDirectory, 'ZGToLLG')

        samples['Dyveto'] = {
            'name': files,
            'weight': '(1-embed_tautauveto)',
            'FilesPerJob': 1, # There's some error about not finding sample-specific variables like "nllW" when mixing different samples into a single job; so split them all up instead
            'EventsPerJob': 50000
        }

        addSampleWeight(samples, 'Dyveto', 'TTTo2L2Nu', mcCommonWeightMatched + '* (topGenPt * antitopGenPt > 0.) * (TMath::Sqrt((0.103*TMath::Exp(-0.0118*topGenPt) - 0.000134*topGenPt + 0.973) * (0.103*TMath::Exp(-0.0118*antitopGenPt) - 0.000134*antitopGenPt + 0.973))) + (topGenPt * antitopGenPt <= 0.)')
        addSampleWeight(samples, 'Dyveto', 'ST_s-channel', mcCommonWeightMatched)
        addSampleWeight(samples, 'Dyveto', 'ST_t-channel_top', mcCommonWeightMatched)
        addSampleWeight(samples, 'Dyveto', 'ST_t-channel_antitop', mcCommonWeightMatched)
        addSampleWeight(samples, 'Dyveto', 'ST_tW_antitop', mcCommonWeightMatched)
        addSampleWeight(samples, 'Dyveto', 'ST_tW_top', mcCommonWeightMatched)
        addSampleWeight(samples, 'Dyveto', 'WWJTo2L2Nu_minnlo', mcCommonWeight)
        addSampleWeight(samples, 'Dyveto', 'WpWmJJ_EWK_noTop', mcCommonWeight + '*(Sum(abs(GenPart_pdgId)==6 || GenPart_pdgId==25)==0)')
        addSampleWeight(samples, 'Dyveto', 'GluGluToWWToENEN', mcCommonWeight + '*1.53/1.4')
        addSampleWeight(samples, 'Dyveto', 'GluGluToWWToENMN', mcCommonWeight + '*1.53/1.4')
        addSampleWeight(samples, 'Dyveto', 'GluGluToWWToENTN', mcCommonWeight + '*1.53/1.4')
        addSampleWeight(samples, 'Dyveto', 'GluGluToWWToMNEN', mcCommonWeight + '*1.53/1.4')
        addSampleWeight(samples, 'Dyveto', 'GluGluToWWToMNMN', mcCommonWeight + '*1.53/1.4')
        addSampleWeight(samples, 'Dyveto', 'GluGluToWWToMNTN', mcCommonWeight + '*1.53/1.4')
        addSampleWeight(samples, 'Dyveto', 'GluGluToWWToTNEN', mcCommonWeight + '*1.53/1.4')
        addSampleWeight(samples, 'Dyveto', 'GluGluToWWToTNMN', mcCommonWeight + '*1.53/1.4')
        addSampleWeight(samples, 'Dyveto', 'GluGluToWWToTNTN', mcCommonWeight + '*1.53/1.4')
        addSampleWeight(samples, 'Dyveto', 'ZZTo4L', mcCommonWeightMatched)
        addSampleWeight(samples, 'Dyveto', 'ZGToLLG', ' ( ' + mcCommonWeight + '*(!(Gen_ZGstar_mass > 0))' + ' ) + ( ' + mcCommonWeightMatched + ' * ((Gen_ZGstar_mass >0 && Gen_ZGstar_mass < 4) * 0.94 + (Gen_ZGstar_mass <0 || Gen_ZGstar_mass > 4) * 1.14) * (Gen_ZGstar_mass > 0)' + ' ) ') # Vg contribution + VgS contribution

        addSampleWeight(samples, 'Dyveto', 'WZTo3LNu_mllmin0p1', mcCommonWeightMatched + '*((Gen_ZGstar_mass >0 && Gen_ZGstar_mass < 4) * 0.94 + (Gen_ZGstar_mass <0 || Gen_ZGstar_mass > 4) * 1.14) * (Gen_ZGstar_mass > 0.1)')

        
if useDYtt:
    files = nanoGetSampleFiles(mcDirectory, 'DYJetsToTT_MuEle_M-50') + \
            nanoGetSampleFiles(mcDirectory, 'DYJetsToLL_M-10to50-LO')
else:
    files = nanoGetSampleFiles(mcDirectory, 'DYJetsToLL_M-50_ext2') + \
            nanoGetSampleFiles(mcDirectory, 'DYJetsToLL_M-10to50-LO')


samples['DY'] = {
    'name': files,
    'weight': mcCommonWeight + embed_tautauveto + '*( !(Sum(PhotonGen_isPrompt==1 && PhotonGen_pt>15 && abs(PhotonGen_eta)<2.6) > 0))',
    'FilesPerJob': 1,
    'EventsPerJob': 35000
}

addSampleWeight(samples,'DY','DYJetsToTT_MuEle_M-50','DY_NLO_pTllrw')
addSampleWeight(samples,'DY','DYJetsToLL_M-10to50-LO','DY_LO_pTllrw')


##### Top #######
files = nanoGetSampleFiles(mcDirectory, 'TTTo2L2Nu') + \
        nanoGetSampleFiles(mcDirectory, 'ST_s-channel') + \
        nanoGetSampleFiles(mcDirectory, 'ST_t-channel_top') + \
        nanoGetSampleFiles(mcDirectory, 'ST_t-channel_antitop') + \
        nanoGetSampleFiles(mcDirectory, 'ST_tW_antitop') + \
        nanoGetSampleFiles(mcDirectory, 'ST_tW_top')

samples['top'] = {
    'name': files,
    'weight': mcCommonWeightMatched,
    'FilesPerJob': 1,
    'EventsPerJob': 35000
}

addSampleWeight(samples,'top','TTTo2L2Nu','Top_pTrw')


samples['WW_minnlo'] = {
    'name': nanoGetSampleFiles(mcDirectory, 'WWJTo2L2Nu_minnlo'),
    'weight': mcCommonWeight,
    'FilesPerJob': 1,
    'EventsPerJob': 50000
}

###### WWewk ########

samples['WWewk'] = {
    'name': nanoGetSampleFiles(mcDirectory, 'WpWmJJ_EWK_noTop'),
    'weight': mcCommonWeight+ '*(Sum(abs(GenPart_pdgId)==6 || GenPart_pdgId==25)==0)', #filter tops and Higgs
    'FilesPerJob': 1,
    'EventsPerJob': 50000
}

###### ggWW ########

samples['ggWW'] = {
    'name': nanoGetSampleFiles(mcDirectory, 'GluGluToWWToENEN') + \
            nanoGetSampleFiles(mcDirectory, 'GluGluToWWToENMN') + \
            nanoGetSampleFiles(mcDirectory, 'GluGluToWWToENTN') + \
            nanoGetSampleFiles(mcDirectory, 'GluGluToWWToMNEN') + \
            nanoGetSampleFiles(mcDirectory, 'GluGluToWWToMNMN') + \
            nanoGetSampleFiles(mcDirectory, 'GluGluToWWToMNTN') + \
            nanoGetSampleFiles(mcDirectory, 'GluGluToWWToTNEN') + \
            nanoGetSampleFiles(mcDirectory, 'GluGluToWWToTNMN') + \
            nanoGetSampleFiles(mcDirectory, 'GluGluToWWToTNTN'),
    #'weight': mcCommonWeight+'*1.53/1.4',
    'weight': mcCommonWeight + embed_tautauveto +'* KFactor_ggWW / 1.4',
    'FilesPerJob': 1,
    'EventsPerJob': 10000
}


######## Vg ########
files = nanoGetSampleFiles(mcDirectory, 'Wg_AMCNLOFXFX_01J') + \
    nanoGetSampleFiles(mcDirectory, 'ZGToLLG')

samples['Vg'] = {
    'name': files,
    'weight': mcCommonWeight + '*(Gen_ZGstar_mass <= 0)',
    'suppressNegative' :['all'],
    'suppressNegativeNuisances' :['all'],
    'FilesPerJob': 1,
    'EventsPerJob': 35000
}

######## VgS ######## 
files = nanoGetSampleFiles(mcDirectory, 'ZGToLLG') + \
    nanoGetSampleFiles(mcDirectory, 'Wg_AMCNLOFXFX_01J') + \
    nanoGetSampleFiles(mcDirectory, 'WZTo3LNu_mllmin0p1')

samples['VgS'] = {
    'name': files,
    'weight': mcCommonWeightMatched,
    'suppressNegative' :['all'],
    'suppressNegativeNuisances' :['all'],
    'FilesPerJob': 1,
    'EventsPerJob': 35000
}
addSampleWeight(samples, 'VgS', 'ZGToLLG', '(Gen_ZGstar_mass > 0)')
addSampleWeight(samples, 'VgS', 'Wg_AMCNLOFXFX_01J',  '(Gen_ZGstar_mass > 0 && Gen_ZGstar_mass <= 0.1) * (gstarLow * 0.94)')
addSampleWeight(samples, 'VgS', 'WZTo3LNu_mllmin0p1', '(Gen_ZGstar_mass > 0.1)*(0.601644*58.59/4.666) * (gstarLow * 0.94)')


############ ZZ ############
samples['ZZ'] = {
    'name': nanoGetSampleFiles(mcDirectory, 'ZZTo4L'),
    'weight': mcCommonWeightMatched,
    'FilesPerJob': 1,
    'EventsPerJob': 35000
}


############ WZ ############
samples['WZ'] = {
    'name': nanoGetSampleFiles(mcDirectory, 'WZTo3LNu_mllmin0p1'),
    'weight': mcCommonWeightMatched + ' * (gstarHigh)',
    'FilesPerJob': 2
}
addSampleWeight(samples, 'WZ', 'WZTo3LNu_mllmin0p1', '(0.601644*58.59/4.666)')


########## VVV #########
files = nanoGetSampleFiles(mcDirectory, 'ZZZ') + \
        nanoGetSampleFiles(mcDirectory, 'WZZ') + \
        nanoGetSampleFiles(mcDirectory, 'WWZ') + \
        nanoGetSampleFiles(mcDirectory, 'WWW')

samples['VVV'] = {
    'name': files,
    'weight': mcCommonWeight,
    'FilesPerJob': 2
}

###########################################
#############   SIGNALS  ##################
###########################################

signals = []


############ ggH H->WW ############
samples['ggH_hww'] = {
    'name': nanoGetSampleFiles(mcDirectory, 'GluGluHToWWTo2L2Nu_M125') + nanoGetSampleFiles(mcDirectory, 'GGHjjToWWTo2L2Nu_minloHJJ_M125'),                                                                                                                        
    'weight': mcCommonWeight,
    'FilesPerJob': 1,
    'EventsPerJob': 25000
}
addSampleWeight(samples, 'ggH_hww', 'GluGluHToWWTo2L2Nu_M125', '(HTXS_stage1_1_cat_pTjet30GeV<107)*Weight2MINLO*1092.7640/1073.2567') #only non GE2J categories with the weight to NNLOPS and renormalize integral 
addSampleWeight(samples, 'ggH_hww', 'GGHjjToWWTo2L2Nu_minloHJJ_M125', '(HTXS_stage1_1_cat_pTjet30GeV>106)*1092.7640/1073.2567')                                                                                                                                             

signals.append('ggH_hww')


############ VBF H->WW ############
samples['qqH_hww'] = {
    'name': nanoGetSampleFiles(mcDirectory, 'VBFHToWWTo2L2Nu_M125'),
    'weight': mcCommonWeight,
    'FilesPerJob': 1,
    'EventsPerJob': 25000
}


files = nanoGetSampleFiles(mcDirectory, 'HZJ_HToWW_M125') + \
    nanoGetSampleFiles(mcDirectory, 'GluGluZH_HToWWTo2L2Nu_M125') + \
    nanoGetSampleFiles(mcDirectory, 'HWplusJ_HToWW_M125') + \
    nanoGetSampleFiles(mcDirectory, 'HWminusJ_HToWW_M125') + \
    nanoGetSampleFiles(mcDirectory, 'ttHToNonbb_M125')

samples['hww'] = {
    'name':   files,
    'weight': mcCommonWeight,
    'FilesPerJob': 1
}

############ H->TauTau ############
files = nanoGetSampleFiles(mcDirectory, 'GluGluHToTauTau_M125') + \
    nanoGetSampleFiles(mcDirectory, 'VBFHToTauTau_M125') + \
    nanoGetSampleFiles(mcDirectory, 'ZHToTauTau_M125') + \
    nanoGetSampleFiles(mcDirectory, 'WplusHToTauTau_M125') + \
    nanoGetSampleFiles(mcDirectory, 'WminusHToTauTau_M125')

samples['htt'] = {
    'name': files, 
    'weight': mcCommonWeight,
    'FilesPerJob': 1
}

##################                                                                                                                                                                                         
#     ggH LL     #                                                                                                                                                                                         
##################                                                                                                                                                                                         

samples['ggH_HWLWL'] = {
    'name': nanoGetSampleFiles(mcDirectory, 'GluGluHToWWTo2L2Nu_M125') + nanoGetSampleFiles(mcDirectory, 'GGHjjToWWTo2L2Nu_minloHJJ_M125'), 
    'weight': mcCommonWeight + '*Higgs_WW_LL*(Higgs_WW_LL>-5)',
    'FilesPerJob': 1,
    'EventsPerJob': 25000
}

addSampleWeight(samples, 'ggH_HWLWL', 'GluGluHToWWTo2L2Nu_M125', '(HTXS_stage1_1_cat_pTjet30GeV<107)*Weight2MINLO*1092.7640/1073.2567') #only non GE2J categories with the weight to NNLOPS and renormalize integral                                                         
addSampleWeight(samples, 'ggH_HWLWL', 'GGHjjToWWTo2L2Nu_minloHJJ_M125', '(HTXS_stage1_1_cat_pTjet30GeV>106)*1092.7640/1073.2567')                                                                          

signals.append('ggH_HWLWL')


##################                                                                                                                                                                                         
#     ggH TT     #                                                                                                                                                                                         
##################                                                                                                                                                                                         

samples['ggH_HWTWT'] = {
    'name': nanoGetSampleFiles(mcDirectory, 'GluGluHToWWTo2L2Nu_M125') + nanoGetSampleFiles(mcDirectory, 'GGHjjToWWTo2L2Nu_minloHJJ_M125'), 
    'weight': mcCommonWeight + '*Higgs_WW_TT*(Higgs_WW_TT>-5)',
    'FilesPerJob': 1,
    'EventsPerJob': 25000
}

addSampleWeight(samples, 'ggH_HWTWT', 'GluGluHToWWTo2L2Nu_M125', '(HTXS_stage1_1_cat_pTjet30GeV<107)*Weight2MINLO*1092.7640/1073.2567')
addSampleWeight(samples, 'ggH_HWTWT', 'GGHjjToWWTo2L2Nu_minloHJJ_M125', '(HTXS_stage1_1_cat_pTjet30GeV>106)*1092.7640/1073.2567')
signals.append('ggH_HWTWT')


##################
#     qqH LL     #
##################

samples['qqH_HWLWL'] = {
    'name': nanoGetSampleFiles(mcDirectory, 'VBFHToWWTo2L2Nu_M125'),
    'weight': mcCommonWeight + '*(Higgs_WW_LL*(Higgs_WW_LL>-5))',
    'FilesPerJob': 1,
    'EventsPerJob': 25000
}

signals.append('qqH_HWLWL')

##################
#     qqH TT     #
##################

samples['qqH_HWTWT'] = {
    'name': nanoGetSampleFiles(mcDirectory, 'VBFHToWWTo2L2Nu_M125'),
    'weight': mcCommonWeight + '*(Higgs_WW_TT*(Higgs_WW_TT>-5))',
    'FilesPerJob': 1,
    'EventsPerJob': 25000
}

signals.append('qqH_HWTWT')

'''
########### ggH+ggWW Interference ########
samples['ggH_gWW_Int'] = {
    'name': nanoGetSampleFiles(mcDirectory, 'GluGluHToWWTo2L2Nu_M125') + \
            nanoGetSampleFiles(mcDirectory, 'GGHjjToWWTo2L2Nu_minloHJJ_M125') + \
            nanoGetSampleFiles(mcDirectory, 'GluGluToWWToENEN') + \
            nanoGetSampleFiles(mcDirectory, 'GluGluToWWToENMN') + \
            nanoGetSampleFiles(mcDirectory, 'GluGluToWWToENTN') + \
            nanoGetSampleFiles(mcDirectory, 'GluGluToWWToMNEN') + \
            nanoGetSampleFiles(mcDirectory, 'GluGluToWWToMNMN') + \
            nanoGetSampleFiles(mcDirectory, 'GluGluToWWToMNTN') + \
            nanoGetSampleFiles(mcDirectory, 'GluGluToWWToTNEN') + \
            nanoGetSampleFiles(mcDirectory, 'GluGluToWWToTNMN') + \
            nanoGetSampleFiles(mcDirectory, 'GluGluToWWToTNTN'),
    'weight': mcCommonWeight + '*ggHWW_Interference',
    'FilesPerJob': 1,
    'EventsPerJob': 15000
}

addSampleWeight(samples, 'ggH_gWW_Int', 'GluGluHToWWTo2L2Nu_M125', '(HTXS_stage1_1_cat_pTjet30GeV<107)*Weight2MINLO*1092.7640/1073.2567')
addSampleWeight(samples, 'ggH_gWW_Int', 'GGHjjToWWTo2L2Nu_minloHJJ_M125', '(HTXS_stage1_1_cat_pTjet30GeV>106)*1092.7640/1073.2567')
addSampleWeight(samples, 'ggH_gWW_Int', 'GluGluToWWToENEN', 'KFactor_ggWW / 1.4')
addSampleWeight(samples, 'ggH_gWW_Int', 'GluGluToWWToENMN', 'KFactor_ggWW / 1.4')
addSampleWeight(samples, 'ggH_gWW_Int', 'GluGluToWWToENTN', 'KFactor_ggWW / 1.4')
addSampleWeight(samples, 'ggH_gWW_Int', 'GluGluToWWToMNEN', 'KFactor_ggWW / 1.4')
addSampleWeight(samples, 'ggH_gWW_Int', 'GluGluToWWToMNMN', 'KFactor_ggWW / 1.4')
addSampleWeight(samples, 'ggH_gWW_Int', 'GluGluToWWToMNTN', 'KFactor_ggWW / 1.4')
addSampleWeight(samples, 'ggH_gWW_Int', 'GluGluToWWToTNEN', 'KFactor_ggWW / 1.4')
addSampleWeight(samples, 'ggH_gWW_Int', 'GluGluToWWToTNMN', 'KFactor_ggWW / 1.4')
addSampleWeight(samples, 'ggH_gWW_Int', 'GluGluToWWToTNTN', 'KFactor_ggWW / 1.4')


############ VBF+qqWW Interference ###########
samples['qqH_qqWW_Int'] = {
    'name': nanoGetSampleFiles(mcDirectory, 'VBFHToWWTo2L2Nu_M125') + nanoGetSampleFiles(mcDirectory, 'WWTo2L2Nu') + nanoGetSampleFiles(mcDirectory, 'WpWmJJ_EWK_noTop'),
    'weight': mcCommonWeight + '*qqHWW_Interference',
    'FilesPerJob': 1,
    'EventsPerJob': 25000
}

addSampleWeight(samples, 'qqH_qqWW_Int', 'WpWmJJ_EWK_noTop', '(Sum(abs(GenPart_pdgId)==6 || GenPart_pdgId==25)==0)')
addSampleWeight(samples, 'qqH_qqWW_Int', 'WWTo2L2Nu', 'nllW*ewknloW')

'''
###### Dummy Total histograms for mkDatacards

samples['ggToWW'] = {
    'name': [],
    'weight': mcCommonWeight,
    'FilesPerJob': 1,
}

samples['qqToWW'] = {
    'name': [],
    'weight': mcCommonWeight,
    'FilesPerJob': 1,
}

samples['ggWW_si'] = {
    'name': [],
    'weight': mcCommonWeight,
    'FilesPerJob': 1,
}

samples['WWewk_si'] = {
    'name': [],
    'weight': mcCommonWeight,
    'FilesPerJob': 1,
}


###########################################
################## FAKE ###################
###########################################

samples['Fake'] = {
  'name': [],
  'weight': 'METFilter_DATA*fakeW',
  'weights': [],
  'isData': ['all'],
  'FilesPerJob': 1
}

for _, sd in DataRun:
  for pd in DataSets:
    tag = pd + '_' + sd

    files = nanoGetSampleFiles(fakeDirectory, tag)

    samples['Fake']['name'].extend(files)
    #samples['Fake']['weights'].extend([DataTrig[pd]] * len(files))
    addSampleWeight(samples, 'Fake', tag, DataTrig[pd])

###########################################
################## DATA ###################
###########################################

samples['DATA'] = {
  'name': [],
  'weight': 'LepWPCut*METFilter_DATA',
  'weights': [],
  'isData': ['all'],
  'FilesPerJob': 5
}

for _, sd in DataRun:
  for pd in DataSets:
    tag = pd + '_' + sd

    files = nanoGetSampleFiles(dataDirectory, tag)

    samples['DATA']['name'].extend(files)
    #samples['DATA']['weights'].extend([DataTrig[pd]] * len(files))
    addSampleWeight(samples, 'DATA', tag, DataTrig[pd])



