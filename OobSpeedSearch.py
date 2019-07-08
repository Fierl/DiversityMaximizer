import cv2
import json
import math
import numpy

from beamngpy import BeamNGpy, Scenario, Vehicle, setup_logging
from beamngpy.sensors import Camera, GForces, Electrics, Damage
from asfault.experiments import *
#from docutils.nodes import transition
import threading

from shapely.geometry import Point

pathToScenarioBeamng = 'c:/Users/SimonFierbeck/seminar/research/levels/asfault/scenarios'
pathToScenarioDocuments = 'c:/Users/SimonFierbeck/Documents/BeamNG.research/levels/asfault/scenarios'
#ev = EvolutionConfig('c:/Users/SimonFierbeck/.asfaultenv/cfg/evolution.json')


def goal_reached(test, state):
    pos = Point(state['pos'][0], state['pos'][1])
    distance = pos.distance(test.goal)
    return distance < c.ex.goal_distance


def get_path_projection(test, state):
    path = test.get_path_polyline()
    point = Point(state['pos'][0], state['pos'][1])
    if point.geom_type != 'Point':
        l.error('Point is: %s', point.geom_type)
        raise ValueError('Not a point!')
    proj = path.project(point, normalized=True)
    proj = path.interpolate(proj, normalized=True)
    return proj


def get_centre_distance(test, state):
    proj = get_path_projection(test, state)
    pos = Point(state['pos'][0], state['pos'][1])
    distance = math.fabs(pos.distance(proj))

    network = test.network
    nodes = network.get_nodes_at(pos)
    if nodes:
        distance -= (c.ev.lane_width + 0.2) / 2.0
    else:
        distance += (c.ev.lane_width + 0.2) / 2.0

    distance = math.fabs(distance)
    return distance


def off_track(test, state):
    distance = get_centre_distance(test, state)
    if distance > c.ev.lane_width / 2.0:
        return True

    return False


def get_segment(test, state):
    network = test.network
    pos = Point(state['pos'][0], state['pos'][1])
    nodes = network.get_nodes_at(pos)
    if nodes:
        return nodes.pop()
    else:
        return None


def getGoalSegment(test, point):
    network = test.network
    pos = point
    nodes = network.get_nodes_at(pos)
    if nodes:
        return nodes.pop()
    else:
        return None


def get_path_polyline(network, start, goal, path):
    directions = get_path_direction_list(network, start, goal, path)
    coords = []
    for idx in range(len(path)):
        buffer_coords(network, coords, path, directions, idx)

    polyline = LineString(coords)
    path_line = polyline

    # path_line = path_line.simplify(0.1, preserve_topology=True)
    path_line = path_line.simplify(0.1)
    return path_line


def get_path_polyline2(network, start, goal, path):
    path_line = get_path_polyline(network, start, goal, path)

    if start.geom_type != 'Point':
        raise ValueError('Not a point!')
    start_proj = path_line.project(start, normalized=True)
    start_proj = path_line.interpolate(start_proj, normalized=True)
    _, path_line = split(path_line, start_proj)

    if goal.geom_type != 'Point':
        raise ValueError('Not a point!')
    goal_proj = path_line.project(goal, normalized=True)
    goal_proj = path_line.interpolate(goal_proj, normalized=True)
    path_line, _ = split(path_line, goal_proj)

    l.info('Computed path polyline for test: %s')

    return path_line


def preprocess(img, brightness):

    # Elaborate Frame from BeamNG
    pil_image = img.convert('RGB')
    open_cv_image = numpy.array(pil_image)

    # Convert RGB to BGR. This is important
    open_cv_image = open_cv_image[:, :, ::-1].copy()

    # decrease_brightness and resize
    hsv = cv2.cvtColor(cv2.resize(open_cv_image, (280, 210)), cv2.COLOR_BGR2HSV)
    hsv[..., 2] = hsv[..., 2] * brightness
    preprocessed = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    # Check that we are passing to the network values between 0 and 1
    return preprocessed


def translate_steering(original_steering_value):
    # Using a quadratic function might be too much
    # newValue = -1.0 * (0.4 * pow(original_steering_value, 2) + 0.6 * original_steering_value + 0)
    # This seems to over shoot. Maybe it's just a matter of speed and not amount of steering
    newValue = -1.0 * original_steering_value;
    linear_factor = 0.6
    # Dump the controller to compensate oscillations in gentle curve
    if abs(original_steering_value) < 1:
        newValue = linear_factor * newValue

    # print("Steering", original_steering_value, " -> ", newValue)
    return newValue


def getOob(oobList, test, port):

    # Gains to port TORCS actuators to BeamNG
    # steering_gain = translate_steering()
    acc_gain = 0.5  # 0.4
    brake_gain = 1.0
    # BeamNG images are too bright for DeepDrive
    brightness = 0.4


    # Set up first vehicle
    # ! A vehicle with the name you specify here has to exist in the scenario
    vehicle = Vehicle('egovehicle')

    scenario = Scenario('asfault', 'asfault', True)

    # Set up sensors
    resolution = (280, 210)
    # Original Settings
    #pos = (-0.5, 1.8, 0.8)  # Left/Right, Front/Back, Above/Below
    # 0.4 is inside
    pos = (0, 2.0, 0.5)  # Left/Right, Front/Back, Above/Below
    direction = (0, 1, 0)
    # direction = (180, 0, 180)

    # FOV 60, MAX_SPEED 100, 20 (3) Hz fails
    # FOV 60, MAX_SPEED 80, 20 (3) Hz Ok
    # FOV 60, MAX_SPEED 80, 12 Hz Ok-ish Oscillations
    # FOV 60, MAX_SPEED 80, 10 Hz Ok-ish Oscillations
    # FOV 40, MAX_SPEED 50, 12 Hz Seems to be fine but drives slower
    # FOV 40, MAX_SPEED 80, 10 Hz Seems to be fine but drives slower
    fov = 60
    # MAX_SPEED = 70
    MAX_FPS = 60
    SIMULATION_STEP = 6
    # Running the controller at 20 hz makes experiments 3 to 4 times slower ! 5 minutes of simulations end up sucking 20 minutes !
    #

    # WORKING SETTINGS: 20 Freq, 90 FOV.
    front_camera = Camera(pos, direction, fov, resolution,
                          colour=True, depth=True, annotation=True)
    electrics = Electrics()

    vehicle.attach_sensor('front_cam', front_camera)
    vehicle.attach_sensor('electrics', electrics)

    with open(pathToScenarioBeamng + '/asfault.json', 'r') as f:
        jsonScenario = json.load(f)
    with open(pathToScenarioBeamng + '/asfault.lua', 'r') as f:
        luaScenario = f.readlines()
    with open(pathToScenarioBeamng + '/asfault.prefab', 'r') as f:
        prefabScenario = f.readlines()
    with open(pathToScenarioDocuments + '/asfault.json', 'w') as outfile:
        json.dump(jsonScenario, outfile)
    with open(pathToScenarioDocuments + '/asfault.lua', 'w') as outfile:
        outfile.writelines(luaScenario)
    with open(pathToScenarioDocuments + '/asfault.prefab', 'w') as outfile:
        outfile.writelines(prefabScenario)
    deep_drive_engaged = True
    STATE = "NORMAL"
    notFinished = True
    portCount = 1
    multiplier = 2
    turtleMode = False
    turtleSpeed = 10
    offRoad = False
    oobSegKey = None
    oobSearch = False

    print(oobList)
    speedList = []
    currentSpeed = oobList[0][0][0]
    for speed in oobList[0][0]:
        speedList.append(speed)
        if speed > currentSpeed:
            currentSpeed = speed

    currentSpeed = currentSpeed * 3.6
    waypointList = []
    resultList = []
    oobWaypoint = []
    newOobWaypointList = []
    for key in oobList[0][1]:
        waypointList.append(key)
    print(waypointList)
    for waypoint in waypointList:
        for key in waypointList:
            print(key)
            for k in key:
                oobWaypoint.append(k)
                resultList.append(k)

    while notFinished:
        # Connect to running beamng
        beamng = BeamNGpy('localhost', port, home='c:/Users/SimonFierbeck/seminar/research')
        bng = beamng.open(launch=True)
        scenario.make(bng)
        bng.load_scenario(scenario)
        try:
            bng.set_deterministic()  # Set simulator to be deterministic
            bng.set_steps_per_second(60)  # With 60hz temporal resolution
            # Connect to the existing vehicle (identified by the ID set in the vehicle instance)
            bng.connect_vehicle(vehicle, port + portCount)
            bng.start_scenario()
            # Put simulator in pause awaiting further inputs
            #bng.pause()

            assert vehicle.skt

            testDic = RoadTest.to_dict(test)
            parentage = testDic['network']['parentage']

            for parent in parentage:
                roadKeys = []
                for keys in parentage:
                    for key in keys:
                        roadKeys.append(key)

            nodesDict = testDic['network']['nodes']
            nodes = []
            for node in nodesDict:
                nodes.append(node)
            vehicle.update_vehicle()

            oobCount = 0
            inOob = False
            vehicle.ai_set_speed(100)
            if oobSearch:
                if turtleMode:
                    currentSpeed = turtleSpeed
                else:
                    currentSpeed = currentSpeed - 10
            print(currentSpeed)
            running = True
            while running:
                # Resume the execution
                # 6 steps correspond to 10 FPS with a resolution of 60FPS
                # 5 steps 12 FPS
                # 3 steps correspond to 20 FPS
                #bng.step(SIMULATION_STEP)

                # # TODO: Is there a way to query for the speed directly ?
                #speed = math.sqrt(vehicle.state['vel'][0] * vehicle.state['vel'][0] + vehicle.state['vel'][1] * vehicle.state['vel'][1])
                # Speed is M/S ?
                # print("Speed from BeamNG is: ", speed, speed*3.6)

                #vehicle.ai_drive_in_lane(True)
                vehicle.update_vehicle()
                tup = get_segment(test, vehicle.state)
                currentSegmentDict = None
                currentSegKey = None

                if tup is not None:
                    currentSegmentDict = NetworkNode.to_dict(tup)
                    currentSegKey = currentSegmentDict['key']

                if offRoad:
                    if oobSegKey in resultList:
                        index = resultList.index(oobSegKey)
                        lostSeg = resultList.pop(index)
                        print('resList without seg', resultList)
                        print(lostSeg)
                    if oobSegKey not in newOobWaypointList:
                        newOobWaypointList.append(oobSegKey)
                        print('new OOB list', newOobWaypointList)
                    offRoad = False

                if inOob and off_track(test, vehicle.state):
                    print('off track')
                    offRoad = True
                    oobCount = oobCount + 1

                if currentSegKey in oobWaypoint:
                    vehicle.ai_drive_in_lane(True)
                    inOob = True
                    oobSegKey = currentSegKey
                    vehicle.ai_set_speed(currentSpeed)
                else:
                    inOob = False
                    vehicle.ai_set_speed(100)

                vehicle.ai_set_waypoint('waypoint_goal')
                vehicle.ai_drive_in_lane(True)

                if goal_reached(test, vehicle.state):
                    print(turtleMode)
                    for res in resultList:
                        segOobDict = testDic['execution']['seg_oob_count']
                        segOobDict[res] = currentSpeed / 3.6
                    if oobCount == 0:
                        testDic['execution']['oobs'] = 0
                        print('waypointlist', newOobWaypointList)
                        print('resultlist', resultList)
                        test = RoadTest.from_dict(testDic)
                        return test
                    else:
                        running = False
                        portCount = portCount + 1
                        multiplier = multiplier + 1
                        oobSearch = True
                        oobWaypoint = newOobWaypointList
                        newOobWaypointList = []
                        if currentSpeed < 20:
                            print(currentSpeed)
                            print('NewoobWay: ', newOobWaypointList)
                            print('resultlist: ', resultList)
                            if turtleMode:
                                for res in oobWaypoint:
                                    print(res)
                                    segOobDict = testDic['execution']['seg_oob_count']
                                    segOobDict[res] = 12
                                testDic['execution']['oobs'] = 0
                                test = RoadTest.from_dict(testDic)
                                print(segOobDict)
                                print(resultList)
                                running = False
                                oobCount = 0
                                return test
                            else:
                                turtleMode = True
                                print('mode on')
                        bng.close()

        finally:
            if oobCount == 0:
                bng.close()
            else:
                print('restart')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--max-speed', type=int, default=70, help='Speed Limit in KM/H')
    args = parser.parse_args()
    print("Setting max speed to", args.max_speed)
    #getOob([])
