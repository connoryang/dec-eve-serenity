#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\projectdiscovery\client\const.py
import os
RESROOT = os.path.dirname(__file__) + '\\res\\'

class Texts:
    SelectionsLabel = 'Selections'
    TaskImageLabel = 'Jovian Tissue Sample'
    RankLabel = 'Rank: '
    ScoreLabel = ' Discovery Credits'
    SubmitButtonLabel = 'Submit'
    PreviousGroupButtonLabel = 'Previous Group'
    NextGroupButtonLabel = 'Next Group'


class Events:
    PlayTutorial = 'OnCitizenSciencePlayTutorial'
    NewTask = 'OnCitizenScienceNewTask'
    NewTrainingTask = 'OnCitizenScienceNewTrainingTask'
    CategoryChanged = 'OnCitizenScienceCategoryChanged'
    ExcludeCategories = 'OnCitizenScienceExcludeCategories'
    SubmitSolution = 'OnCitizenScienceSubmitSolution'
    ResultReceived = 'OnCitizenScienceResultReceived'
    TrainingResultReceived = 'OnCitizenScienceTrainingResultReceived'
    ContinueFromResult = 'OnCitizenScienceContinueFromResult'
    ContinueFromTrainingResult = 'OnCitizenScienceContinueFromTrainingResult'
    UpdateScoreBar = 'OnCitizenScienceUpdateScoreBar'
    ProjectDiscoveryStarted = 'OnProjectDiscoveryStarted'
    ContinueFromReward = 'OnProjectDiscoveryContinueFromReward'
    StartTutorial = 'OnProjectDiscoveryStartTutorial'
    QuitTutorial = 'OnProjectDiscoveryQuitTutorial'
    CloseResult = 'OnProjectDiscoveryResultClosed'
    HoverMainImage = 'OnHoverMainImage'
    ClickMainImage = 'OnClickMainImage'
    ProcessingViewFinished = 'OnProcessingViewFinished'
    MouseExitMainImage = 'OnMouseExitMainImage'
    MouseEnterMainImage = 'OnMouseEnterMainImage'
    TransmissionFinished = 'OnTransmissionFinished'
    RewardViewFadeOut = 'OnRewardViewFadeOut'
    MainImageLoaded = 'OnMainImageLoaded'
    EnableUI = 'OnUIEnabled'


class Settings:
    ProjectDiscoveryTutorialPlayed = 'ProjectDiscoveryTutorialPlayed'
    ProjectDiscoveryIntroductionShown = 'ProjectDiscoveryIntroductionShown'


class Sounds:
    CategorySelectPlay = 'wise:/project_discovery_category_select_play'
    MainImageLoadPlay = 'wise:/project_discovery_main_image_calculation_loop_play'
    MainImageLoadStop = 'wise:/project_discovery_main_image_calculation_loop_stop'
    MainImageLoopPlay = 'wise:/project_discovery_main_image_loop_play'
    MainImageLoopStop = 'wise:/project_discovery_main_image_loop_stop'
    MainImageOpenPlay = 'wise:/project_discovery_main_image_open_play'
    ColorSelectPlay = 'wise:/project_discovery_color_select_play'
    ProcessingPlay = 'wise:/project_discovery_analysis_calculation_loop_play'
    ProcessingStop = 'wise:/project_discovery_analysis_calculation_loop_stop'
    RewardsWindowOpenPlay = 'wise:/project_discovery_analysis_window_open_play'
    RewardsWindowClosePlay = 'wise:/project_discovery_analysis_window_close_play'
    RewardsWindowLoopPlay = 'wise:/project_discovery_analysis_window_loop_play'
    RewardsWindowLoopStop = 'wise:/project_discovery_analysis_window_loop_stop'
    AnalysisDonePlay = 'wise:/project_discovery_analysis_done_play'
    AnalysisWindowMovePlay = 'wise:/project_discovery_analysis_window_move_play'


TrainingTasks = {'starter': {160000016: [102],
             160000017: [211],
             160000005: [303]},
 'levelOne': {160000009: [233],
              160000001: [203],
              160000011: [221]},
 'levelTwo': {160000014: [123],
              160000003: [112],
              160000007: [113]},
 'levelThree': {160000010: [102, 233],
                160000006: [121, 203],
                160000000: [102, 201]},
 'levelFour': {160000012: [303, 201]},
 'levelFive': {160000008: [102, 303, 302],
               160000015: [102, 215]},
 'negative': {160000002: [901],
              160000004: [101],
              160000013: [201]},
 'unspecific': {}}
