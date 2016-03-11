#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\modules\nice\client\_nastyspace\animation.py
from carbon.common.lib.animation import *
from carbon.client.script.animation.animationBehavior import AnimationBehavior as animationBehavior
from carbon.client.script.animation.animationClient import AnimationComponent
from carbon.client.script.animation.animationController import AnimationController
from carbon.client.script.animation.headTrackAnimationBehavior import HeadTrackAnimationBehavior as headTrackAnimationBehavior
from eve.client.script.incarna.animation.behaviours.walkTypeBehaviour import WalkTypeBehaviour as walkTypeBehaviour
from eve.client.script.incarna.animation.bipedAnimationController import BipedAnimationController
from eve.client.script.incarna.animation.playerAnimationController import ACCELERATED_TURN_MULTIPLIER
from eve.client.script.incarna.animation.playerAnimationController import MINIMUM_MOVE_SPEED
from eve.client.script.incarna.animation.playerAnimationController import MIN_ACCELERATED_TURN_ANGLE
from eve.client.script.incarna.animation.playerAnimationController import ONE_EIGHTY_ANIM_TURN_ANGLE
from eve.client.script.incarna.animation.playerAnimationController import PlayerAnimationController
