# This configuration uses a "modified" version of the EE noise recipe
# for AOD step.
#------------------------------------------------------------------------------
import FWCore.ParameterSet.Config as cms

import PhysicsTools.PatAlgos.tools.helpers as configtools
from PhysicsTools.PatAlgos.tools.helpers import addToProcessAndTask


import FWCore.ParameterSet.VarParsing as VarParsing
options = VarParsing.VarParsing('analysis')

options.inputFiles = '/store/mc/RunIIFall17DRPremix/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/AODSIM/PU2017_94X_mc2017_realistic_v11-v1/40000/B2029913-168A-E811-B0A2-44A842CFD619.root'
#options.inputFiles = '/store/data/Run2017D/SingleMuon/AOD/17Nov2017-v1/70001/680A8B6C-95E4-E711-BA08-00266CFB8A5C.root'

options.outputFile = 'corrMet_AOD_MC.root'
options.maxEvents  = 100
options.parseArguments()
#____________________________________________________________________||
process = cms.Process("CORR")

patAlgosToolsTask = configtools.getPatAlgosToolsTask(process)
#____________________________________________________________________||

isData = False # False for MC samples / True for data samples

#____________________________________________________________________||
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.load("Configuration.Geometry.GeometryRecoDB_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")
#____________________________________________________________________||
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
from Configuration.AlCa.GlobalTag import GlobalTag
if isData:
    process.GlobalTag = GlobalTag(process.GlobalTag, '94X_dataRun2_ReReco_EOY17_v2', '')
else:
    process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:startup', '')
#____________________________________________________________________||
process.source = cms.Source(
    "PoolSource",
    fileNames = cms.untracked.vstring( options.inputFiles )
    )
#____________________________________________________________________||
process.out = cms.OutputModule(
    "PoolOutputModule",
    fileName = cms.untracked.string( options.outputFile ),
    SelectEvents = cms.untracked.PSet( SelectEvents = cms.vstring('p') ),
    outputCommands = cms.untracked.vstring(
        'drop *',
        'keep recoGenMETs_*_*_*',
        'keep recoCaloMETs_*_*_*',
        'keep recoPFMETs_*_*_*',
        'keep *_*_*_CORR'
        )
    )
#_____________________________________________________________________||
process.options = cms.untracked.PSet( wantSummary = cms.untracked.bool( False ))
process.MessageLogger.cerr.FwkReport.reportEvery = 1
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32( options.maxEvents ) )
#_____________________________________________________________________||
# PF MET 
#
# Removing Jets, their PF Candidates, and Unclustered PF Candidates which 
# have the EE noise problem.
#________________________________________________________________________||
#process.load("PhysicsTools.PatAlgos.producersLayer1.patCandidates_cff")
#patAlgosToolsTask.add(process.patCandidatesTask)
#process.load("PhysicsTools.PatAlgos.selectionLayer1.selectedPatCandidates_cff")
#patAlgosToolsTask.add(process.selectedPatCandidatesTask)
#process.load("PhysicsTools.PatAlgos.cleaningLayer1.cleanPatCandidates_cff")
#____________________________________________________________________________
# Electrons :
#____________
process.load("PhysicsTools.PatAlgos.producersLayer1.electronProducer_cff")
patAlgosToolsTask.add(process.makePatElectronsTask)

process.load("PhysicsTools.PatAlgos.selectionLayer1.electronSelector_cfi")
patAlgosToolsTask.add(process.selectedPatElectrons)

process.load("PhysicsTools.PatAlgos.cleaningLayer1.electronCleaner_cfi")
patAlgosToolsTask.add(process.cleanPatElectrons)
#__________________________________________________________________________||

# Muons :
#________
process.load("PhysicsTools.PatAlgos.producersLayer1.muonProducer_cff")
patAlgosToolsTask.add(process.makePatMuonsTask)

process.load("PhysicsTools.PatAlgos.selectionLayer1.muonSelector_cfi")
patAlgosToolsTask.add(process.selectedPatMuons)

process.load("PhysicsTools.PatAlgos.cleaningLayer1.muonCleaner_cfi")
patAlgosToolsTask.add(process.cleanPatMuons)
#__________________________________________________________________________||

# Taus :
#_______
process.load("PhysicsTools.PatAlgos.producersLayer1.tauProducer_cff")
patAlgosToolsTask.add(process.makePatTausTask)
process.patTaus.skipMissingTauID = True

process.load("PhysicsTools.PatAlgos.selectionLayer1.tauSelector_cfi")
patAlgosToolsTask.add(process.selectedPatTaus)

# temporary fix until we find a more sustainable solution
from RecoParticleFlow.PFProducer.pfLinker_cff import particleFlowPtrs
process.particleFlowPtrs = particleFlowPtrs
patAlgosToolsTask.add(process.particleFlowPtrs)

process.load("PhysicsTools.PatAlgos.cleaningLayer1.tauCleaner_cfi")
patAlgosToolsTask.add(process.cleanPatTaus)
#__________________________________________________________________________||

# Photons :
#__________
process.load("PhysicsTools.PatAlgos.producersLayer1.photonProducer_cff")
patAlgosToolsTask.add(process.makePatPhotonsTask)

process.load("PhysicsTools.PatAlgos.selectionLayer1.photonSelector_cfi")
patAlgosToolsTask.add(process.selectedPatPhotons)

process.load("PhysicsTools.PatAlgos.cleaningLayer1.photonCleaner_cfi")
patAlgosToolsTask.add(process.cleanPatPhotons)
#__________________________________________________________________________||

# Jets :
#_______
if not isData:
    process.load("PhysicsTools.PatAlgos.producersLayer1.jetProducer_cff")
    patAlgosToolsTask.add(process.makePatJetsTask)
else:
    from PhysicsTools.PatAlgos.recoLayer0.bTagging_cff import *
    process.load("PhysicsTools.PatAlgos.recoLayer0.jetTracksCharge_cff")
    patAlgosToolsTask.add(process.patJetCharge)
    process.load("PhysicsTools.PatAlgos.recoLayer0.jetCorrections_cff")
    patAlgosToolsTask.add(process.patJetCorrectionsTask)
    process.load("PhysicsTools.PatAlgos.producersLayer1.jetProducer_cfi")
    patAlgosToolsTask.add(process.patJets)

    makePatJetsTask = cms.Task(
        process.patJetCorrectionsTask,
        process.patJetCharge,
        process.patJets
        )

    from RecoBTag.ImpactParameter.pfImpactParameterTagInfos_cfi import * #pfImpactParameterTagInfos
    from RecoBTag.SecondaryVertex.pfSecondaryVertexTagInfos_cfi import * #pfSecondaryVertexTagInfos
    from RecoBTag.SecondaryVertex.pfInclusiveSecondaryVertexFinderTagInfos_cfi import * #pfInclusiveSecondaryVertexFinderTagInfos
    from RecoBTag.Combined.deepFlavour_cff import * #pfDeepCSVTask
    
    # make a copy to avoid labels and substitution problems
    _makePatJetsWithDeepFlavorTask = makePatJetsTask.copy()
    _makePatJetsWithDeepFlavorTask.add(
        pfImpactParameterTagInfos, 
        pfSecondaryVertexTagInfos,
        pfInclusiveSecondaryVertexFinderTagInfos,
        pfDeepCSVTask
        )
    
    from Configuration.Eras.Modifier_run2_miniAOD_80XLegacy_cff import run2_miniAOD_80XLegacy
    run2_miniAOD_80XLegacy.toReplaceWith(
        makePatJetsTask, _makePatJetsWithDeepFlavorTask
        )


process.load("PhysicsTools.PatAlgos.selectionLayer1.jetSelector_cfi")
patAlgosToolsTask.add(process.selectedPatJets)
#__________________________________________________________________________||

from PhysicsTools.PatAlgos.cleaningLayer1.jetCleaner_cfi import cleanPatJets

process.jetsNoEENoise = cleanPatJets.clone(
    src = cms.InputTag("patJets"),
    finalCut = cms.string('pt > 50 || abs(eta) < 2.65 || abs(eta) > 3.139'),
   )

process.jetsEENoise = cleanPatJets.clone(
    src = cms.InputTag("patJets"),
    finalCut = cms.string('pt < 50 && abs(eta) > 2.65 && abs(eta) < 3.139')
)

process.pfcandidateClustered = cms.EDProducer(
    "CandViewMerger",
    src = cms.VInputTag(
        cms.InputTag("selectedPatMuons"),
        cms.InputTag("selectedPatElectrons"),
        cms.InputTag("selectedPatPhotons"),
        cms.InputTag("selectedPatTaus"),
        cms.InputTag("patJets")
        )
    )
process.pfcandidateForUnclusteredUnc = cms.EDProducer(
    "CandPtrProjector",
    src = cms.InputTag("particleFlow"),
    veto = cms.InputTag("pfcandidateClustered")
    )
process.badUnclustered = cms.EDFilter(
    "CandPtrSelector",
    src = cms.InputTag("pfcandidateForUnclusteredUnc"),
    cut = cms.string("abs(eta) > 2.65 && abs(eta) < 3.139")
    )
process.blobUnclustered = cms.EDProducer(
    "UnclusteredBlobProducer",
    candsrc = cms.InputTag("badUnclustered")
    )
process.superbad = cms.EDProducer(
    "CandViewMerger",
    src = cms.VInputTag(
        cms.InputTag("blobUnclustered"),
        cms.InputTag("jetsEENoise")
        )
    )
process.pfCandidatesGoodEE2017 = cms.EDProducer(
    "CandPtrProjector",
    src = cms.InputTag("particleFlow"),
    veto = cms.InputTag("superbad")
    )
#____________________________________________________________________________||
# New PF MET which DOES NOT include faulty jets
#____________________________________________________________________________||

# raw MET
from RecoMET.METProducers.PFMET_cfi import pfMet
addToProcessAndTask("pfMet", pfMet.clone(), process, patAlgosToolsTask)
process.pfMetModified = pfMet.clone(
    src = cms.InputTag("pfCandidatesGoodEE2017")
    )

# Produce MET
process.load("PhysicsTools.PatAlgos.producersLayer1.metProducer_cff")
patAlgosToolsTask.add(process.makePatMETsTask)
if isData:
    process.patMETs.addGenMET = False


process.patPFMetModified = getattr(process, "patMETs").clone(
    metSource = cms.InputTag('pfMetModified'),
    addMuonCorrections = cms.bool(False)   
)

if isData:
    jecLevel = cms.InputTag("L2Relative")
else:
    jecLevel = cms.InputTag("L2L3Residual")
process.corrPfMetType1Modified = cms.EDProducer(
    "PATPFJetMETcorrInputProducer",
    src = cms.InputTag("jetsNoEENoise"),
    jetCorrEtaMax = cms.double(9.9),
    jetCorrLabel = cms.InputTag("L3Absolute"),
    jetCorrLabelRes = jecLevel,
    offsetCorrLabel = cms.InputTag("L1FastJet"),
    skipEM = cms.bool(True),
    skipEMfractionThreshold = cms.double(0.9),
    skipMuonSelection = cms.string('isGlobalMuon | isStandAloneMuon'),
    skipMuons = cms.bool(True),
    type1JetPtThreshold = cms.double(15.0)
    )

process.pfMetT1Modified = cms.EDProducer(
    "CorrectedPATMETProducer",
    src = cms.InputTag('patPFMetModified'),
    srcCorrections = cms.VInputTag(
        cms.InputTag('corrPfMetType1Modified', 'type1'),
        ),
    )


process.p = cms.Path(
    process.jetsNoEENoise +
    process.jetsEENoise +
    process.pfcandidateClustered +
    process.pfcandidateForUnclusteredUnc +
    process.badUnclustered +
    process.blobUnclustered +
    process.superbad +
    process.pfCandidatesGoodEE2017 +
    process.pfMetModified +
    process.patPFMetModified +
    process.corrPfMetType1Modified +
    process.pfMetT1Modified
)


process.e1 = cms.EndPath(
    process.out, patAlgosToolsTask
)
if isData:
    # OOTPhoton modules are loaded in data but are not used in MC. 
    # They are only used in runOnData function. Without OOTPhotons runOnData 
    # does not operate. There are other ways to run on Data
    # but this is the most generic case, whether one does not need OOTPhotons
    # at all.
    process.load("PhysicsTools.PatAlgos.producersLayer1.ootPhotonProducer_cff")
    patAlgosToolsTask.add(process.makePatOOTPhotonsTask)
    from PhysicsTools.PatAlgos.tools.coreTools import runOnData
    runOnData( process )
