#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\login\charcreation\bloodlineDollLoader.py
import paperDoll as PD
import eve.client.script.ui.login.charcreation.bloodlineSelector as BS
import GameWorld

class BloodlineDollLoader(object):

    def GetClothedDoll(self, raceID, bloodlineID, genderID, scene):
        for bloodline in BS.RACE_PATHS_MAPPING[raceID]:
            resources, blood, poseID = bloodline
            if blood != bloodlineID:
                continue
            else:
                break

        factory = sm.GetService('character').factory
        if genderID == 0:
            doll = PD.PaperDollCharacter.ImportCharacter(factory, scene, resources[0])
        else:
            doll = PD.PaperDollCharacter.ImportCharacter(factory, scene, resources[1])
        self.SetAnimationNetwork(doll.avatar, genderID, poseID)
        return doll

    def SetAnimationNetwork(self, avatar, genderID, poseID):
        MORPHEME_NETWORK = 'res:/Animation/MorphemeIncarna/Export/CharCreation_runtimeBinary/CharacterCreation.mor'
        animation = GameWorld.GWAnimation(MORPHEME_NETWORK)
        if animation.network is not None:
            animation.network.SetAnimationSetIndex(genderID)
            animation.network.SetControlParameter('ControlParameters|NetworkMode', 0)
            animation.network.SetControlParameter('ControlParameters|BloodlinePoseNumber', poseID)
            animation.network.SetControlParameter('ControlParameters|Selected', 1.0)
            avatar.animationUpdater = animation
