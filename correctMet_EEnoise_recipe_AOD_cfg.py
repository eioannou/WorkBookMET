# This configuration uses a "modified" version of the EE noise recipe
# for AOD step.
#------------------------------------------------------------------------------
import FWCore.ParameterSet.Config as cms

import FWCore.ParameterSet.VarParsing as VarParsing
options = VarParsing.VarParsing('analysis')
#options.inputFiles = '/store/mc/RunIISpring18DRPremix/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/AODSIM/100X_upgrade2018_realistic_v10-v1/70000/FEDCEFC1-8224-E811-9B1B-A0369F8363BE.root'
#options.inputFiles = '/store/mc/RunIISummer18DRPremix/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/AODSIM/101X_upgrade2018_realistic_v7-v2/80000/F28F6278-3173-E811-821F-0CC47A7E6B00.root'
#options.inputFiles = 'file:CC7A350F-E29D-E811-B440-FA163EBC74D7.root'
options.inputFiles = '/store/mc/RunIIFall17DRPremix/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/AODSIM/PU2017_94X_mc2017_realistic_v11-v1/40000/B2029913-168A-E811-B0A2-44A842CFD619.root'
options.outputFile = 'corrMet_AOD.root'
options.maxEvents  = 100
options.parseArguments()
#____________________________________________________________________||
process = cms.Process("CORR")
#____________________________________________________________________||
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.load("Configuration.Geometry.GeometryIdeal_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")
#____________________________________________________________________||
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
from Configuration.AlCa.GlobalTag import GlobalTag
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
process.options = cms.untracked.PSet( wantSummary = cms.untracked.bool( True ))
process.MessageLogger.cerr.FwkReport.reportEvery = 1
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32( options.maxEvents ) )
#_____________________________________________________________________||
# PF MET 
#
# Removing Jets, their PF Candidates, and Unclustered PF Candidates which 
# have the EE noise problem.
#________________________________________________________________________||
process.load("PhysicsTools.PatAlgos.producersLayer1.patCandidates_cff")
process.load("PhysicsTools.PatAlgos.selectionLayer1.selectedPatCandidates_cff")
process.load("PhysicsTools.PatAlgos.cleaningLayer1.cleanPatCandidates_cff")

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
process.pfMetModified = pfMet.clone(
    src = cms.InputTag("pfCandidatesGoodEE2017")
    )

# Produce MET
from PhysicsTools.PatAlgos.producersLayer1.metProducer_cfi import patMETs
process.patPFMetModified = patMETs.clone(
    metSource = cms.InputTag('pfMetModified'),
    addMuonCorrections = cms.bool(False),
    genMETSource = cms.InputTag('genMetTrue')
)

process.corrPfMetType1Modified = cms.EDProducer(
    "PATPFJetMETcorrInputProducer",
    src = cms.InputTag("jetsNoEENoise"),
    jetCorrEtaMax = cms.double(9.9),
    jetCorrLabel = cms.InputTag("L3Absolute"),
    jetCorrLabelRes = cms.InputTag("L2L3Residual"),
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
    process.patCandidates +
    process.selectedPatCandidates +
    process.cleanPatCandidates +
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
    process.out
)
