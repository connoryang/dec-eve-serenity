#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\eveclientqatools\probeperformancebenchmark.py
import argparse
import os
import math
import subprocess
import tempfile
import shutil
import devenv
import yamlext
import performancebenchmarkdata as data

def _enumerate_ships(start_pos, test_case):
    yCount = 0
    xPos = start_pos[0]
    index = 0
    for cntr in xrange(test_case.number_of_rows ** 2):
        typeId = test_case.ship_list[cntr % len(test_case.ship_list)]
        if yCount >= test_case.number_of_rows:
            xPos += test_case.distance_between_ships
            yCount = 0
        for zCount in xrange(test_case.number_of_rows):
            yield (index,
             typeId,
             xPos,
             yCount * test_case.distance_between_ships + start_pos[1],
             zCount * test_case.distance_between_ships + start_pos[2])
            index += 1

        yCount += 1


def create_sequence(benchmark, camera, output_path, time = 12, telemetry = True):
    static_data = os.path.join(devenv.EVEROOT, 'staticData')
    type_ids = yamlext.loadfile(os.path.join(static_data, 'typeIDs', 'types.staticdata'))
    graphic_ids = yamlext.loadfile(os.path.join(static_data, 'graphicIDs', 'graphicIDs.staticdata'))
    test_case = data.TEST_CASES[benchmark]
    yaw = data.CAMERA_PRESETS[camera][1] / 180.0 * math.pi
    pitch = data.CAMERA_PRESETS[camera][0] / 180.0 * math.pi
    distance = data.CAMERA_PRESETS[camera][2]
    x = distance * math.cos(yaw) * math.cos(pitch)
    y = -distance * math.sin(pitch)
    z = distance * math.sin(yaw) * math.cos(pitch)
    with open(output_path, 'w') as out_file:
        out_file.write('name: Death Cube\ndescription: |\n  Performance Benchmark\ncommands:\n  - [scene, m10]\n  - [set_camera_position, [%s, %s, %s]]\n  - [set_camera_focus, [0.0, 0.0, 0.0]]\n  - [set_camera_fov, 1.0]\n' % (x, y, z))
        start_pos = (0, 0, 0)
        for index, type_id, x, y, z in _enumerate_ships(start_pos, test_case):
            g = graphic_ids[type_ids[type_id]['graphicID']]
            sof = '%s:%s:%s' % (g['sofHullName'], g['sofFactionName'], g['sofRaceName'])
            out_file.write("  - [actor, ship%s, '%s']\n" % (index, sof))

        for index, type_id, x, y, z in _enumerate_ships(start_pos, test_case):
            out_file.write('  - [set_position, ship%s, [%s, %s, %s]]\n' % (index,
             x,
             y,
             z))
            out_file.write('  - [add_actor, ship%s]\n' % index)

        out_file.write('  - [preload_lods]\n  - [wait_for_loads]\n')
        if telemetry:
            out_file.write('  - [sleep, %s]\n  - [telemetry, start, localhost]\n  - [sleep, %s]\n  - [telemetry, stop]\n' % (max(time - 8, 0), min(time, 8)))
        else:
            out_file.write('  - [sleep, %s]\n' % time)


def run_benchmark(benchmark, camera, time = 12, telemetry = True, additional_args = None):
    additional_args = additional_args or []
    temp_dir = tempfile.mkdtemp()
    try:
        sequence = os.path.join(temp_dir, 'benchmark.yaml')
        create_sequence(benchmark, camera, sequence, time, telemetry)
        args = [os.path.join(devenv.BRANCHROOT, 'evemark', 'launch.bat'), '/scenes=%s' % sequence] + additional_args
        subprocess.check_call(args, shell=True)
    finally:
        shutil.rmtree(temp_dir)


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cube', choices=[ x.split('_')[-1] for x in dir(data) if x.startswith('CUBE_') ], default='CLASSIC', help='performance benchmark name (default is CLASSIC)')
    parser.add_argument('--camera', choices=[ x.split('_')[-1] for x in dir(data) if x.startswith('CAMERA_PRESET_') ], default='NEAR', help='camera preset (default is NEAR)')
    parser.add_argument('--time', type=int, default=12, help='time to show the benchmark')
    parser.add_argument('--notelemetry', action='store_false', help="don't capture telemetry snapshot")
    args, probe_args = parser.parse_known_args()
    cube = getattr(data, 'CUBE_' + args.cube)
    camera = getattr(data, 'CAMERA_PRESET_' + args.camera)
    run_benchmark(cube, camera, args.time, args.notelemetry, probe_args)


if __name__ == '__main__':
    _main()
