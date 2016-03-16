#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\trinity\crashdriver.py
import os
import sys

def crash(done = None):
    import blue
    import trinity
    import uthread2
    rj = trinity.CreateRenderJob('Crash')
    rj.steps.append(trinity.TriStepRunComputeShader())
    rj.steps[0].effect = trinity.Tr2Effect()
    rj.steps[0].effect.effectFilePath = 'res:/graphics/effect/managed/space/system/crash.fx'
    blue.resMan.Wait()
    rj.ScheduleOnce()
    while not (rj.status == trinity.RJ_DONE or rj.status == trinity.RJ_FAILED or rj.cancelled):
        uthread2.yield_()

    if done:
        done[0] = True


def _main():
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    import binbootstrapper
    binbootstrapper.update_binaries('.', *binbootstrapper.DLLS_GRAPHICS)
    from binbootstrapper.trinityapp import TrinityApp
    app = TrinityApp()
    import uthread2
    done = [False]
    uthread2.start_tasklet(crash, done)
    while not done[0]:
        app.run_frames(10)


if __name__ == '__main__':
    _main()
